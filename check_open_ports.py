import socket
import sys
from optparse import OptionParser

# Exit Codes
EXIT_OK = 0
EXIT_WARNING = 1
EXIT_CRITICAL = 2
EXIT_UNKNOWN = 3

def start_check(host: str, start_port: int, end_port: int):
    open_ports = []
    for port in range(start_port, end_port):
        location = (host, port)
        result = check_port_open(location)

        #print("Result for port " + str(port) + ": " + str(result))

        if result == 0:
            open_ports.append(port)

    return open_ports

def check_port_open(location):
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = soc.connect_ex(location)
    soc.close()
    return result

def parse_open_ports(ports: str):
    if ports == "":
        return []
    
    try:
        allowed_ports = [int(i) for i in ports.split(",")]
        allowed_ports = sorted(allowed_ports)
        return allowed_ports
    except:
        print("Error, check list of allowed ports. Example: -P 500,21,23,80,3333")
        sys.exit(EXIT_UNKNOWN)

def check_not_allowed_ports(open_ports, allowed_ports):
    not_allowed_ports = []
    for port in open_ports:
        not_allowed_ports.append(port)
    for port in allowed_ports:
        if port in open_ports:
            not_allowed_ports.remove(port)
    return not_allowed_ports

def check_false_allowed_ports(open_ports, allowed_ports):
    false_allowed_ports = []
    for port in allowed_ports:
        false_allowed_ports.append(port)
    for port in allowed_ports:
        if port in open_ports:
            false_allowed_ports.remove(port)
    return false_allowed_ports

def main():
    parser = OptionParser("usage: %prog -h <IP address> and -p <port or list of ports>, that have been authorized to be open")
    parser.add_option("-H", "--hostaddress", dest = "host", default = "", help = "Specify the IP address you want to check")
    parser.add_option("-P", "--port", dest = "port", default = "", help = "Specify the port or list of ports that are allowed to be open. Example: -P 500,21,23,80,3333")
    parser.add_option("-S", "--startportrange", dest = "spr", default = "0", help = "Specify the start port from which open ports will be checked (start port included)")
    parser.add_option("-E", "--endportrange", dest = "epr", default = "65536", help = "Specify the end port to which open ports will be checked (end port included)")
    (opts, args) = parser.parse_args()

    if opts.host == "":
        print("Error, host not specified. Example: -H 127.0.0.1")
        sys.exit(EXIT_UNKNOWN)

    start = 0
    end = 65537

    try:
        start = int(opts.spr)
        end = int(opts.epr) + 1
    except:
        print("Error, check start and end port specification")
        sys.exit(EXIT_UNKNOWN)

    open_ports = start_check(opts.host, start, end)
    allowed_ports = parse_open_ports(opts.port)
    not_allowed_ports = check_not_allowed_ports(open_ports, allowed_ports)
    false_allowed_ports = check_false_allowed_ports(open_ports, allowed_ports)

    if len(not_allowed_ports) > 0:
        ports = ""
        for port in not_allowed_ports:
            ports = ports + str(port) + "\n"
        print("Critical, there are ports open wich were not specified as allowed open ports. Open ports are:\n" + ports)
        sys.exit(EXIT_CRITICAL)
    
    if len(false_allowed_ports) > 0:
        ports = ""
        for port in false_allowed_ports:
            ports = ports + str(port) + "\n"
        print("Warning, there are more ports specified as allowed open ports than are actually open. Unused allowed ports are:\n" + ports)
        sys.exit(EXIT_WARNING)
    
    print("OK, all open ports are marked as allowed")
    sys.exit(EXIT_OK)

if __name__ == "__main__":
    main()