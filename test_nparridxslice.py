import numpy as np
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

import time
tt =time.perf_counter
a = np.random.rand(100_0000)
b = a>0.99
i = np.nonzero(b)
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
