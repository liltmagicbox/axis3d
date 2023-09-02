import numpy as np


def test1():
	import time
	tt =time.perf_counter
	a = np.random.rand(100_0000)
	b = a>0.5
	i = np.nonzero(b) #e-6 fast!
	#i = i[0]
	#-----
	t = tt()
	a[i] #3ms for 500k, as we know.
	print(tt()-t)
test1()
exit()

def copytest():
	a = np.arange(12)

	b = a[[4,5,6]]
	b+=2
	print(a)
	print(b)

	a[[4,5,6]]+=10
	print(a)
	print(b)

	result='b is copy of.  we need on-demand access.'

def test1():
	import time
	tt =time.perf_counter
	a = np.random.rand(100_0000)
	b = a>0.5
	i = np.nonzero(b)
	#i = i[0].astype('int32') it must be as it was.. 64 is faster, (1,) is little.
	#i = [i for i in range(500000)] #58ms, while nonzero=i32(1,) 38ms, i64 44ms.
	#print(i)
	#print(a[i])
	#print(a[b])

	t = tt()
	a[b]
	print(tt()-t)
	t = tt()
	a[b]
	print(tt()-t)
	t = tt()
	a[i]
	print(tt()-t)
	t = tt()
	a[i]
	print(tt()-t)
	print('----------')

#a>0.5
0.01650230004452169
0.017554700141772628
0.005107099888846278
0.004752000095322728
result = 'i cant believe...'

#a>0.01
0.006735499948263168
0.009210200048983097
0.008031400153413415
0.008223199984058738

#a>0.99
0.001438099890947342
0.0016863998025655746
0.0002962998114526272
0.00034909998066723347




test1()

#
0.024958600057289004
0.020993900019675493
0.006279099965468049
0.0068552999291568995
#----------
10.959065899951383
4.125973500078544
3.4548210001084954
2.5722212998662144
#----------
5.7634142998140305
3.592626600060612
3.7304760001134127
4.19629539991729
#when n=100..
#we need each-line-array!



N = 3
#=====================
def test2():
	import time
	tt =time.perf_counter
	a = np.random.rand(N*100_0000).reshape(N,-1)
	b = a[0]>0.5
	i = np.nonzero(b)
	#i = i[0].astype('int32') it must be as it was.. 64 is faster, (1,) is little.
	#i = [i for i in range(500000)] #58ms, while nonzero=i32(1,) 38ms, i64 44ms.
	#print(i)
	#print(a[i])
	#print(a[b])

	t = tt()
	a[:,b]
	print(tt()-t)
	t = tt()
	a[:,b]
	print(tt()-t)
	t = tt()
	a[:,i]
	print(tt()-t)
	t = tt()
	a[:,i]
	print(tt()-t)
	print('#----------')
test2()

def test3():
	import time
	tt =time.perf_counter
	a = np.random.rand(N*100_0000).reshape(-1,N)
	b = a[:,0]>0.5
	i = np.nonzero(b)
	#i = i[0].astype('int32') it must be as it was.. 64 is faster, (1,) is little.
	#i = [i for i in range(500000)] #58ms, while nonzero=i32(1,) 38ms, i64 44ms.
	#print(i)
	#print(a[i])
	#print(a[b])

	t = tt()
	a[b]
	print(tt()-t)
	t = tt()
	a[b]
	print(tt()-t)
	t = tt()
	a[i]
	print(tt()-t)
	t = tt()
	a[i]
	print(tt()-t)
	print('#----------')
test3()
