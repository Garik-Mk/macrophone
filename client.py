import socket


# Parser needed

class Client():
    def __init__(self) -> None:
        pass

    def connect(self, address: str, port: int):
        ...

    def send(self):
        ...





def main_loop():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(('localhost', 3050))
    while True:
        input_data = input()
        my_socket.sendall(input_data.encode('utf-8'))
    my_socket.close()

if __name__ == '__main__':
    main_loop()
