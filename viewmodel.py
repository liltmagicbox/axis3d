
class ViewModel:
	def __init__(self):
		self.tables = {}
	def update(self, data):
		1
	def get_tables(self):
		for table in self.tables.values():
			yield table

