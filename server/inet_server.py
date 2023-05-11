import socket


def get_ip():
    hostname=socket.gethostname()
    return socket.gethostbyname(hostname)


def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #server.bind((get_ip(), 10000))
    # ip = '192.168.44.115'
    ip = get_ip()
    port = 2234
    print('IP for connection ', ip)
    server.bind((ip, port))
    

    server.listen()

    user, address = server.accept()
    print('Connection successful')

    while True:                     # temp
        data = user.recv(1024)      #
        print(data.decode('utf-8')) #

    return user


if __name__ == '__main__':
    run_server()
