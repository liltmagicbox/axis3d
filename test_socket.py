from queue import Queue
import socket
import threading
import time



def queueVlist():
    "list extreamly faster!"
    q = Queue()
    t =time.time()
    for i in range(1000_000):
        q.put(i)
    print(time.time()-t)

    q = []
    t =time.time()
    for i in range(1000_000):
        q.append(i)
    print(time.time()-t)

    q = Queue()
    t =time.time()
    for i in range(1000_000):
        q.put(i)
    print(time.time()-t)


def bVlist():
    "list extreamly faster! , bytes+= seems slow."
    q = b''
    t =time.time()
    for i in range(150_0):
        q+= bytes(i)
    print(time.time()-t)

    q = []
    t =time.time()
    for i in range(150_0):
        q.append(bytes(i))
    bb=b''.join(q)
    print(time.time()-t)

    q = b''
    t =time.time()
    for i in range(150_0):
        q+= bytes(i)
    print(time.time()-t)

#500ms vs 800ms . 1.5M.
#4KB, 4MB, 1000.
# 1M x 4B*6 => 1M x 24B -> 24MB.
#40MB, 10000 times. .. 3ms vs 6ms.
def if4times():
    "list extreamly faster! , bytes+= seems slow."
    aa=[]
    a,b,c,d = 1,2,3,4

    t =time.perf_counter()
    for i in range(10000):
        aa.append(i)
    print(time.perf_counter()-t)

    t =time.perf_counter()
    for i in range(10000):
        if a==1:
            if b==2:
                if c==4:
                    1
                elif d==4:
                    aa.append(i)
    print(time.perf_counter()-t)

    t =time.perf_counter()
    for i in range(10000):
        aa.append(i)
    print(time.perf_counter()-t)

#if4times()
#exit()

def get_conn():
    HOST = 'localhost' # Standard loopback interface address (localhost) 
    PORT = 65432 # Port to listen on (non-privileged ports are > 1023)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    conn, addr = server.accept()  # blocking
    #can't get addr well.
    return conn



def accept_forever(server, clients):
    while True:
        conn, addr = server.accept()  # blocking
        conn.settimeout(50)

        #print('Connected: ', addr)
        #queue.put( (addr, 'connected') )
        queue = Queue()
        clients[addr] = queue
        t = threading.Thread(target = recv_forever, args = (conn,addr, clients) )
        t.start()


def bad_recv_forever(conn,addr, clients):
    START = 'START'.encode()
    END = 'END'.encode()
    li = None
    while True:
        try:
            data = conn.recv(4096)  # blocking
            if data != END:
                li.append(data)
                continue
        except ConnectionResetError:  # client without close.
            break
        except TimeoutError:
            break
        except AttributeError:
            pass
        if not data:  # client closed.
            break
        #print(data, type(data), data.decode() )  # bytes
        if data == START:
            li = []
        elif data == END:
            if li is None:
                continue
            #queue.put( (addr, 'data',  b''.join(li)) )
            queue = clients.get(addr)
            if queue is None:
                break
            queue.put( b''.join(li) )
            li = None
    #======================
    clients.pop(addr)
    #queue.put( (addr, 'disconnected') )

#tcp guarantees that all bytes received will be identical and in the same order as those sent

but = """
(('127.0.0.1', 2546), b"('localhost', 65432)ENDSTART('localhost', 65432)")
(('127.0.0.1', 2546), b"('localhost', 65432)ENDSTART('localhost', 65432)")
(('127.0.0.1', 2546), b"('localhost', 65432)ENDSTART('localhost', 65432)ENDSTART('localhost', 65432)ENDSTART('localhost', 65432)")
(('127.0.0.1', 2546), b"('localhost', 65432)ENDSTART('localhost', 65432)")
(('127.0.0.1', 2546), b"('localhost', 65432)")
(('127.0.0.1', 2546), b"('localhost', 65432)ENDSTART('localhost', 65432)")
(('127.0.0.1', 2546), b"('localhost', 65432)")
(('127.0.0.1', 2546), b"('localhost', 65432)")
    for addr, queue in self.clients.items():
RuntimeError: dictionary changed size during iteration

happended. since socket stacks at buffer..
"""

def recv_forever(conn,addr, clients):
    while True:
        try:
            data = conn.recv(64)  # blocking
            if not data:  # client closed.
                break
            #args = data.decode().split(',')
            length = int(data[:8].decode())
            key = data[8:16].decode().strip()
            args = data[16:].decode().split(',')
            data = ( key, get_data(conn,length) )
            
            queue = clients.get(addr)
            if queue is None:
                break
            queue.put( data  )

        except ConnectionResetError:  # client without close.
            break
        except TimeoutError:
            break
        except Exception as e:  # args got no ,
            print(e)
            break

        #print(data, type(data), data.decode() )  # bytes
    #print('server closed,',addr)
    #======================
    clients.pop(addr)


connitnuous = """
('localhost', 65432) dict_keys([('127.0.0.1', 2818)])
invalid literal for int() with base 10: '\x00L@\x0f\x00M@\x0f'
('localhost', 65432) dict_keys([])

server closed, but buffer has old data.
..we need flush.
"""

def get_data(conn, length, size=4096)->bytes:
    li = []
    times, left = divmod(length, size)

    for i in range(times):
        li.append(conn.recv(size))
    li.append(conn.recv(left))

    return b''.join(li)


scn = """
1.server connection wait
2. client connects.
3.server connected. start a thread.  sends READY to client.
4. client got READY, connection confirmed. (if negative, break.)

5.client sends header
6.server gets header, send back BODY.
7. client sends full data.
8.server got, parse, done.

#client sends alwayse.fine.

"""

class Server:
    def __init__(self, host = 'localhost', port=65432):
        #HOST = 'localhost' # Standard loopback interface address (localhost) 
        #PORT = 65432 # Port to listen on (non-privileged ports are > 1023)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind( (host, port))  #NOTE: localhost still fastest for internal.
        #self.server.bind((socket.gethostname(), port))  #NOTE: localhost still fastest for internal.
        self.server.listen(5)# connection waiting queue max 5.

        self.addr = host,port
        self.clients = {}
        #self.queue = Queue()

        
    def run(self):
        t = threading.Thread(target = accept_forever, args = (self.server, self.clients) )
        t.start()
    def get(self):
        #for addr, queue in self.clients.items(): during iter..
        for addr in tuple(self.clients):
            queue = self.clients.get(addr, Queue())
            while not queue.empty():
                yield addr, queue.get_nowait()

    def look(self):
        while True:
            print(self.addr, self.clients.keys())
            time.sleep(1)
            for i in self.get():
                print(len(i))

def main():
    s = Server()
    s.run()
    s.look()

if __name__ == '__main__':
    main()
