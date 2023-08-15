from abc import ABC, abstractmethod

class WindowInterface(ABC):
	@abstractmethod
	def set_title(self):
		1
	@abstractmethod
	def set_icon(self):
		1
	@abstractmethod
	def set_size(self):
		1
	@abstractmethod
	def set_fullscreen(self):
		1
	@abstractmethod
	def set_top(self):
		1
	@abstractmethod
	def set_mouselock(self):
		1
	
	@abstractmethod
	def bind_key(self):
		1
	@abstractmethod
	def bind_mouse(self):
		1
	@abstractmethod
	def bind_mousebutton(self):
		1
	@abstractmethod
	def bind_filedrop(self):
		1
	
	@abstractmethod
	def run(self):
		1
	@abstractmethod
	def close(self):
		1
	
	@abstractmethod
	def process_input(self):
		1
	@abstractmethod
	def update(self):
		1
	@abstractmethod
	def draw(self):
		1
	

class MaterialInterface(ABC):
	@abstractmethod
	def bind(self):
		1
	@abstractmethod
	def set_mat4(self):
		1
	@abstractmethod
	def set_uniform1(self):
		1
		


class GeometryInterface(ABC):
	@abstractmethod
	def bind(self):
		1
	@abstractmethod
	def draw(self):
		1
	@abstractmethod
	def draw_instanced(self):
		1
	@abstractmethod
	def update(self):
		1


#a = Window()
#a.rox()
