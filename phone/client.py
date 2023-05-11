import argparse
import socket


def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='Client',
        description='Client for macros server',
    )
    parser.add_argument('-b', '--mac_address', type=str, required=False, help='MAC address')    #WORK IN PROGRESS
    parser.add_argument('-i', '--ip', type=str, default='127.0.0.1', help='Server public address')
    parser.add_argument('-p', '--port', type=int, default=10000, help='Server Port')
    return parser.parse_args()


def connect_inet(ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((ip, int(port)))

    print('Connection successful: ip=', ip, ' port=', port)
    
    while 1:
        text = input()
        if text == "quit":
            break
        client.send(bytes(text, 'UTF-8'))


def connect_bluetooth(serverMACAddress, port=3):
    client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    client.connect((serverMACAddress,port))
    while 1:
        text = input()
        if text == "quit":
            break
        client.send(bytes(text, 'UTF-8'))
    client.close()


def connect_usb():
    ...

if __name__ == '__main__':
    address = input('MAC: ')
    port = input('port: ')
    connect_inet(address, port)