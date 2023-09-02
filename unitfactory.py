from gunfire_unit import UnitArray


class UnitDict:
	def __init__(self, attr_dict, n=1):
		self.default = attr_dict.copy()
		self.data = {}
		self.counter = 0
		idxs = self.acquire(n)
	def set(self, key,value, idxs=None):
		if idxs is None:
			idxs = self.data.keys()

		try:
			if len(value) == len(idxs):
				for i, idx in enumerate(idxs):
					self.data[idx][key] = value[i]
			else:
				raise ValueError(f'value len not matching: {len(value)}, expected:{len(idxs)}')
		except TypeError:
			for idx in idxs:
				self.data[idx][key] = value

	def get(self, key, idxs=None):
		if idxs is None:
			idxs = self.data.keys()
		return [ self.data[idx][key] for idx in idxs]

	def acquire(self, n=1, **kwargs):
		if n == 1:
			attr_dict = self.default.copy()
			attr_dict.update(kwargs)
			self.counter+=1
			self.data[self.counter] = attr_dict
			return [self.counter]
		else:
			attr_dict = self.default.copy()
			long_dict = {}
			for key,value in kwargs.items():
				try:
					if len(value) == n:
						long_dict[key] = value
				except TypeError:
					attr_dict[key] = value
			#================
			idxs = []
			for i in range(n):
				new_dict = attr_dict.copy()
				for key,value in long_dict.items():
					new_dict[key] = value[i]
				self.counter+=1
				self.data[self.counter] = new_dict
				idxs.append(self.counter)
			return idxs

	def release(self, idxs):
		for idx in idxs:
			self.data.pop(idx)

	def __len__(self):
		return len(self.data)
	def rand(self):
		return [random.random() for i in range(len(self))]
	def randn(self):
		return [random.randn() for i in range(len(self))]
	def randint(self, a,b=None):
		return [random.randint(a,b) for i in range(len(self))]



#===================================
#attrs?
class Unit:
	def __init__(self, unit_array, idxs=None, behavior=None ):
		object.__setattr__(self, '_data', unit_array)
		object.__setattr__(self, '_idxs', idxs)
		object.__setattr__(self, 'behavior', behavior)
		object.__setattr__(self, 'attrs', tuple(unit_array.default.keys()) )
	def __setattr__(self, key,value):
		self._data.set(key,value, self._idxs)
	def __getattr__(self, key):
		return self._data.get(key, self._idxs)
	def __del__(self):
		if self._idxs:
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
	def update(self,dt):
		if self.behavior is None:return
		for func in self.behavior:
			self.execute(func,dt)

class UnitFactory:
	def __init__(self):
		self.data = {}
		self.behavior = {}
		self.units = {}
		self.unit = {}
	def set(self, name, data, behavior=None, array = True):
		self.data[name] = data
		self.behavior[name] = behavior
		if array:
			ua = UnitArray(data)
		else:
			ua = UnitDict(data)
		self.units[name] = ua
		self.unit[name] = Unit(ua, behavior)
		#--
	def order(self, name, n=1, whole=False, **kwargs):
		if whole:
			ua = UnitArray( self.data[name] , n)
			idxs = ua.acquire(n, **kwargs)#to activate.
			return Unit(ua, behavior = self.behavior[name])  #update itself!
		ua = self.units[name]
		idxs = ua.acquire(n, **kwargs)
		return Unit(ua,idxs)

	def update(self,dt):
		for name, behavior in self.behavior.items():
			unit = self.unit[name]
			for func in be:
				unit.execute(func,dt)







#========================================
def minitest():
	a = Unit( UnitDict({'pos':3},7) )
	a = Unit( UnitArray({'pos':3},7) )
	a.pos=[i for i in range(7)]
	print(a.pos)

def main():
	minitest()

if __name__ == '__main__':
	main()