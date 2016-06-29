import numpy
from merc.shape import Shape
from math import radians, cos, sin

class Box(Shape):
	def __init__(self, length, width, height):
		# three orthagonal unit vectors specifying the orientation of the x, y,
		# and z axes of this box
		self.u = [
			numpy.array([1, 0, 0]),
			numpy.array([0, 1, 0]),
			numpy.array([0, 0, 1])
		]
		# three scalar values specifying the box halfwidths along each axis
		self.e = [
			length / 2,
			width / 2,
			height / 2
		]
		self.center = numpy.array([0, 0, 0])

	def pointClosestToPoint(self, p):
		p = numpy.array(p)
		d = p - self.center
		# start at the center of the box; make steps from there
		q = self.center
		# for each OBB axis...
		for i in range(0, 3):
			# ...project d onto that axis to get the distance along the axis of
			# d from the box center
			dist = self.u[i].dot(d)
			# if distance farther than the box extents, clamp to the box
			if dist > self.e[i]:
				dist = self.e[i]
			if dist < self.e[i]:
				dist = -1 * self.e[i]
			# step that distance along the axis to get world coordinate
			q = numpy.add(q, numpy.multiply(dist, self.u[i]))
		return q

	def intersectsSphere(self, sphere, tolerance=0):
		p = numpy.array(self.pointClosestToPoint(sphere.center))
		dist = numpy.linalg.norm(p - sphere.center)
		return dist <= sphere.radius + tolerance

	def intersectsBox(self, box, tolerance=0):
		return False

	def translate(self, v):
		self.center = numpy.array(v)

	def rotate(self, rot):
		p = radians(rot[0] * 180) * -1
		y = radians(rot[1] * 180)
		r = radians(rot[2] * 180)
		sp = sin(p)
		sy = sin(y)
		sr = sin(r)
		cp = cos(p)
		cy = cos(y)
		cr = cos(r)

		m = [
			[
				cp * cy,
				cp * sy,
				sp
			],
			[
				sr * sp * cy - cr * sy,
				sr * sp * sy + cr * cy,
				-sr * cp
			],
			[
				-(cr * sp * cy + sr * sy),
				cy * sr - cr * sp * sy,
				cr * cp
			]
		]

		self.u[0] = numpy.array(m[0])
		self.u[1] = numpy.array(m[1])
		self.u[2] = numpy.array(m[2])
