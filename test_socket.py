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

if4times()
exit()

def get_conn():
    HOST = 'localhost' # Standard loopback interface address (localhost) 
    PORT = 65432 # Port to listen on (non-privileged ports are > 1023)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    conn, addr = server.accept()  # blocking
    #can't get addr well.
    return conn



def accept_forever(server, queue):
    while True:
        conn, addr = server.accept()  # blocking
        conn.settimeout(50)

        #print('Connected: ', addr)
        queue.put( (addr, 'connected') )

        t = threading.Thread(target = recv_forever, args = (conn,addr, queue) )
        t.start()


def recv_forever(conn,addr, queue):
    DATA = 'DATA'.encode()
    END = 'END'.encode()
    li = []
    state = 0
    while True:
        try:
            data = conn.recv(1024)  # blocking
        except ConnectionResetError:  # client without close.
            break
        except TimeoutError:
            break
        if not data:  # client closed.
            break
        #print(data, type(data), data.decode() )  # bytes
        if data == DATA:
            state = 1
        elif data == END:
            queue.put( (addr, 'data',  b''.join(li)) )
            li = []
            state = 0
        else:
            if state:
                li.append(data) #this adds 4 of if.
    #======================
    queue.put( (addr, 'disconnected') )



def get_data(conn)->bytes:
    li = []
    while True:
        try:
            data = conn.recv(1024)  # blocking
            li.append(data)
        except:
            return b''
        if data == END:
            break
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
        self.server.bind((host, port))
        self.server.listen(5)#5 max??

        self.queue = Queue()

    def run(self):
        t = threading.Thread(target = accept_forever, args = (self.server, self.queue) )
        t.start()

    def look(self):
        while True:
            print('tick')
            time.sleep(1)
            while not self.queue.empty():
                print(self.queue.get_nowait())


def main():
    s = Server()
    s.run()
    s.look()

if __name__ == '__main__':
    main()
