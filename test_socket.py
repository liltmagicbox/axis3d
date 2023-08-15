from queue import Queue
import socket
import threading
import time

HEADER_LEN = 128


explain_socket = """

소켓통신 정리.
아무튼 편리하고 빠르다고 하고
결론적으로 UDP도 DGRAM 인가로 되게 쉽게 되었을뿐이었다.
TCP는 순서유지된다고하는데 , 로컬이라면 u쪽도 그러리라 보긴 함.

4096 8102? 의 버퍼가 통상적 네트워크의..라고 하니 그정도로 하도록 하고
패킷이 지나치게 크면 오히려 느리단걸 봐서인지,
그러나 반복이 우려되긴했으나, 4키로바이트 씩 쏘니까 1000번만에도 4메가라 충분할듯함...적은가.
뭐 아무튼 스레드에서 돌아기니 괜찮다는 식으로 넘겼습니다.

큐는 기본적으로 문제없으니 사용하도록 하고
설계구조상 사전을 쓰거나 하는건 매우 불편한 방식으로 되긴 했다. 서버측엔 쓴채 남아버렸지만 결국..

웹소켓 크롬측에서 스테이트 커넥팅 커넥티드 디스커넥 이 괜히있는게 아녔다 싶어. 거의 근접했으나
thread 에서 왠지 counter 가 바로 안 보이길래 그냥 안했습니다.

서버측에선 수신되면 그걸 죄다 스레드로 넘겨서 처리한다는 식으로 돌려야하는거겠고

로컬호스트가 빠르긴하고 , 겟프롬네임-겟호스트네임 식으로  써서 겨우 현재 구동중인 로컬 아이피를 얻어냈다.

B''+=하면 처참히 느릴거같애서 결국 조인으로 리스트에 더하는식으로 하는건 잘 했고,
이번엔 반복문 효과적으로 DIVMOD써서 처리했다. 정확히 받을 바이트를 받는게 핵심이라나.
그래서 고정길이의 헤더라는 개념이 나오는데, LJUST 라는걸로 뭉치는게 되니까 매우 유용했다. 이후 스트립,스플릿으로.
ARGS는 그냥 단일로 ,로 구분하게했고 매우 잘했다.

원래 의도된것인 넘파이 데이터보내기도 가능할듯. 송수신측에서 ARGS를 처리하는법은 알고있어야겠지만.

서버측에선, , 왠지, 포트가 열린 상태라면 파이썬자동종료도 되긴 ㅏ지만 명시적으로 클로즈를 해주는게 낫다고 적혀있었고
그래야 보내는측에서도 타임아웃에 의해 에러가 발생하는게 가능했다.
그외에 포트점유에의한 문제는 oS에러가 뜨는것이고 나머지는 파이썬에러로 납득가능한 식으로 돌아가곤 한다..

SENDALL / RECV외엔 일단 안 썼으며 뭐..
아. 버퍼같은곳에 마구 적재되므로, 1024 걸어뒀을시, 포화되면, 다음것이 자동으로 들어와버리는식으로 들어와있으므로 주의.
OK 같은 핸드셰이크를 또 하는건 정말 아닌거같았는데, 결국 되긴 했다. 어제 2시경부터 했으니 나름 되었지뭐.
7시간, 5시간 12시간만에 얻어낸 결과다.
보내는측에선 버릴각오하고 보내되 특히 유디피를 애용하거나, 티씨피는 아무튼 로컬에선 별차이없다고 보며 진행했다.

타임아웃에의해 어쨌든 유발되면 다행인데,   클라측에선 보냄 했을때 에러가 발생하던가 했기도 했고 뭐.

"""

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
    server.close()

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
            data = conn.recv( HEADER_LEN )  # blocking
            if not data:  # client closed.
                break
            #args = data.decode().split(',')
            length = int(data[:8].decode())
            
            #key = data[8:16].decode().strip()
            #args = data[16:].decode().split(',')
            args = data[8:].decode().strip().split(',')
            data = get_data(conn,length)
            
            queue = clients.get(addr)
            if queue is None:
                break
            queue.put( (args,data)  )

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
    conn.close()
    clients.pop(addr)


connitnuous = """
('localhost', 65432) dict_keys([('127.0.0.1', 2818)])
invalid literal for int() with base 10: '\x00L@\x0f\x00M@\x0f'
('localhost', 65432) dict_keys([])

server closed, but buffer has old data.
..we need flush.
"""

def get_data(conn, length, size=8192)->bytes:
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
    def __init__(self, port=65432, localhost = True, udp=False):
        #HOST = 'localhost' # Standard loopback interface address (localhost) 
        #PORT = 65432 # Port to listen on (non-privileged ports are > 1023)
        if udp:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if localhost:
            host = 'localhost'
        else:
            host = socket.gethostbyname(socket.gethostname())  # this is local ip.
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
                #yield queue.get_nowait()
                yield addr, queue.get_nowait()

    def look(self):
        while True:
            print(self.addr, self.clients.keys())
            time.sleep(1)
            for i in self.get():
                #addr, arg+data
                #print(i[0], i[1][0] , len(i[1][1]) )
                print(i)

def main():
    s = Server()
    s.run()
    s.look()

if __name__ == '__main__':
    main()
