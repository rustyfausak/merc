import numpy

class Actor:
	def __init__(self, data):
		self.__dict__ = data

	def update(self, data):
		self.__dict__.update(data)

	def isBall(self):
		return self.Class == 'TAGame.Ball_TA'

	def isCar(self):
		return self.Class == 'TAGame.Car_TA'

	def isPRI(self):
		return self.Class == 'TAGame.PRI_TA'

	def isCollidable(self):
		return self.isBall() or self.isCar()

	def hasProp(self, prop):
		return hasattr(self, prop)

	def getProp(self, prop, default=None):
		if not self.hasProp(prop):
			return default
		return self.__dict__.get(prop)['Value']
