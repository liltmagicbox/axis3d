from gunfire_unit import UnitArray
from collections import defaultdict

ARRAY_WHOLE_THRES = 100_000

class UnitDict:
	def __init__(self, attr_dict, n=None):
		self.default = attr_dict.copy()
		self.data = attr_dict.copy()
	def __len__(self):
		return len(self.data)
	def set(self, key,value, idxs=None):
		if idxs is None:
			idxs = self.data.keys()
		for idx in idxs:
			self.data[idx][key] = value

	def get(self, key, idxs=None):
		return self.data[key]
	def acquire(self, n=1, **kwargs):

		return idxs
	def release(self, idxs):
		for idx in idxs:
			self.data.pop(idx)
	def rand(self):
		return random.random()
	def randn(self):
		return random.randn()
	def randint(self, a,b=None):
		return random.randint(a,b)



class LinkedUnitArray:
	def __init__(self, attr_dict, n=None):
		self.default = attr_dict.copy()
		ua = UnitArray(attr_dict,n)
		self.uamap = {ua:ua}

	def acquire(self, n=1, whole=False, **kwargs):
		if whole:
			attr_dict = self.default.copy()
			attr_dict.update(kwargs)
			ua = UnitArray( attr_dict, n)
			ua.destroy = lambda s:self.
			self.uamap[ua] = ua
			return Unit(ua)
		#---
		try:
			ua = self.uamap[0]
			idxs = ua.acquire(n)
		except OverflowError:
			ua = UnitArray( self.data )
			self.uamap.insert(0, ua)
			idxs = ua.acquire(n)
		finally:
			return Unit(ua, idxs)

	def release(self, idxs):
		ua,idxs = idxs
		if idxs is None:
			self.uamap.pop(ua)
		else:
			self.uamap[ua].release(idxs)

#===================================
#attrs?
class Unit:
	def __init__(self, unit_array, idxs=None):
		object.__setattr__(self, '_data', unit_array)
		object.__setattr__(self, '_idxs', idxs)
	def __setattr__(self, key,value):
		if key not in self._data.default:raise KeyError
		self._data.set(key,value, self._idxs)
	def __getattr__(self, key):
		return self._data.get(key, self._idxs)
	def __del__(self):
		self._data.release(self._idxs)
	#----
	def rand(self):
		return self._data.rand()
	def randn(self):
		return self._data.randn()
	def randint(self, a,b=None):
		return self._data.randint(a,b)
	#====
	def execute(self, function, *args, **kwargs):
		function(self, *args, **kwargs)

class UnitFactory:
	def __init__(self, units_cls = UnitArray):
		self.units_cls = units_cls
		#--
		self.data[name] = {}
		self.behavior[name] = {}
		self.units[name] = {}
	def set(self, name, data, behavior):
		self.data[name] = data
		self.behavior[name] = behavior
		self.units[name] = self.units_cls(data)

	def order(self, name, n=1, whole=False):
		ua = self.units[name]
		try:
			idxs = ua.acquire(n,whole, **kwargs)
		except TypeError:
			idxs = ua.acquire(n, **kwargs)
		return Unit(ua,idxs)



a = Unit( UnitDict({'pos':3}) )
a.pos=4
print(a.pos)

exit()
