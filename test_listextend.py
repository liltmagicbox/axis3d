import time
tt = time.perf_counter

def extendtest():
	a = []
	b = [i for i in range(1000_000)]
	t = tt()
	a.extend(b)
	print(tt()-t)

	a = []
	b = [i for i in range(1000_000)]
	#c = a[:500_000]
	t = tt()
	a.extend(b)

	print(tt()-t)

#10ms for 1M
#cutting 500k took 4ms.

#7ms -> 1M
#3.5ms -> 500k

#... we have no problem. great.

a = []
b = [i for i in range(1000_000)]
t = tt()
x = b[-1:]
#b.pop()
#print(x)
print(tt()-t)
#5e-6
#..same.