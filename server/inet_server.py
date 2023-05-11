import netifaces as ni
import socket


def get_ip():
    return ni.ifaddresses('wlp1s0')[ni.AF_INET][0]['addr']


def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #server.bind((get_ip(), 10000))
    # ip = '192.168.44.115'
    ip = get_ip()
    print('IP for connection ', ip)
    server.bind((ip, 10000))

    server.listen()

    user, address = server.accept()
    print('Connection successful')

    while True:                     # temp
        data = user.recv(1024)      #
        print(data.decode('utf-8')) #

    return user


if __name__ == '__main__':
    run_server()
