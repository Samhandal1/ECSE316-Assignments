import argparse
import sys
import time
import socket
import random

BUFFER = 1024

def parse_packet(server_name, query_type):

    packet = ""

    ### PACKET HEADER ###

    # ID (16-bit identifier assigned by the client)
    id = random.randint(0, 0xFFFF)
    hex_id = format(id, '04x')
    packet += hex_id

    # FLAGS (don't vary for query)
    packet += "0100"

    # QDCOUNT (one question, will always be 1)
    packet += "0001"

    # ANCOUNT (No records in the Answer section)
    packet += "0000"

    # NSCOUNT (No records in the Authoritative section)
    packet += "0000"

    # ARCOUNT (No records in the Additional section)
    packet += "0000"

    ### PACKET QUESTION ###
    qlen = 0

    # QNAME
    # domain names are represented as lists of labels
    qname = ""
    server_name_array = server_name.split('.')

    for label in server_name_array:

        # each label is preceded by a single byte giving the number of ASCII characters used in the label
        num_ascii_char = len(label)
        qname += format(num_ascii_char, '02x')
        qlen += 2

        # each character is coded using 8-bit ASCII
        for letter in label:
            qname += format(ord(letter), '02x')
            qlen += 2

    # To signal the end of a domain name, one last byte is written with value 0
    qname += "00"
    qlen += 2
    packet += qname

    # QTYPE (16-bit code specifying the type of query)
    if (query_type == "NS"):
        # 0x0002 for a type-NS query (name server)
        qtype = "0002"
    elif (query_type == "MX"):
        # 0x000f for a type-MX query (mail server)
        qtype = "000f"
    else:
        # 0x0001 for a type-A query (host address)
        qtype = "0001"
    
    packet += qtype
    qlen += 4

    # QCLASS (always use 0x0001 in this field, representing an Internet address)
    packet += "0001"
    qlen += 4

    # convert to a bytes object
    byte_sequence = bytes.fromhex(packet)
    return byte_sequence, hex_id, qlen

def send_dns_query(server, name, query_type, timeout, max_retries, port):

    # print summarized query
    print("DnsClient sending request for " + name)
    print("Server: " + server)
    print("Request type: " + query_type)

    # create client socket, set params
    # A pair (host, port) is used for the AF_INET address family, where host is a string representing either a hostname in internet domain notation like 'daring.cwi.nl' or an IPv4 address like '100.50.200.5', and port is an integer.
    # UDP (SOCK_DGRAM) is a datagram-based protocol. You send one datagram and get one reply and then the connection terminates.
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.settimeout(timeout)
    timer = time.perf_counter()

    for i in range(max_retries + 1):
        try:
            # send
            packet, id, qlen = parse_packet(name, query_type)
            clientSocket.sendto(packet, (server, port))

            # receive
            response, response_address = clientSocket.recvfrom(BUFFER)
            curr_time = time.perf_counter() - timer

            # maybe only when we parse
            print("Response received after " + str(curr_time) + " seconds (" + str(i) + " retries)")
            clientSocket.close()
            return response, id, qlen

        except socket.timeout:
            if (i < max_retries):
                print("ERROR    Socket timeout, unanswered query")
            else:
                print("ERROR    Maximum number of retries " + str(max_retries) + " exceeded")
                clientSocket.close()
                sys.exit(1)

# do we retry or terminate???
def parse_dns_response(result, id, qlen):

    # convert a bytes object to a string representing its hexadecimal representation
    hex_string = result.hex()

    ### HEADER ###

    # ID
    # query header id must match response header id
    result_id = hex_string[:4]
    if result_id != id:
        print("ERROR    Unexpected response: query id and response id do not match.")

    ### FLAGS ###
    # Convert flag segment to binary
    flag = hex_string[4:8]                  # extract flag bytes
    binary_flag = bin(int(flag, 16))[2:]    # Convert integer to binary string and remove "0b" prefix

    # QR
    # check if QR bit is 1 (response)
    qr = binary_flag[0]
    if qr != 1:
        print("ERROR    Unexpected response: expected response, but got type query.")

    # OPCODE
    opcode = binary_flag[1:5]

    # AA
    # report whether or not the response you receive is authoritative
    aa = binary_flag[5]
    if aa == 1:
        isAuthoritative = True
    else:
        isAuthoritative = False

    # TC
    # indicates whether or not this message was truncated
    tc = binary_flag[6]
    if tc == 1:
        isTruncated = True
    else:
        isTruncated = False

    # RD
    # bit set in the request message
    rd = binary_flag[7]

    # RA
    # bit set or cleared by the server in a response message to indicate whether or not recursive queries are supported
    ra = binary_flag[8]
    if ra != 1:
        print("ERROR    Unexpected response: server does not support recursive queries.")

    # Z
    # 3-bit field reserved for future use
    z = binary_flag[9:12]

    # RCODE
    # 4-bit field, only meaningful in response messages, containing the response code
    rcode = binary_flag[12:16]
    if rcode != "0000":
        if rcode == "0001":
            print("ERROR    Format error: the name server was unable to interpret the query.")
        elif rcode == "0010":
            print("ERROR    Server failure: the name server was unable to process this query due to a problem with the name server.")
        elif rcode == "0011":
            print("NOTFOUND     Name error: the domain name referenced in the query does not exist.")
        elif rcode == "0100":
            print("ERROR    Not implemented: the name server does not support the requested kind of query.")
        elif rcode == "0101":
            print("ERROR    Refused: the name server refuses to perform the requested operation for policy reasons.")
        else:
            print("ERROR    Unexpected response: unknown rcode error.")

    # QDCOUNT
    # number of entries in the question section
    qdcount = hex_string[8:12]

    # ANCOUNT
    # number of resource records in the answer section
    ancount = hex_string[12:16]
    num_answers = 0
    if ancount != "0000":
        num_answers = int(ancount, 16)
        print("*** Answer Section (" + str(num_answers) + " records) ***")
    else:
        print("NOTFOUND")

    # NSCOUNT
    # number of name server resource records in the Authority section - IGNORE
    nscount = hex_string[16:20]

    # ARCOUNT
    # number of resource records in the Additional records section
    arcount = hex_string[20:24]
    num_additional = 0
    if arcount != "0000":
        num_additional = int(arcount, 16)
        print("*** Additional Section (" + str(num_additional) + " records) ***")
    else:
        print("NOTFOUND")


    ### QUESTION ###
    # should be identical to query...
    question_string = hex_string[24:qlen]

    # # QNAME
    # question_string = hex_string[24:]
    # dom_name_index = [24, (question_string.find("00") + 24)]
    # dom_name = hex_string[24:(dom_name_index[1] + 1)]

    # # QTYPE
    # qtype_index = [(dom_name_index[1] + 1), (dom_name_index[1] + 4)]

    # # QCLASS
    # qclass_index = [(qtype_index[1] + 1), (qtype_index[1] + 4)]
    # question_string = hex_string[24:(qclass_index[1] + 1)]

    ### ANSWER ###
    answer_string = hex_string[qlen:]
    domname_type, name = packetCompression(answer_string)

def packetCompression(hexdump):

    domname_type = ""

    # CASE 1 - POINTER
    hex_to_int = int(hexdump, 16)               # convert to binary to check first two bits
    binary_string = bin(hex_to_int)[2:]         # Convert integer to binary string and remove "0b" prefix

    if binary_string[:2] == "11":

        # first two bits to 1 allows pointers to be distinguished from labels
        domname_type = "pointer"

        # convert back to hex
        bin_to_int = int(binary_string[:16], 2)
        hex_pointer = hex(bin_to_int)[2:]

        return domname_type, hex_pointer
    
    indx = 0
    while indx < len(hexdump):

        # jump to next label
        ascii_to_check = hexdump[indx:(indx + 2)]
        count_to_next_label = int(ascii_to_check, 16)
        indx_to_check = (indx + 2) + (count_to_next_label * 2)

        # CASE 2 - a sequence of labels ending with a zero octet
        ascii_to_check = hexdump[indx_to_check:(indx_to_check + 2)]
        if ascii_to_check == "00":

            domname_type = "label-00"
            return domname_type, hexdump[:(indx_to_check + 2)]
        
        # CASE 3 - a sequence of labels ending with a pointer
        hex_to_int = int(ascii_to_check, 16)                # convert to binary to check first two bits
        binary_string = bin(hex_to_int)[2:]                 # Convert integer to binary string and remove "0b" prefix
        if binary_string[:2] == "11":

            domname_type = "label-p"
            return domname_type, hexdump[:(indx_to_check + 2)]

        # increment and continue
        indx = indx_to_check


def main():

    # parse arguments
    parser = argparse.ArgumentParser(description="DnsClient")

    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout for retransmitting an unanswered query.")
    parser.add_argument("-r", "--max-retries", type=int, default=3, help="Maximum number of retries for unanswered query.")
    parser.add_argument("-p", "--port", type=int, default=53, help="UDP port number of the DNS server.")
    parser.add_argument("-mx", "--mail-server", action="store_true", help="Send an MX (mail server) query.")
    parser.add_argument("-ns", "--name-server", action="store_true", help="Send an NS (name server) query.")
    parser.add_argument("server", help="IPv4 address of the DNS server.")
    parser.add_argument("name", help="Domain name to query for.")

    args = parser.parse_args()

    # throw error if both flags given
    if args.mail_server and args.name_server:
        print("ERROR\tBoth -mx and -ns cannot be given simultaneously.")
        sys.exit(1)

    query_type = "A"
    if args.mail_server:
        query_type = "MX"
    elif args.name_server:
        query_type = "NS"

    # ADD!!!!!
    # ERROR <tab> Incorrect input syntax: [description of specific problem] ERROR <tab>

    # send and parse result
    result, id, qlen = send_dns_query(args.server, args.name, query_type, args.timeout, args.max_retries, args.port)
    parse_dns_response(result, id, qlen)

if __name__ == "__main__":
    main()
