import socket
import time

#sock.getsockname()
#('127.0.0.1', 6134)

class Client:
	def __init__(self, host='localhost', port=65432):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.addr = (host, port)
	def connect(self):
		while True:
			try:
				self.sock.connect( self.addr )
				break
			except ConnectionRefusedError:
				continue
		print('connected')
	def send(self, byte_data):
	    self.sock.sendall(byte_data)

def main():
	cli = Client()
	cli.connect()
	while True:
		cli.send(b'START')
		cli.send( str(cli.addr).encode() )
		cli.send(b'END')
		time.sleep(0.001)

if __name__ == '__main__':
	main()