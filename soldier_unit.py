#oop -> axis enlist.
from abc import ABC, abstractmethod
import numpy as np
from collections import defaultdict
from typing import get_type_hints
#def fun(position:Vec3, mass:float, dt:float):1
#key_type_map = get_type_hints(fun)


def load_txt(txt_dir):
	try:
		with open(txt_dir, 'r', encoding = 'utf-8') as f:
			lines = f.readlines()
	except:
		with open(txt_dir, 'r', encoding = 'cp949') as f:
			lines = f.readlines()
	data_dict = {}
	for line in lines:
		x = line.strip()
		key,value = x.split(':')
		try:
			value = float(value)
		except:
			pass
		data_dict[key] = value
	return data_dict

def save_txt(txt_dir, data_dict):
	with open(txt_dir, 'w', encoding = 'utf-8') as f:
		for key,value in data_dict.items():
			line = f"{key}:{value}\n"
			f.write(line)

class TxtLoader:
	"holding loaded-txt."
	def __init__(self):
		self._data_dict = {}
	def load(self, txt_dir):
		try:
			return self._data_dict[txt_dir]
		except KeyError:
			d = load_txt(txt_dir)
			self._data_dict[txt_dir] = d
			return d

def test_text():
	ddict = {'hp':5,'power':3} #no str name
	save_txt('ham.txt', ddict)
	d = load_txt('ham.txt')
	print(d)



class Unit:
	def __init__(self):
		#self._data = {}
		object.__setattr__(self, '_data',{})
	def _update(self, ddata):
		self._data.update(ddata)
	def __getattr__(self, key):
		return self._data[key]
	def __setattr__(self , key,value):
		self._data[key] = value
	@classmethod
	def from_array(cls,attr_names,array):
		unit = cls()
		ddata = {k:v for k,v in zip(attr_names,array) }
		unit._update(ddata)
		return unit
	@property
	def attrs(self):
		return self._data
	
def test_unit():
	u = Unit()
	u.pos=3
	print(u.pos)

	u = Unit.from_array(['a','b','pos'], [1,2,3])
	print(u.a,u.b,u.pos)


class Units_Interface(ABC):
	@abstractmethod
	def __init__(self):
		pass
	@abstractmethod
	def __iter__(self):
		"not for units[0]"
	@abstractmethod
	def add(self, unit):
		pass
	@abstractmethod
	def remove(self, unit_id):
		"try to do so."
	@abstractmethod
	def clear(self):
		pass
	@abstractmethod
	def get(self, unit_id):
		"returns None if not exists."
	#===========
	@abstractmethod
	def execute(self, function, *args, **kwargs):
		"execute function, to all units."


class Units(Units_Interface):
	_unit_counter = 0
	def __init__(self):
		self._units = {}
	def __iter__(self):
		"not for units[0]"
		yield from self._units.values()
	def add(self, unit):
		unit.id = Units._unit_counter
		Units._unit_counter +=1
		self._units[unit.id] = unit
	def remove(self, unit_id):
		"try to do so."
		try:
			self._units.pop(unit_id)
		except:
			pass
	def clear(self):
		self._units.clear()
	def get(self, unit_id):
		"returns None if not exists."
		return self._units.get(unit_id)
	#===========
	def execute(self, function, *args, **kwargs):
		"execute function, to all units."
		for unit in self._units.values():
			function(unit, *args, **kwargs)

def test_units():
	uu = Units()
	uu.add( Unit())
	uu.add( Unit())
	uu.remove(0)
	for i in uu:
		print(i)
	print(uu.get(1))
	print(uu.get(0))
	uu.clear()

def test_execute():
	uu = Units()
	uu.add(Unit())
	uu.add(Unit())
	uu.execute( print, 0.3)
	for i in uu:
		i.pos = 0
	def update(self,dt):
		self.pos += dt
	uu.execute( update, 0.1)
	uu.execute( update, 0.1)
	uu.execute( lambda x:print(x.pos) )

	# not this brittle numpy way.. use self, that has arr, so fast like light.
	# def update_pos(pos,dt):
	# 	pos += dt
	# uu.execute( update_pos, uu.pos,0.3 )
	# uu.execute( update_pos, 'pos' , 0.3 )



class UnitArray:
	"there is no unit, but in-out.   / float only. use oop instead,if wanted."
	_unit_counter = 0
	_fresh_idx = []
	def __init__(self, default_attrs):
		self._defaults = default_attrs

		#===set idxmap
		idx_map = {'id':slice(0,1)}
		begin = 1
		for key,value in default_attrs.items():
			try:
				#if len(value) == 3: #tuple list , len(vec())->returning 3..
				length = len(value)
			except:
				float(value)
				length = 1

			end = begin + length
			idx_map[key] = slice(begin, end)
			begin = end
		self._attr_map = idx_map

		#===make array
		#attrs = len(default_attrs)+1
		attrs = end
		n = 5
		#self._fresh_idx = [i for i in range(n)]
		self._fresh_idx = [i for i in range(n-1,-1,-1)] #reversed 4,3,2,1,0
		self._arr = np.zeros( (attrs,n) ).astype('float32')
		self._id_map = {}

	def __len__(self):
		return self._arr.shape[1]
	def __getattr__(self, key):
		idx = self._idx(key)
		return self._arr[idx]
	@property
	def attrs(self):
		return self._defaults
	def _idx(self, key):
		return self._attr_map[key]

	def __iter__(self):
		"extreamly heavy. for convinience only!"
		#for i in range( self._arr.shape[1]):
		for i in self._id_map.values():
			yield self._get_unit(i)
	def _get_unit(self,i):
		x = self._arr[:,i]
		return Unit.from_array( self._defaults, x)

	def _extend(self , n=0):
		"extends the array. n= 50%. "
		stacks, current_n = self._arr.shape
		if n==0:
			n = int(current_n * 0.5)
		new = np.zeros( (stacks,n) ).astype('float32')
		self._arr = np.hstack( [self._arr, new] )
		self._fresh_idx.extend( [i for i in range(current_n+n-1, current_n-1, -1)] )
		#print(self._arr, self._fresh_idx)
	

	def _get_fresh_idx(self):
		if len(self._fresh_idx)==0:
			self._extend()
		return self._fresh_idx.pop()
	
	def _get_fresh_id_idx(self):
		new_id = self._unit_counter+1
		
		idx = self._get_fresh_idx()
		self._id_map[new_id] = idx
		self._unit_counter +=1
		return new_id, idx

	def _get_fresh_id_idxs(self,n):
		stacks, current_n = self._arr.shape
		self._extend(n)  #extended, fresh idx++.
		fresh_idxs = [i for i in range(current_n, current_n+n)]
		
		#=================
		new_id = self._unit_counter+1
		new_ids = [i for i in range(new_id , new_id+n)]

		self._id_map.update( { id:idx for id,idx in zip(new_ids,fresh_idxs)} )
		self._fresh_idx = self._fresh_idx[:-n]
		self._unit_counter += n
		return new_ids, fresh_idxs



	def append(self, **kwargs):
		"list-like. slower"
		#self._units[unit.id] = unit
		new_id,idx = self._get_fresh_id_idx()
		
		self._arr[ self._idx('id') ,idx] = new_id
		for key,value in self.attrs.items():
			value = kwargs[key] if key in kwargs else value
			self._arr[ self._idx(key) ,idx] = value

		#x = [ value for key,value in self.attrs.items()]
		#print(self._arr[ 1: ,idx],'view',x)
		#print(self._arr[:,idx])
		return new_id
		#===========================


	def extend(self, n=2, **kwargs):
		#01234 , 5+2, 
		new_ids,fresh_idxs = self._get_fresh_id_idxs(n)

		#set id
		self._arr[ self._idx('id') , fresh_idxs ] = new_ids

		#set other attrs
		for key,value in self.attrs.items():
			value = kwargs[key] if key in kwargs else value
			try:
				self._arr[ self._idx(key) , fresh_idxs] = value
			except ValueError:
				slicer = self._idx(key)
				length = slicer.stop-slicer.start
				value = np.array(value).flatten().reshape(length,-1)
				self._arr[ self._idx(key) , fresh_idxs] = value
				#for idx,i in enumerate(range(slicer.start , slicer.stop)):
					#self._arr[ i , fresh_idxs] = value[idx]
			
		return new_ids

	def add(self, unit):
		"look, it's great."
		self.append(**unit.attrs)
	def remove(self, unit_id):
		try:
			idx = self._id_map.pop(unit_id)
		except:
			return
		self._arr[:,idx] = 0
		self._fresh_idx.append(idx)

	def clear(self):
		for id in list(self._id_map):
			self.remove(id)

	def get(self, unit_id):
		"returns None if not exists."
		idx = self._id_map.get(unit_id)
		if idx is None:
			return None
		return self._get_unit(idx)
	#===========
	def execute(self, function, *args, **kwargs):
		"execute function, to all units."
		function(self, *args, **kwargs)


def test_get():
	a = UnitArray({'king':44,'age':4, 'pos':(1,2,3)})
	a.append()
	print(a.get(3))
	print(a.get(1))


def test_unitarr_ididx():
	a = UnitArray({'king':44,'age':4, 'pos':(1,2,3)})
	a.append() #1
	a.append() #2
	a.remove(1) #-1
	print(a._arr)
	a.extend(3) #2 345
	a.remove(3) #2  45
	a.append() # 2 456
	a.append()# 2 4567
	a.extend(2) # 2 4567 89
	a.remove(9) # 2 4567 8
	a.append()# 2 4567 10
	a.append()# 2 4567 10 11
	a.append()# 2 4567 10 11 12
	a.append()# 2 4567 10 11 12 13
	a.append()# 2 4567 10 11 12 14
	print(a._arr)
	print(a._id_map)

def test_unitarr_appendattr():
	a = UnitArray({'king':44,'age':4, 'pos':(1,2,3)})
	a.append(king=77)
	print(a._arr)
	a.append(age=99)
	print(a._arr)
	a.append(pos=(7,6,5))
	print(a._arr)

def test_unitarr():
	from random import random
	a = UnitArray({'king':44,'age':4, 'pos':(1,2,3)})
	a.extend(n=3, pos=(99,88,77) )
	a.extend(n=5, age = [1,3,4,5,6] , king=(11,22,33,44,55) , pos=[[int(random()*10),int(random()*10),int(random()*10)] for i in range(5)] )
	a.extend( pos=(99,88,77) )
	print(a._arr)

def experiment_extendfast():
	"100ms, x10 faster!"
	from time import perf_counter
	a = UnitArray({'king':44,'age':4, 'pos':(1,2,3)})
	t = perf_counter()
	t = perf_counter()
	a.extend(1000_00)
	print(perf_counter()-t)
	print(len(a))

def experiment_appendslow():
	"1000ms for 100k append."
	from time import perf_counter
	a = UnitArray({'king':44,'age':4, 'pos':(1,2,3)})
	t = perf_counter()
	t = perf_counter()
	for i in range(100000):
		a.append()
	print(perf_counter()-t)





# #doing oop to array..
def test_unitarray():
	uu = UnitArray({'king':44,'age':4, 'pos':(1,2,3)})
	uu.add( Unit())
	uu.add( Unit())
	uu.remove(0)
	for i in uu:
		print(i)
	print(uu.get(1))
	print(uu.get(0))
	uu.clear()


def test_executearray():
	uu = UnitArray({'king':44,'age':4, 'pos':(1,2,3)})
	uu.add(Unit())
	uu.add(Unit())
	uu.execute( print, 0.3)
	#for i in uu:
	#	i.pos = 0
	#not this horrable way!

	def update(self,dt):
		self.pos += dt
	uu.execute( update, 0.1)
	uu.execute( update, 0.1)
	uu.execute( lambda x:print(x.pos) )


def test_loadtxt():
	dd = load_txt('ham.txt')
	ua = UnitArray(dd)
	print(ua.attrs)
	print(len(ua))



class World:
	"map.."




def main():
	for i in list(globals()):
		#print(i,'d')
		if 'test_' in i:
			globals()[i]()
	print('tests done')

if __name__ == '__main__':
	main()

