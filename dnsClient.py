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
    packet += format(id, '04x')

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

    # QNAME
    # domain names are represented as lists of labels
    qname = ""
    server_name_array = server_name.split('.')

    for label in server_name_array:

        # each label is preceded by a single byte giving the number of ASCII characters used in the label
        num_ascii_char = len(label)
        qname += format(num_ascii_char, '02x')

        # each character is coded using 8-bit ASCII
        for letter in label:
            qname += format(ord(letter), '02x')

    # To signal the end of a domain name, one last byte is written with value 0
    qname += "00"
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

    # QCLASS (always use 0x0001 in this field, representing an Internet address)
    packet += "0001"

    byte_sequence = bytes.fromhex(packet)
    return byte_sequence

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
            packet = parse_packet(name, query_type)
            clientSocket.sendto(packet, (server, port))

            # receive
            response, response_address = clientSocket.recvfrom(BUFFER)
            curr_time = time.perf_counter() - timer
            print("Response received after " + str(curr_time) + " seconds (" + str(i) + " retries)")
            clientSocket.close()
            return response

        except socket.timeout:
            if (i < max_retries):
                print("ERROR    Socket timeout, unanswered query")
            else:
                print("ERROR    Maximum number of retries " + str(max_retries) + " exceeded")
                clientSocket.close()
                sys.exit(1)

def parse_dns_response(result):
    print("NOTFOUND")

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

    # send logic
    result = send_dns_query(args.server, args.name, query_type, args.timeout, args.max_retries, args.port)
    parse_dns_response(result)

if __name__ == "__main__":
    main()
