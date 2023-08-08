#nptest
import numpy as np


def get_collision_combi(N=5):
	a = np.arange(1,N+1)

	#for i in range(1, N):
	for i in range(1, len(a)):
		print( i ,  a[i:])

get_collision_combi()






from time import perf_counter

#50, 0.0008 , 0.8ms.
#100 1.9ms
#1000, 28ms.huh.
perf_counter()

data = {}
N = 50
for N in range(900,1300):
	continue
	#x->> rowmajor
	pos = np.random.rand(3,N).astype('float32')

	# t = perf_counter()
	# for i in range(N-1):
	# 	p0 = pos[:,i]
	# 	dist2 = np.sum( (pos[:,i+1:] -p0.reshape(3,1))**2 ,axis=0)
	# t = perf_counter()


	t = perf_counter()
	# (x-x)^2 +...
	for i in range(N-1):
		p0 = pos[:,i]
		dist2 = np.sum( (pos[:,i+1:] -p0.reshape(3,1))**2 ,axis=0)
		#print(dist2)
	#print(perf_counter()-t)
	data[N] = perf_counter()-t
	print(N,end='/')

#for i,v in data.items():
#	print(i,v)


#======================vertical   [0] = [x,y,z] .. assume slower, it was.
data = {}
N = 50
for N in range(900,1300):
	#x->> rowmajor
	pos = np.random.rand(N,3).astype('float32')

	t = perf_counter()
	# (x-x)^2 +...
	for i in range(N-1):
		p0 = pos[i]
		dist2 = np.sum( (pos[i+1:] -p0)**2 ,axis=0)
		#print(dist2)
	#print(perf_counter()-t)
	data[N] = perf_counter()-t
	print(N,end='/')



from matplotlib import pyplot as plt
x = data.keys()
y = data.values()
plt.plot(x,y)
plt.show()






#=========================
#npsum int danger.

def sumsum():
	a = np.arange(100_000)
	a[0] = 1
	np.sum(a)
#sum errors.

"""
np.prod(a[5:14])
259459200
>>> np.prod(a[5:15])
-662538496
>>>
NP i 64!
py but unlimited.

#np.prod overflow??


#======
#see float working for sum, not prod.

a = np.arange(1,100000).astype('float32')
np.sum(a)
4999950000.0

>>> np.prod(a)
C:python310libsite-packagesnumpycorefromnumeric.py:88: RuntimeWarning: overflow encountered in reduce
  return ufunc.reduce(obj, axis, dtype, out, **passkwargs)
inf
>>>



#======
# random [] whlie rand ,

np.random.random( [3,2] )
array([[0.21678322, 0.73683952],
       [0.8530055 , 0.27792319],
       [0.58520805, 0.72195073]])
>>> np.random.random(3,2 )
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "mtrand.pyx", line 438, in numpy.random.mtrand.RandomState.random
TypeError: random() takes at most 1 positional argument (2 given)
>>> np.random.rand(3,2 )
array([[0.66288634, 0.82878273],
       [0.68886315, 0.10292406],
       [0.39328583, 0.77475276]])
>>>

USE randn a,b)
random.standard_normal tuple

nanprod nansum nan skips.good.


#====
np.comprod
1, 1+2, 1+2+3 ,,,
np.cumprod([1,2,3,4,5])
array([  1,   2,   6,  24, 120])
>>>


#====
DESCRETE DIFF!!!!

np.diff
np.diff([1,2,4,4,6])
array([1, 2, 0, 2])
>>>

lambda x: x**2

np.diff( [ b(i) for i in range(15) ] )
array([ 1,  3,  5,  7,  9, 11, 13, 15, 17, 19, 21, 23, 25, 27])
>>> [ b(i) for i in range(15) ]
[0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196]
>>>

np.diff( [ b(i) for i in range(15) ] ,n=2)
array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
>>>
recursive- whatever- 2nd diff!





"""


