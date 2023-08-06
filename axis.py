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


#...fianly too bad. we read code lines, yeah.
#no. this is too bad.
#this too complex. don't! func_name and dt delivered automatically using bool flag.
#this is rather not complex, compared with screening.. 
def somewhat_heavy(somewhat_heavy:1, rpos:3,rvel:3,racc:3, dt):
	#case1 dt flag. somewhat_heavy*dt
	#case 2, screening

	N = somewhat_heavy.shape[1]
	if (np.count_nonzero(somewhat_heavy) / N) <0.1: #or 5k?
		screen = somewhat_heavy.astype('bool').flatten()
		
		#====below same structure, hand-copied.
		rvel[:,screen] += racc[:,screen]*dt
		rpos[:,screen] += rvel[:,screen]*dt
		return
	rvel += racc*dt
	rpos += rvel*dt

#print(dir(somewhat_heavy.__code__))
#print(len(somewhat_heavy.__code__.co_code))

def codelineslentest():
	from time import perf_counter

	t = perf_counter()
	for i in range(100000):
		1#len(somewhat_heavy.__code__.co_code)
	print(perf_counter()-t)
	exit()
	#20 vs 34ms
	#py iter 100k, 7ms.




def somewhat_heavy(rpos:3,rvel:3,racc:3, dt):
	print('inpyut', dt, racc)
	rvel += racc*dt
	rpos += rvel*dt
	e=1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1
	d=1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1
	c=1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1
	b=1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1
	a=1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1+1
print(len(somewhat_heavy.__code__.co_code))


N = 12
DTYPE = 'float32'
HEAVYLINES = 47

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
		lines = ['---array:']
		for k,v in self.attrs.items():
			fitarr = self.arrfit(self.array[v])
			line = f" attr {k} :{v} \n{fitarr}"
			lines.append(line)
		lines.append('---array fin')
		return '\n'.join(lines)
	
	@staticmethod
	def arrfit(arr):
		a = []
		for j in arr:
			line = [f"{i:.2f}" for i in j]
			a.append(str(line))
		return '\n'.join(a)

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
		if self.add_attr( func.__name__ , 1):
			slicer = self.attrs[func.__name__]
			self.array[slicer] = 1
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
		N = self.N
		
		for func in self.funcs:
			func_name = func.__name__
			var_names = tuple(get_type_hints(func))
			#var_names = func.__code__.co_varnames

			#flag - lets the func decide - set arg of funcname.  think about dt chaining..
			#slicer = self.attrs[func_name]
			#dt *= self.array[slicer] #0.8ms-2.5ms added. acceptable.
			flag = self.array[self.attrs[func_name]]
			if (len(func.__code__.co_code)>HEAVYLINES) and (np.count_nonzero(flag) / N) <0.5: #or 5k?
				self.update_screen(func, var_names, dt, flag)
			else:
				self.update_all(func, var_names, dt)

	def update_screen(self, func, var_names,dt, flag):
		print('scceee')
		screen = flag.astype('bool').flatten()

		kwargs = {'dt':dt}
		for var in var_names:
			if var == 'dt':
				continue
			slicer = self.attrs[var]
			attr = self.array[slicer,screen] #here copy happens..
			#FAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFA
			#FAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFA
			#FAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFA
			#FAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFA
			#FAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFA
			#FAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFAILFA
			# copy, not += wortking. just func do what it want.
			kwargs[var] = attr
		func(**kwargs)

	def update_all(self, func, var_names, dt):
		kwargs = {'dt':dt}
		for var in var_names:
			if var == 'dt':
				continue
			slicer = self.attrs[var]
			attr = self.array[slicer]
			kwargs[var] = attr
		func(**kwargs)


			

	def _badupdate(self,dt):
		N = self.N
		
		for func in self.funcs:
			func_name = func.__name__
			slicer = self.attrs[func_name]
			flag = self.array[slicer]
			x  = np.count_nonzero(flag)
			screening = x/N < 0.1


			var_names = func.__code__.co_varnames
		
			#then, not write the result.
			if not screening:
				dt *= flag #0.8ms-2.5ms added. acceptable.

			kwargs = {'dt':dt}
			for var in var_names:
				if var == 'dt':
					continue
				slicer = self.attrs[var]
				if screening:
					flag = flag.astype('bool').flatten()
					attr = self.array[slicer, flag]
					print(attr,'att!!!!!!!!!!!!!!!!!!!r',var)
				else:
					attr = self.array[slicer]
				kwargs[var] = attr
			#print('running', func)
			#for i in [ f"{k} : {v}"for k,v in kwargs.items()]:
			#	print(i)
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

#a.set('acc',1)
#a.set('acc.x',1)
#a.set('acc', (0.1, 9.8, 0.1) , [1,2,3,5] )
#a.set('acc', (0.1, 9.8, 0.1) , slice(1,5) )
#a.set('pos', np.random.rand(a.N))
a.set('pos_update', np.random.rand(a.N)>0.9)

a.set('pos', np.random.rand(a.N*3).reshape(3,-1) )
a.set('acc.y', np.random.rand(a.N) )

#x = a.get('pos',slice(3,5))
#print(x)

a.add_func(somewhat_heavy)
a.set('somewhat_heavy', np.random.rand(a.N)>0.5 )
a.set('racc.x', np.random.rand(a.N))

a.update(0.1)

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