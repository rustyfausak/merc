import numpy
from merc.shape import Shape

class Sphere(Shape):
	def __init__(self, center, radius):
		self.center = center
		self.radius = radius

	def intersectsSphere(self, sphere, tolerance=0):
		p1 = numpy.array(self.center)
		p2 = numpy.array(sphere.center)
		dist = numpy.linalg.norm(p1 - p2)
		return dist <= self.radius + sphere.radius + tolerance

	def intersectsBox(self, box, tolerance=0):
		return box.intersectsSphere(self, tolerance)
