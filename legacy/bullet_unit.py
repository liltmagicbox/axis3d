import numpy as np

def test_uidmap():
	"is possible, great way. since idxs is extreamly fast, while uid missing.."
	a = np.arange(10)+10
	print(a[ [1,3,0,0,-1] ]) #so safe. let 0 be 'the trash can'.

	#write also available!
	a[ [1,2,3,1]] = 5
	print(a)


def make_idarr(N):
	#note: np.nonzero(cond)-> (1,) i64 is fastest.
	return np.zeros( N ).astype('int64')
	#np.nonzero(np.ones(N)))


def make_arr(rows, N):
	return np.zeros( (rows,N) ).astype('float32')
def stack_arr(arr, new):
	"need sametype"
	return np.hstack( [arr, new] )
def extend_arr(arr, n=0):
	rows, arrlen = arr.shape
	n = int(arrlen*0.5) if n==0 else n
	new = make_arr(rows,n)
	return stack_arr(arr, new)

def get_freeidx_arr(arr):
	cond = arr[0] == 0
	return np.nonzero(cond)




def _make_slicemap(attr_dict):
	idx_map = {'uid':slice(0,1)}
	begin = 1
	for key,value in attr_dict.items():
		try:
			#if len(value) == 3: #tuple list , len(vec())->returning 3..
			length = len(value)
		except:
			float(value)
			length = 1

		end = begin + length
		idx_map[key] = slice(begin, end)
		begin = end


def _parse_kwargs(kwargs):
	"soft copy, parse xyz."
	data = {}
	xyzs = {}
	for key,value in kwargs.items():
		if key.endswith('xyz'):  # posxyz -> pos, posx,posy,posz
			pos = key[:-3]
			
			posx = pos+'x'
			posy = pos+'y'
			posz = pos+'z'
			xyzs[posx] = pos,0
			xyzs[posy] = pos,1
			xyzs[posz] = pos,2

			key = pos
		#finally
		value = list(value) if type(value) == tuple else value
		data[key] = value
		
	return data, xyzs

class Unit:
	"""holding uids, watching uarr. 1 or N viewer of uarr.
	execute, self,getting,looks uarr. great.
	it can act like oop, if len==1.
		dir(unit) to see attrs, methods?
	"""
	def __init__(self, uids, uarr):
		self._uids = uids
		self._uarr = uarr
	def __getattr__(self, key):
		return (self._uarr[self._uids]).get(key)
	def __setattr__(self, key,value):
		(self._uarr[self._uids]).set(key, value)
	#----
	def __len__(self):  # unit.hp = [i for i in range(len(unit))]
		return len(self._uids)
	#def __getitem__(self, idxs): # if need it, use append, instead of extend.
	#----
	def execute(self, function, *args, **kwargs):
		function(self, *args, **kwargs)

class UnitArray:
	def __init__(self, **kwargs):
		default_attr, idx_map = parse_kwargs(kwargs)
		rows = list(idx_map.values())[-1].stop

		self.default = default_attr
		self.idx_map = idx_map
		self._arr = make_arr(rows, 10)
	#----
	def __getitem__(self, idxs):
		return self._arr[:,idxs]
	#===========
	def append(self, *args, **kwargs):
		1
	def extend(self, n, *args, **kwargs):
		1
	#-----------------------
	def execute(self, function, *args, **kwargs):
		function(self, *args, **kwargs)



class Units:
	def __init__(self, **kwargs):
		object.__setattr__(self, '_xyzs', xyzs)
		object.__setattr__(self, '_data', data)

	def __getattr__(self, key):
		if key in self._xyzs:
			key,idx = self._xyzs[key]
			return self._data[key][idx]
		return self._data[key]
	def __setattr__(self , key,value):
		if key in self._xyzs:
			key,idx = self._xyzs[key]
			self._data[key][idx] = value
		elif key in self._data:
			value = list(value) if type(value) == tuple else value
			self._data[key] = value
		else:
			raise KeyError
	
	def __len__(self):
		self._arr
	@property
	def attrs(self):
		return tuple(self._data.keys())




def test_unit():
	dd = {'a':1,'b':2,'posxyz': (1,2,3) }
	u2 = Unit( **dd )
	u2.pos= (3,2,1)
	u2.posx=5
	print(u2.pos, u2.posx, u2.posz)

	dd['a']=4
	print(u2.attrs)
	u2.b=9
	print(u2.attrs)
	print(u2.b)
	u3 = u2.copy()
	u2.a = 8
	print(u2.attrs, u3.attrs)
