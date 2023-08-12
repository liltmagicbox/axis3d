import socket
import time

#sock.getsockname()
#('127.0.0.1', 6134)

class Client:
    def __init__(self, host='localhost', port=65432):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(5)
        self.address = (host, port)
    def connect(self):
        self.socket.close()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.socket.connect( self.address )
                break
            except ConnectionRefusedError:
                continue
        self.socket.settimeout(5)

    def send(self, data):
        #header = json.dumps( {'key':'keyname', 'length':length , 'npinfo': [(32,4),'float32'] } )
        #64, 8+8+ key-len-args.
        length = str(len(data)).zfill(8)
        key = 'key'.rjust(8)  # f"{a:<8}"
        args = '32,4,float32'.ljust(48)
        header = f'{length}{key}{args}'.encode()

        try:
            self.socket.sendall(header)
            self.socket.sendall(data)
        except ConnectionResetError:
            print('reconnecting..')
            self.connect()



def main():
    cli = Client()
    cli.connect()
    import numpy as np

    while True:
        #data= str(cli.addr).encode()
        data = np.arange(20).tobytes()
        cli.send(data)
        time.sleep(0.001)

if __name__ == '__main__':
    main()
