import numpy as np
from typing import get_type_hints

#=====
N = 10
DTYPE = 'float32'

#=====


def pos_update(pos:3,vel:3,acc:3, dt):
	"4 times < 10. not slice"
	vel += acc*dt
	pos += vel*dt

def rpos_update(rpos:3,rvel:3,racc:3, dt):
	"4 times < 10. not slice"
	rvel += racc*dt
	rpos += rvel*dt


class Axis:
	def __init__(self):
		" since vec requires 3 lines.. 2d."
		self.attrs = {'id':slice(0,1)}  # for internal usually..but opened.
		attr_len = 1 #sum(attrs.values())
		self.array = np.zeros( (attr_len, N) , dtype = DTYPE)
		self.funcs = []
		self.stop = 0
		self.add_attr('rent',1)
	def __repr__(self):
		"repr is for programmer. eval(repr(self)).  print/str __str first."
		raise NotImplementedError
	def __str__(self):
		"print == str."
		def _arrfit(arr):
			a = []
			for j in arr:
				line = [f"{i:.2f}" for i in j]
				a.append(str(line))
			return '\n'.join(a)

		lines = ['---array:']
		for k,v in self.attrs.items():
			fitarr = _arrfit(self.array[v])
			line = f" {k} :{v} \n{fitarr}"
			lines.append(line)
		lines.append('---array fin')
		return '\n'.join(lines)
	

	@property
	def N(self):
		N = self.array.shape[1]  # [0] is attrs, [1] is items len.
		return N

	#=================

	def add_attr(self, attr_name, attr_len):
		"return True if adding attr is successful."
		if attr_name in self.attrs:
			return False
		#========
		#"# [0:2]-> slice(0,2) / slice(start,stop) slice(items_from_begin)"
		start = tuple(self.attrs.values())[-1].stop  # last stop idx
		stop = start + attr_len  # [1:4] len=3.
		self.attrs[attr_name] = slice(start, stop)

		new_line = np.zeros( (attr_len, self.N) , dtype = DTYPE)  # dtype here. or concatenate..
		self.array = np.concatenate( [ self.array , new_line] )
		return True

	
	def add_func(self, func):
		"funcname becomes flag."
		if self.add_attr( func.__name__ , 1):
			slicer = self.attrs[func.__name__]
			#self.array[slicer] = 1  # set default True.
		else:
			return
		#========
		attr_dict = get_type_hints(func)  # (pos:3 , dt) => {pos:3}.
		for key,value in attr_dict.items():
			self.add_attr(key,value)

		self.funcs.append(func)
	
	#===========================

	def update(self,dt):
		"no flag, no screening. just give them all attrs."
		for func in self.funcs:
			var_names = tuple(get_type_hints(func))
			
			kwargs = {'dt':dt}
			for var in var_names:
				if var == 'dt':
					continue
				slicer = self.attrs[var]
				lines = self.array[slicer]
				kwargs[var] = lines
			func(**kwargs)
			
	#=====
	def set(self, attr, value, id_ids=None):
		"set by id, note:ids list py iter, do for <5k. "
		#test 3 lines:
		#value = 3
		#value = [1,2,3]
		#value = [[1],[2],[3]]
		#for only len==3.
		if '.' in attr:
			attr, note = attr.split('.')
			slicer = self.attrs[attr]		
			start = slicer.start
			if note == 'x':
				slicer = slice(start,start+1)
			elif note == 'y':
				slicer = slice(start+1,start+2)
			elif note == 'z':
				slicer = slice(start+2,start+3)
		
		else:
			slicer = self.attrs[attr]

		#=====step 2
		if id_ids is None:
			try:
				self.array[slicer] = value
			except ValueError:
				self.array[slicer] = [ (i,) for i in value]
		else:
			try:
				self.array[slicer,id_ids] = value
			except ValueError:
				self.array[slicer,id_ids] = [ (i,) for i in value]


	def get(self, attr, id_ids=None):
		"should be copy of the array.."
		slicer = self.attrs[attr]
		
		if id_ids is None:
			return self.array[slicer]
		else:
			return self.array[slicer,id_ids]

	#==============
	def getslice(self, n):
		"rent available space"
		start = self.stop
		stop = start+n
		if self.N < stop:
			self.expand(n)
		#===
		self.stop = stop
		slicer = slice(start, stop)
		#self.array[attr,slicer] = 1
		self.set('rent',1, slicer)
		return slicer
	def expand(self, n):
		"when you need bigger n.."
		attr_len , n_origin =  self.array.shape
		array = np.zeros( (attr_len, n) , dtype = DTYPE)
		self.array = np.concatenate([self.array, array],axis=1)


a = Axis()
a.add_func(pos_update)
#a.expand(7)
s = a.getslice(11)
print(a)
print(s)

def test1():	
	a = Axis()
	print(a.N)

	a.add_func(pos_update)
	#print(a.attrs)
	a.set('acc',1)
	a.set('acc.x',1)
	a.set('acc', (0.1, 9.8, 0.1) , [1,2,3,5] )
	a.set('acc', (0.1, 9.8, 0.1) , slice(1,5) )
	a.set('pos', np.random.rand(a.N))
	a.set('pos_update', np.random.rand(a.N)>0.5)

	a.set('pos', np.random.rand(a.N*3).reshape(3,-1) )
	a.set('acc.y', np.random.rand(a.N) )

	x = a.get('pos',slice(3,5))
	print(x)

	a.update(0.1)

	print(a)






TIPS = """
#str.strip.__qualname__  == 'str.strip'  /  __name__  == just funcname.

#var_names = func.__code__.co_varnames  this contains local vars.

"""
