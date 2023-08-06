import numpy as np

from typing import get_type_hints

#======================= do attrname:attr_len,  keep dt kinds empty. no vec.x / is_funcname is auto-created.
#str.strip.__qualname__  >>> 'str.strip'  while name is just funcname.

def pos_update(pos:3,vel:3,acc:3, dt):
	"4 times < 10. not slice"
	vel += acc*dt
	pos += vel*dt


def rpos_update(rpos:3,rvel:3,racc:3, dt):
	"4 times < 10. not slice"
	rvel += racc*dt
	rpos += rvel*dt

N = 10
DTYPE = 'float32'

class Axis:
	def __init__(self):
		" since vec requires 3 lines.. 2d."
		self.attrs = {'id':slice(0,1)}  # for internal usually..but opened.
		attr_len = 1 #sum(attrs.values())
		self.array = np.zeros( (attr_len, N) , dtype = DTYPE)
		self.funcs = []


	def __repr__(self):
		"repr is for programmer. eval(repr(self)).  print/str __str first."
		raise NotImplementedError
	def __str__(self):
		"print == str."
		attrs = { k: (v.stop-v.start) for k,v in self.attrs.items()}
		return f"{attrs}\n{self.array.shape},{self.array[:,0]}"
		
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

		new_line = np.zeros( (attr_len, self.N) , dtype = DTYPE)  # dtype here. or concatedate..
		self.array = np.concatenate( [ self.array , new_line] )
		return True

	
	def add_func(self, func):
		"funcname becomes flag."
		if not self.add_attr( func.__name__ , 1):
			return
		#========
		attr_dict = get_type_hints(func)  # (pos:3 , dt) => {pos:3}.
		for key,value in attr_dict.items():
			self.add_attr(key,value)

		self.funcs.append(func)
	
	#===========================

	def update(self,dt):
		for func in self.funcs:
			kwargs = {'dt':dt}
			for varname in func.__code__.co_varnames:
				if varname == 'dt':
					continue
				slicer = self.attrs[varname]
				attr = self.array[slicer]
				kwargs[varname] = attr
			print('running', func)
			for i in [ f"{k} : {v}"for k,v in kwargs.items()]:
				print(i)
			func(**kwargs)


	#=====
	def set(self, attr, value):
		#test 3 lines:
		#value = 3
		#value = [1,2,3]
		#value = [[1],[2],[3]]

		slicer = self.attrs[attr]
		#we've done, great thing!
		try:
			self.array[slicer] = value
		except ValueError:
			self.array[slicer] = [ (i,) for i in value]

	def get(self, attr):
		"should be copy of the array.."
		slicer = self.attrs[attr]
		return self.array[slicer]



#or locals().keys()
#func.__code__
#def ma(a,b):print(a,b)
# ma.__code__.co_names
# ('print',)
# >>> ma.__code__.co_name
# 'ma'
# >>> ma.__code__.co_nlocals
# 2
# >>> ma.__code__.co_flags
# 67
# >>> ma.__code__.co_filename
# '<stdin>'
# >>> ma.__code__.co_argcount
# 2
# >>> ma.__code__.co_cellvars
# ()
# >>> ma.__code__.co_code
# b't\x00|\x00|\x01\x83\x02\x01\x00d\x00S\x00'
# >>> ma.__code__.co_consts
# (None,)
# >>> ma.__code__.co_lines
# <built-in method co_lines of code object at 0x0000020D3D3AFCB0>
# >>> ma.__code__.co_freevars
# ()
# >>> ma.__code__.co_varnames
# ('a', 'b')
# >>>

	
a = Axis()
print(a.N)

a.add_func(pos_update)

#print(a.attrs)

print(a)
#a.set('acc',1)
#a.set('acc.x',1)
a.set('acc', (0.1, 9.8, 0.1) )
a.update(0.1)
#print(a.array)


"""remnant

#https://docs.python.org/3/library/typing.html

# class vec:
# 	attrs = ('x','y','z')
# class quat:
	# attrs = ('w','x','y','z')

#from typing import NewType
#vec = NewType('vec', float)

#def pos_update(pos:3,vel:3,acc:1, dt:1): dt set attr,,
#def pos_update(pos:3,vel:3,acc:1, dt): now dt skip.
#def pos_update(pos:'xyz',vel:'xyz',acc:'xyz', dt):  #now 3-> xyz, dot access.
#def pos_update(pos:vec,vel:vec,acc:vec, is_pos_update:bool, dt):  #now 3-> xyz, dot access.
#def pos_update(pos:vec,vel:vec,acc:vec, dt):  #now 3-> xyz, dot access. ... no! we dont dot access for vec.
#simple is best

#bad. even Axis.attrs['pos'] = 'xyz'
# attr_dict = {
# 	'pos': 'xyz',
# 	'vel': 'xyz',
# 	'acc': 'xyz',

# 	'rpos': 'xyz',
# 	'rvel': 'xyz',
# 	'racc': 'xyz',
	
# 	'quat': 'wxyz',	
# }






"""