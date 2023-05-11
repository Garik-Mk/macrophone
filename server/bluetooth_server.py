"""Temp. May be removed"""

import socket
from getmac import get_mac_address as gma

def main():
    """Main func"""
    bt_mac = gma() # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
    print(bt_mac)

    port = 4 # 3 is an arbitrary choice. However, it must match the port used by the client.
    backlog = 1
    size = 1024


    server = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    server.bind((bt_mac,port))
    server.listen(backlog)
    try:
        client, address = server.accept()
        print(address, 'has been connected')
        while 1:
            data = client.recv(size)
            if data:
                print(data)
    except Exception:
        print("Closing socket")
        client.close()
        server.close()

main()
