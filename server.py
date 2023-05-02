"""Main server lib"""
import socket


class Server():
    def __init__(self) -> None:
        pass

    def open_new_connection(self, port: int) -> None:
        ...

    # def recive():     # IDK needed or not.
    #     ...

    def handle(self, signal: str) -> None:
        ...





def create_server(port: int) -> tuple[int]:
    """Creates server on localhost on given port"""
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.bind(('localhost', port))
    my_socket.listen(1)
    conn, addr = my_socket.accept()
    return (conn, addr)

def main_loop() -> None:
    """Main loop for recieving data from clients"""
    stop_flag = False
    conn, addr = create_server(3050)    # Temprorary value
    print(addr, "Connection succesful")
    while not stop_flag:
        data = conn.recv(1024)
        if not data:
            break
        print(data)
    conn.close()

if __name__ == '__main__':
    main_loop()