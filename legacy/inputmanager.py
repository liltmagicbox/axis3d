
def get_keymap(key_translate_map):
    key_map = { v:k for k,v in key_translate_map.items() }
    #fill 0 to 9, a to z
    for i in range(key_translate_map['0'], key_translate_map['9']+1):
        k = chr(i).lower()
        key_map[i] = k
    for i in range(key_translate_map['a'], key_translate_map['z']+1):
        k = chr(i).lower()
        key_map[i] = k
    return key_map


class Inputmap:
    """generalize all inputs, by key,value. mx,my, ml, mr, mm, a, esc, space, pagedown, ctrl, caps, shift, rshift
    ja jb jx jy jr1 jr2 jr3 jstart jrx jry jlx jly jup jdown jleft jright"""
    def __init__(self):
        self.data = {}

    def set(self, key,value):
        self.data[key] = value
    def get(self, key):
        return self.data.get(key)
    def flush(self):
        li = []
        for k,v in self.data.items():
            li.append(k)
            li.append(str(v)[:7])#1e-4 , 0.1234 0.2px for 2k.
        self.data.clear()
        return ','.join(li)

def _test():
    a = Inputmap()
    a.set('mx',0.334)
    a.set('my',0.133413253429857239578)
    a.set('ml',1)
    a.set('a',1)
    a.set('a',0)
    a.set('b',1)

    print(a.tostr())





key_setting = """
# single channel, key-value combination.
input_info = {
    'key':value,
    'a':True,
    'b':1,
    #'mx':396,
    #'mouse':(55,43),
    'mx':0.78,
    'ml':1,
    'l1':0.7,
    'J_L_X':0.5#-1to1
}

w -> forward 1.0
s -> forward -1.0
JL Y -> forward 1.0 #so -1 be -1..

axis 0-1
axis -1-0
button 0 or 1

it's 30ms, so don't care whether mouse click or xy first..
mousemove -> mouse click -> key -> else..

...no json.
just (keyname,keyvalue,,,) string-bytes.
mx,1/my,0.5/
mx,1,my,0.5

"""






strmakertest = """
from time import perf_counter

class Inputmap:
    def __init__(self):
        self.data = {}
    def set(self, key,value):
        self.data[key] = value
    def tostr(self):
        li = []
        for kv in self.data.items():
            li.extend( map(str,kv) )
        return ','.join(li)

t = perf_counter()

a = Inputmap()
a.set('mx',0.334)
a.set('my',0.1334)
a.set('ml',1)
a.set('a',1)
a.set('a',0)
a.set('b',1)

a.tostr()
print(perf_counter()-t)
class Inputmap:
    def __init__(self):
        self.data = {}
    def set(self, key,value):
        self.data[key] = value
    def tostr(self):
        li = []
        for k,v in self.data.items():
            li.append(k)
            li.append(str(v))
        return ','.join(li)

t = perf_counter()

a = Inputmap()
a.set('mx',0.334)
a.set('my',0.1334)
a.set('ml',1)
a.set('a',1)
a.set('a',0)
a.set('b',1)

a.tostr()
print(perf_counter()-t)

"""
