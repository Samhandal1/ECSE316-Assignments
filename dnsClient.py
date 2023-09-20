import argparse
import sys

def send_dns_query(server, name, query_type, timeout, max_retries, port):
    print(f"DnsClient sending request for {name}")
    print(f"Server: {server}")
    print(f"Request type: {query_type}")

    # This is just a placeholder. Actual querying logic should be implemented here.
    # This code will always return "NOTFOUND" for now.
    
    return "NOTFOUND"

def main():
    parser = argparse.ArgumentParser(description="DnsClient")

    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout for retransmitting an unanswered query.")
    parser.add_argument("-r", "--max-retries", type=int, default=3, help="Maximum number of retries for unanswered query.")
    parser.add_argument("-p", "--port", type=int, default=53, help="UDP port number of the DNS server.")
    parser.add_argument("-mx", "--mail-server", action="store_true", help="Send an MX (mail server) query.")
    parser.add_argument("-ns", "--name-server", action="store_true", help="Send an NS (name server) query.")
    parser.add_argument("server", help="IPv4 address of the DNS server.")
    parser.add_argument("name", help="Domain name to query for.")

    args = parser.parse_args()

    if args.mail_server and args.name_server:
        print("ERROR\tBoth -mx and -ns cannot be given simultaneously.")
        sys.exit(1)

    query_type = "A"
    if args.mail_server:
        query_type = "MX"
    elif args.name_server:
        query_type = "NS"

    result = send_dns_query(args.server, args.name, query_type, args.timeout, args.max_retries, args.port)
    print(result)

if __name__ == "__main__":
    main()
