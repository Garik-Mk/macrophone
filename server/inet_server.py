"""Server main lib"""
import socket
try:
    from proceed_command import apply_hotkey
except ModuleNotFoundError:
    from server.proceed_command import apply_hotkey

def get_ip():
    """Get current PC ip address"""
    hostname=socket.gethostname()
    return socket.gethostbyname(hostname)


def run_server():
    """Run actual socket server."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_ip = get_ip()
    server.bind((server_ip, 0))
    while True:
        print(f'IP and port for connection: {server_ip}:{server.getsockname()[1]}')

        server.listen() #TODO make to wait for several seconds

        user, address = server.accept() #TODO make connection manager
        print(f'Connection successful: {address, user} connected')

        while True:
            try:
                data = user.recv(1024)
            except ConnectionResetError:
                print('Error while reading from socket. Waiting for connection...')
                break
            if len(data) == 0:
                print('Client has been disconnected. Server waiting for connection...')
                break
            apply_hotkey(data)


if __name__ == '__main__':
    run_server()
