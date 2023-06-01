
import socket
import sys
sys.path.append("..")
from server.utils import ACCEPTABLE_KEYS


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
    return client

def is_valid_command(command: str) -> bool:
    """Gets command in 'key+key+key' style and validates that all keys exist"""
    commands_list = command.split('+')
    for each_command in commands_list:
        if not each_command.lower() in ACCEPTABLE_KEYS:
            return False
    return True

def send_command(sock, command: str):
    """Send command to pc"""
    if is_valid_command(command):
        print("Sending command.. ", command)
        sock.send(bytes(command, 'UTF-8'))
    else:
        print('Invalid command')

if __name__ == '__main__':
    address = parse_ip_and_port(sys.argv[1])
    connect(address)
