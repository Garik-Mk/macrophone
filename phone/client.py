
import socket
import sys


def parse_ip_and_port(inputstring: str) -> tuple:
    """Parse 192.168.1.213:3245 into ('192.168.1.213', 3245)"""
    ip, port = inputstring.split(':')
    port = int(port)
    return (ip, port)



def connect(connect_address: tuple):
    """Main client connection function"""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect(connect_address)

    print('Connection successful')

    while 1:        #temp, will be replaced with pipeline to main file
        text = input()
        if text == "quit":
            break
        client.send(bytes(text, 'UTF-8'))


if __name__ == '__main__':
    address = parse_ip_and_port(sys.argv[1])
    connect(address)
