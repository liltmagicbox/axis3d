from queue import Queue
import threading
import socket
import time

#sock.getsockname()
#('127.0.0.1', 6134)


def sendall(socket,data):
    #header = json.dumps( {'key':'keyname', 'length':length , 'npinfo': [(32,4),'float32'] } )
    #64, 8+8+ key-len-args.
    args,data = data
    #'keyname:arg1,arg2,arg3'
    #key, args = args.split(':')
    
    length = str(len(data)).zfill(8)
    #key = key.rjust(8)  # f"{a:<8}"
    #args = str(args).ljust(48)
    #key = 'key'.rjust(8)  # f"{a:<8}"
    #args = '32,4,float32'.ljust(48)
    header = f'{length}{args}'.ljust(64).encode()

    try:
        socket.sendall(header)
        socket.sendall(data)# OSError not socket object ..
    except ConnectionResetError:
        socket.close()
    except ConnectionAbortedError:
        socket.close()


def sendall_forever(address, queue, ready, is_udp):
    "socketholder for thread-in socket."
    ready.clear()
    socket = get_connected(address, is_udp)
    ready.set()
    while True:
        if socket._closed:
            ready.clear()
            socket = get_connected(address, is_udp)
            ready.set()

        data = queue.get()  # block
        sendall(socket, data)


def get_connected(address, is_udp=False):
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if is_udp:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    while True:
        try:
            sock.connect( address )
            break
        except ConnectionRefusedError:
            continue
    return sock

class Client:
    def __init__(self, port=65432, localhost = True, udp=False):
        self.udp = udp
        if localhost:
            host = 'localhost'
        else:
            host = socket.gethostbyname(socket.gethostname())  # this is local ip.
        self.address = (host, port)
        self.queue = Queue()
        self.ready = threading.Event()
        self.connect()
    def send(self, data):
        "fire & forget"
        if self.udp:
            if not self.ready.is_set():
                return
        self.queue.put(data)

    def connect(self):
        t = threading.Thread(target = sendall_forever, args = (self.address, self.queue, self.ready, self.udp) )
        t.start()


def main():
    cli = Client()
    import numpy as np

    while True:
        #data= str(cli.addr).encode()
        data = np.arange(5).astype('int8').tobytes()
        cli.send( ('key,arg1',data) )
        time.sleep(0.001)

if __name__ == '__main__':
    main()
