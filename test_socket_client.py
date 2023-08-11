import socket
import time

#sock.getsockname()
#('127.0.0.1', 6134)


host='localhost'
port=65432
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))


#except ConnectionRefusedError:

def send(byte_data):
    sock.sendall(byte_data)

