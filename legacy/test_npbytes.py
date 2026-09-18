
#numpy bytes. for socket.


basic = """
bytes( 'stringdata' ,encodeing = 'utf-8')
shall -> b'stringdata'
..looks like it.
decode( data )
become str again.

b'\xff'
is hex byte.

bytes('12', encoding = 'utf-8').hex()
'3132'
a is 61.

"""


#bytes , look just bytes...  = 
byte = """
#int 32
#a=np.array([1,2,3]).tobytes()
#b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00'

#np.array([1,2,3],dtype='int16').tobytes()
#b'\x01\x00\x02\x00\x03\x00'

#np.array([1,2,3],dtype='int8').tobytes()
#b'\x01\x02\x03'


#np.array([1,2,3],dtype='float32').tobytes()
#b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@'
"""

typeFtoC = """
#np.array([1,2,3],dtype='float32').tobytes('F')
#b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@'
#np.array([1,2,3],dtype='float32').tobytes('C')
#b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@'

#here changed. since bytes 1d shaped..
#np.array([[1,1],[2,2],[3,3]],dtype='float32').tobytes('F')
#b'\x00\x00\x80?\x00\x00\x00@\x00\x00@@\x00\x00 \x80?\x00\x00\x00@\x00\x00@@'
#np.array([[1,1],[2,2],[3,3]],dtype='float32').tobytes('C')
#b'\x00\x00\x80?\x00\x00 \x80?\x00\x00\x00@\x00\x00\x00@\x00\x00@@\x00\x00@@'
"""

didnt = """
np.zeros([4,3])
array([[0., 0., 0.],
       [0., 0., 0.],
       [0., 0., 0.],
       [0., 0., 0.]])
np.frombuffer( b, dtype='float32' ,like=np.empty([4,3]) )
array([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11.],
      dtype=float32)
np.frombuffer( b, dtype='float32' ,like=np.empty([4,3]) ).shape
(12,)
"""


fine="""
np.frombuffer( b, dtype='float32' ).reshape(4,3)
array([[ 0.,  1.,  2.],
       [ 3.,  4.,  5.],
       [ 6.,  7.,  8.],
       [ 9., 10., 11.]], dtype=float32)

"""


send_data = """
shape
dtype
bytes len

"""

import numpy as np
import json

def np_pack(nparr):
	byte = nparr.tobytes()
	shape = nparr.shape
	dtype = str(nparr.dtype)
	bytelen = len(byte)
	#print(byte, shape,dtype,datalen)
	return json.dumps( [bytelen,dtype,shape]) , byte

def np_back(byte, shape,dtype):
	return np.frombuffer(byte , dtype = dtype).reshape(shape)


a = np.array([1,2]  ,dtype = 'float32')
b = a.tobytes()

send(a)



