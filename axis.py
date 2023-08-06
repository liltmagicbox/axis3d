import numpy as np

from typing import get_type_hints

#======================= do attrname:attrlen,  keep dt kinds empty. no vec.x / is_funcname is auto-created.
#str.strip.__qualname__  >>> 'str.strip'  while name is just funcname.

def pos_update(pos:3,vel:3,acc:3, dt):
	"4 times < 10. not slice"
	vel += acc*dt
	pos += vel*dt


def rpos_update(rpos:3,rvel:3,racc:3, dt):
	"4 times < 10. not slice"
	rvel += racc*dt
	rpos += rvel*dt


class Axis:
	def __init__(self, attrs = None):
		" since vec requires 3 lines.. 2d."
		if attrs is None:
			attrs = {'id':1}
		attr_len = sum(attrs.values())
		N = 10
		self.attrs = attrs
		self.array = np.zeros( (attr_len, N) , dtype = 'float32')

	def __repr__(self):
		"repr is for programmer. eval(repr(self)).  print/str __str first."
		raise NotImplementedError
	def __str__(self):
		"print == str"
		return f"{self.attrs}\n{self.array.shape},{self.array[:,0]}"
	
	#add_attr returns T/F.
	# def has_attr(self, attr_name):
	# 	return attr_name in self.attrs
		
	def add_attr(self, attr_name, attr_len):
		"return True if adding attr is successful."
		if attr_name in self.attrs:
			return False
		#=========
		self.attrs[attr_name] = attr_len

		new_line = np.zeros( (attr_len, self.N) , dtype = 'float32')  # dtype here. or concatedate..
		self.array = np.concatenate( [ self.array , new_line] )
		return True

	def add_func(self, func):
		"funcname becomes flag."
		# attr_name = func.__name__
		# if self.has_attr(attr_name):
		# 	return
		#=========
		if not self.add_attr( func.__name__ , 1):
			return

		attr_dict = get_type_hints(func)  # (pos:3 , dt) => {pos:3}.
		for key,value in attr_dict.items():
			self.add_attr(key,value)

	@property
	def N(self):
		N = self.array.shape[1]  # [0] is attrs, [1] is items len.
		return N
	
a = Axis()
print(a.N)

a.add_func(pos_update)
#print(a.attrs)
print(a)



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