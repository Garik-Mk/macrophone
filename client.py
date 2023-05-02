import socket

def main_loop():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect(('localhost', 3030))
    while True:
        input_data = input()
        my_socket.sendall(input_data.encode('utf-8'))
    my_socket.close()

if __name__ == '__main__':
    main_loop()