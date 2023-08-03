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
		last_idx = 0
		attrs = {}
		for key,value in attr_dict.items():
			a = last_idx
			b = a+value
			#print(last_idx,key, a,b)
			attrs[key] = slice(a,b)
			last_idx += value
		#===make slicer

		self.data = data
		self.attrs = attrs


	#=============
	def update(self, dt):
		vel = self._get_idx('vel')
		acc = self._get_idx('acc')
		self.data[vel] += self.data[acc] * dt

	def __getitem__(self, key):
		idx = self._get_idx(key)
		return self.data[idx]
	def __setitem__(self, key, value):
		idx = self._get_idx(key)
		self.data[idx] = value
	#=============
	def _get_idx(self, attr):
		if '.' in attr:#assume .x,.y,.z
			attr, axis = attr.split('.')
			start = self.attrs[attr].start
			if axis == 'x':
				return start
			elif axis == 'y':
				return start+1
			elif axis == 'z':
				return start+2
		return self.attrs[attr]#is slicer

		# #if attr in self.attrs:
		# else:
		# 	rai
	def get(self, id, attr=None):
		"id,ids"
		if attr is None:
			idx = slice(0,999)
		else:
			idx = self._get_idx(attr)			
		return self.data[idx,id]

	def set(self, id, attr, value):
		"set a value to id,ids, but not ids->values !"
		idx = self._get_idx(attr)
		self.data[idx, id] = value
		# try:
		# 	self.data[idx, id] = value
		# except ValueError:
		# 	for idx,i in enumerate(value):
		# 		self.data[idx, id][idx] = i
		# print(self.data[idx, id], self.data[idx, id].shape,'done')

	# def get(self, filter_idxs):
	# 	item_line = np.take(self.data, filter_idxs, axis=1)#a=1 for all attrs.
	# 	return item_line
	
	#https://numpy.org/doc/stable/reference/generated/numpy.place.html
	# def set2(self, ids, attr, values):
	# 	#aa = np.array(id)
	# 	#aa.reshape(-1,1)
	# 	print(id)
	# 	idx = self._get_idx(attr)
	# 	#np.put_along_axis(self.data, ids, value, axis=1)
	# 	a[:,3] = 3

	# 	"set value, by id(s) , to attr."
	# 	slicer = self.get_idx(attr)
	# 	print(self.data[slicer,idx])
	# 	self.data[slicer,idx] = value
	# 	print(self.data[slicer,idx])


	# #=============
	
	# def _get(self, key):
	# 	keytype = type(key)
		
	# 	if keytype == tuple:
	# 		attr, slicer = key
	# 		#print(attr, slicer, type(attr))
	# 		#print(self[attr],'got data')
	# 		#x[:,15:19]
	# 		return self[attr][:, slicer] #got data , get all, but slicer a:b.

	# 	elif keytype == slice:#assume attrs slicing..
	# 		return self.data[key]
		
	# 	elif keytype == str:
	# 		idx = self.get_idx(key)
	# 		return self.data[idx]

	# # def add(self, )
	# def __setitem__(self, key, value):
	# 	print(key, value)
	# 	idx = self.get_idx(key)
	# 	self.data[idx] = value

	# 	x = self._get(key)
	# 	print(x,'goiegjo',key)
	# 	x = self[key]

def test_update():
	data = Axisdata()
	data.set([1,2,3,4,5,6,7], 'acc.y', 9.8)
	data['vel'] += data['acc']*0.1
	print('==========')

	print(data.get([1,2,3,4,5], 'vel'), 'heah')

	print('==========')

	data.update(0.1)

	print('==========')

	print(data.get([1,2,3,4,5], 'vel'))

	print('==========')
	exit()

def test_more_simple_getset():

	data = Axisdata()
	x = data.get(5,'pos')
	x = data.get([5,6,7],'pos')
	x = data.get(5)
	print(x)
	print('=====')

	data.set(5,'pos', (1,1,1) )
	data.set(6,'vel', (1,1,1) )
	data.set(7,'acc', (1,1,1) )
	#data.set(slice(0,3),'pos', (2,2,2) )
	data.set([8,10,12],'pos', (7,7,7) )
	print(data.data)


	data.set(3, 'id', 6)
	data.set(5, 'id', 5)
	data.set( [0,1,2], 'id', 4)
	print(data.data)
	print(data.get(6),'nowworkks')

	#data['acc'] = (0,-9.8, 0)
	data.set( 6,'acc' ,  (0,-9.8, 0) )
	print(data.get(6),'nowworkks')

	#data.set( [1,2,3,4,5],'acc' ,  (0,-9.8, 0) ) #we cant.
	data.set( [1,2,3,4,5],'acc.y' ,  -9.8 ) #we cant.

	# for i in [1,2,3,4,5]:
	# 	data.set(i ,'acc' ,  (0,-9.8, 0) ) #we cant.
	print(data.data)

	# data['id', 6:15] = 777
	# print(data['id'],'ho')

	# print('===============')

	# data['id'] = [1,2,3,4]
	# #https://stackoverflow.com/questions/13736718/how-to-make-python-class-support-item-assignment
	# print(data['id'],'id')
	# x = data.get(5)
	# print(x,'nux')





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

