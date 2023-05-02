import socket

def create_server() -> tuple[int]:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.bind(('localhost', 3030))
    my_socket.listen(1)
    conn, addr = my_socket.accept()
    return (conn, addr)

def main_loop() -> None:
    stop_flag = False
    conn, addr = create_server()
    print(addr, "Connection succesful")
    while not stop_flag:
        data = conn.recv(1024)
        if not data:
            break
        print(data)
    conn.close()

if __name__ == '__main__':
    main_loop()