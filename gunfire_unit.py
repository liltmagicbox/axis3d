import numpy as np
import platform


DEFAULT_ARR_LENGTH = 5
MAX_ARR_LENGTH = 200_0000

DTYPE_INT = 'int64'
DTYPE_FLOAT = 'float32'
#platform.machine()'AMD64'
#platform.architecture() ('64bit', 'WindowsPE')
if not platform.architecture()[0] == '64bit':
	DTYPE_INT = 'int32'


def make_idxs(arr):
	return np.nonzero(arr)[0]
def make_rand(n):
	return np.random.rand(n)
def make_randn(n):
	return np.random.randn(n)
def make_randint(n, a,b):
	if b is None:
		b = a
		a = 0
	size = n
	return np.random.randint(a, b, size)
def make_b(n):
	return np.zeros(n, dtype='bool')
def make_i(idxs):
	return np.array(idxs, dtype= DTYPE_INT) #on 64bit pc, dtype=int == i32  => slow.
def make_1d(n):
	return np.zeros(n).astype(DTYPE_FLOAT)
def make_nd(n,rows):
	return np.zeros( (rows, n) ).astype(DTYPE_FLOAT)
def make_arr(n, value):
	try:
		return make_nd(n, len(value) )
	except:
		return make_1d(n)
#----
def extend_1d(arr, n=0):
	old_n = len(arr)
	n = int(old_n*0.5) if n==0 else n
	new = make_1d(old_n+n)
	new[:old_n] = arr
	return new
def extend_nd(arr, n=0):
	rows, arrlen = arr.shape
	n = int(arrlen*0.5) if n==0 else n
	new = make_nd(n, rows)
	return np.hstack( [arr, new] )
def extend_arr(arr,n=0):
	a , *b = arr.shape
	if b:
		return extend_nd(arr,n)
	else:
		return extend_1d(arr,n)
#----
def is_1d(arr):
	a , *b = arr.shape
	return not bool(b) # [] is 1d
def set_arr(arr, value, idxs):
	if is_1d(arr):
		set_arr_1d(arr,value,idxs)
	else:
		set_arr_nd(arr,value,idxs)
def set_arr_1d(arr, value, idxs):
	if idxs is None:
		arr[:] = value
	else:
		arr[idxs] = value
def set_arr_nd(arr, value, idxs):
	#value [1,2,3] [[1],[2],[3]]
	try:
		len(value[0])
	except:  #value (1,2,3) , need transpose.
		value = tuple( (i,) for i in value )
	if idxs is None:
		arr[:] = value
	else:
		arr[:,idxs] = value

def get_arr(arr, idxs):
	if idxs is None:
		return arr
	else:
		if is_1d(arr):
			return arr[idxs]
		else:
			return arr[:,idxs]

def parse_xyz(key):
	if key.endswith('x'):
		i = 0
	elif key.endswith('y'):
		i = 1
	elif key.endswith('z'):
		i = 2
	key = key[:-1]
	return key,i

#=========================

class UnitArray:
	def __init__(self, attr_dict, n=None):
		n = DEFAULT_ARR_LENGTH if n is None else n
		self.fixed = False if n == DEFAULT_ARR_LENGTH else True
		self.default = attr_dict.copy()
		
		self.free_idxs = []
		self.active = None
		self.data = {}
		self._setdata(n)
	def _setdata(self, n):
		self.free_idxs = [i for i in range(n)]
		self.active = make_b(n)
		self.data = {}
		for key, value in self.default.items():
			self.data[key] = make_arr(n, value)
	#--------------
	def __len__(self):
		"for internal only.. like rand."
		return len(tuple(self.data.values())[0])
	
	def __repr__(self):
		ss = ['----Unit Array----']
		ss.append( f"{self.active}--{'active'}{self.active.shape}" )
		for key,value in self.data.items():
			ss.append( f"{value}--{key}{value.shape}" )
		ss.append('----')
		return '\n'.join(ss)
	#====
	def _extend(self, n):
		now_n = len(self)
		half_n = now_n//2
		ext_n = half_n if n<half_n else n
		if (now_n+ext_n > MAX_ARR_LENGTH) or self.fixed: raise OverflowError("array can't extend")
		#---
		for key, arr in self.data.items():
			self.data[key] = extend_arr(arr, ext_n)
		#---
		idxs = [i for i in range(now_n, now_n+ext_n)]
		self.free_idxs.extend(idxs)
		active = make_b(now_n+ext_n)
		active[:now_n] = self.active
		self.active = active

	def _get_free_idxs(self, n):
		if len(self.free_idxs) < n:
			self._extend(n)

		idxs = self.free_idxs[-n:]
		self.free_idxs = self.free_idxs[:-n]
		return make_i(idxs)
	#-----	
	#external 4 interfaces.
	def acquire(self, n=1, **kwargs):
		if n<1:raise ValueError("n must be >=1")
		idxs = self._get_free_idxs(n)
		for key, value in self.default.items():
			value = kwargs.get(key, value)
			self.set(key,value, idxs)
		self.active[idxs] = True
		return idxs
	def release(self, idxs):
		self.free_idxs.extend(idxs)
		self.active[idxs] = False
	def set(self, key,value, idxs=None):
		try:
			return set_arr(self.data[key], value, idxs)
		except:
			key,i = parse_xyz(key)
			return set_arr(self.data[key][i], value, idxs)

	def get(self, key, idxs=None):
		try:
			return get_arr(self.data[key], idxs)
		except:
			key,i = parse_xyz(key)
			return get_arr(self.data[key][i], idxs)
	#-----
	#if self.fixed
	def get_active_idxs(self):
		"1M, 2.5ms"
		return make_idxs(self.active)
	#-----
	#tiny randoms
	def rand(self):
		return make_rand(len(self))
	def randn(self):
		return make_randn(len(self))
	def randint(self, a,b=None):
		return make_randint(len(self), a,b)



def main():
	#how 7,7,7 to 3,1?
	dd = {'hp':10,'mp':5,'pos':(7,7,7)}
	ua = UnitArray( dd)
	print(ua.default)

	ua.set('posx', 3)
	print(ua.get('posx') )
	ua.set('posx', [6,7,8,9,5])
	print(ua.get('posx') )
	ua.set('hp' ,ua.randint(1,55) )
	print(ua)
	x = ua.acquire(hp=99)
	x = ua.acquire(2)
	x = ua.acquire(3, mp=[11,12,13])
	x = ua.acquire(2, pos=(3,4,3) )
	x = ua.acquire(2, pos=([11,22],[33,44],[55,66]) )
	ua.release([3])
	ua.release([1,5])
	print(x)
	print(ua)
	#print(ua.active)

	ua = UnitArray(dd)
	ua.set('hp',[5])
	ua.set('mp',[2])
	ua.set('hp',3)
	ua.set('mp',4)
	ua.set('hp',[5],[2])
	ua.set('mp',[2],[2])
	ua.set('hp',3,[2])
	ua.set('mp',4,[2])
	#us.set('posx', [2] )

	ua.set('pos',(1,2,3) )
	ua.set('pos',([1],[2],[3]))
	ua.set('pos',([11],[22],[33]) ,[3])
	print(ua)

	ua.set('hp',[1,2,3,4,5])
	print(ua.get('hp',[1,3,4]) )


if __name__ == '__main__':
	main()