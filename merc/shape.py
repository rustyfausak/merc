from abc import ABC, abstractmethod

class Shape(ABC):
	def intersects(self, other, tolerance=0):
		from merc.sphere import Sphere
		from merc.box import Box
		if isinstance(other, Sphere):
			return self.intersectsSphere(other, tolerance)
		if isinstance(other, Box):
			return self.intersectsBox(other, tolerance)
		raise ValueError("Cannot determine intersection of shape type", type(other))

	@abstractmethod
	def intersectsSphere(self, sphere, tolerance=0):
		pass

	@abstractmethod
	def intersectsBox(self, box, tolerance=0):
		pass
