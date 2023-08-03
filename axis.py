import numpy as np



""" x,y,z,  rx,ry,rz,  scale, sx,sy,sz
quat is mid-data.
finally MAT. TRS.
and instanced.

 """


class Axisdata:
	def __init__(self, N=20):
		attr_dict = {
			'id':1,
			'pos': 3,
			'vel': 3,
			'acc': 3,
			'changed':1,
		}

		attr_n = sum( attr_dict.values() )
		#N = 20 #objects N.
		# row[0] =id, row[1] = x, row[2] = y...
		# [x1,x2,x3...] for faster access.
		data = np.zeros( attr_n * N , dtype='float32').reshape(attr_n, N)
		#print(data.shape)

		#===make slicer
		last_idx = -1
		attrs = {}
		for key,value in attr_dict.items():
			last_idx += value
			a = last_idx
			b = a+value
			attrs[key] = slice(a,b)
		#===make slicer

		self.data = data
		self.attrs = attrs
	def __getitem__(self, key):
		#print(key)
		#slice(0, 1, None) or (0,1)
		#or (0, slice(0, 1, None))  [0, 0:1]
		#('pos', slice(3, 5, None)) ['pos', 3:5]
		#slice('pos', 'acc', None) wow data['pos':'acc']
		return self._get(key)

	def _get(self, key):
		keytype = type(key)
		
		if keytype == tuple:
			attr, slicer = key
			#print(attr, slicer, type(attr))
			#print(self[attr],'got data')
			#x[:,15:19]
			return self[attr][:, slicer] #got data , get all, but slicer a:b.

		elif keytype == slice:#assume attrs slicing..
			return self.data[key]
		
		elif keytype == str:
			idx = self.get_idx(key)
			return self.data[idx]

	# def add(self, )
	def get(self, filter_idxs):
		item_line = np.take(self.data, filter_idxs, axis=1)#a=1 for all attrs.
		return item_line
	def __setitem__(self, key, value):
		print(key, value)
		idx = self.get_idx(key)
		self.data[idx] = value

		x = self._get(key)
		print(x,'goiegjo',key)
		x = self[key]
	
	def set(self, idx, attr, value):
		"set value, by id(s) , to attr."
		slicer = self.get_idx(attr)
		print(self.data[slicer,idx])
		self.data[slicer,idx] = value
		print(self.data[slicer,idx])

	def get_idx(self, attr):
		if attr in self.attrs:
			idx = self.attrs[attr]
			return idx

data = Axisdata()
data.set(3, 'id', 696)
data.set(5, 'id', 55)
#data.set( [6,15], 'id', 99)

data['id', 6:15] = 777
print(data['id'],'ho')

print('===============')

data['id'] = [1,2,3,4]
#https://stackoverflow.com/questions/13736718/how-to-make-python-class-support-item-assignment
print(data['id'],'id')
x = data.get(5)
print(x,'nux')





def test_nptake_axis1():
	"to get indices selective all ."
	a = (np.arange(18)*2)
	print(a)
	fi = [1,3,5]
	x = a[fi]
	print(x)

	print('========')
	#https://stackoverflow.com/questions/19821425/how-to-filter-numpy-array-by-list-of-indices
	a = (np.arange(18)*2).reshape(3,6)
	print(a)

	#from [[ 0  2  4  6  8 10]
	fi = [1,3,5]
	x = np.take(a, fi)
	print(x)

	print('select allattrs: using axis=1')
	x = np.take(a, fi, axis=1)
	print(x)



def test_axis_getitem():
	data = Axisdata()
	#basic attr access.
	x = data['id']
	print(x)
	#x = data['x']
	#print(x)
	x = data['pos']
	print(x)
	x = data['changed']
	print(x)

	#get some items.. but this not via id... ,.. no, but is id.
	print('=========')
	x = data['pos',3:5]
	print(x)
	#x = data['pos':'acc']
	x = data['pos']
	print(x[:,15:19])

	#get most-all attrs.
	x = data[3:5]
	print(x)

