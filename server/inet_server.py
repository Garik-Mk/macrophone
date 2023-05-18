"""Server main lib"""
import socket
from .key_press import handler


def get_ip():
    """Get current PC ip address"""
    hostname=socket.gethostname()
    return socket.gethostbyname(hostname)


def run_server():
    """Run actual socket server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = get_ip()
    server.bind((server_ip, 0))
    print(f'IP and port for connection: {server_ip}:{server.getsockname()[1]}')
    # quit() # temp, for debug
    server.listen() #TODO make to wait for several seconds

    user, address = server.accept() #TODO make connection handler
    print(f'Connection successful: {address, user} connected')

    while True:
        data = user.recv(1024)
        if len(data) == 0:
            print('Client has been disconnected. Server closed')
            break
        handler(data.decode('utf-8'))
        print(data.decode('utf-8'))

    return user


if __name__ == '__main__':
    run_server()
