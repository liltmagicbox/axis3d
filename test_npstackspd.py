import numpy as np
import time
tt = time.perf_counter
tt()


#1M, extend 1 took, 1.5ms. 3M, 5ms.
a = np.random.rand(1000_000)
b = np.zeros(1000_001).astype('float32')
t=tt()
b[:-1] = a
print(tt()-t)


def extend_experiment():
	a = np.random.rand(1000_000)
	b = np.random.rand(1000_000)
	t=tt()
	c = a>0.5 #1.7ms
	b[c] #16ms
	print(tt()-t)

	i = np.nonzero(c)
	t=tt()
	b[i] #4ms!
	print(tt()-t)
	result = " the slicing, is happened if arr has empty. what if arr is full, no need to be sliced..?"

a = np.arange(1000_000)
b = np.arange(1000_000)
c = np.arange(1000_000)

tt = time.perf_counter

t=tt()
x = np.stack([a,b,c])
#print(x)
print(tt()-t)
result='5ms for stacking 1M*3 -> 3M.'


