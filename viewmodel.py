
class ViewModel:
	def __init__(self):
		self.tables = {}
	def update(self, data):
		header,bdata = data
		shape,attrs, *rest = header
		#focused?

	def get_tables(self):
		yield from [ViewTable()]
		for table in self.tables.values():
			yield table


class ViewTable:
	def get_meshid(self):
		return '00010001'

	def get_uniforms(self):
		1
	def get_Models(self):
		"individual or for instanced, as wish."
		model = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
		return [model]
