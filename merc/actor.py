import numpy

class Actor:
	def __init__(self, data):
		self.__dict__ = data
		self.last_rb = None

	def update(self, data):
		self.last_rb = self.getProp('TAGame.RBActor_TA:ReplicatedRBState')
		self.__dict__.update(data)

	def isBall(self):
		return self.Class == 'TAGame.Ball_TA'

	def isCar(self):
		return self.Class == 'TAGame.Car_TA'

	def isPRI(self):
		return self.Class == 'TAGame.PRI_TA'

	def isCollidable(self):
		return self.isBall() or self.isCar()

	def hasProp(self, name):
		return hasattr(self, name)

	def getProp(self, name, default=None):
		if not self.hasProp(name):
			return default
		prop = self.__dict__.get(name)
		if not prop:
			return default
		return prop['Value']

	def getTravel(self):
		rb = self.getProp('TAGame.RBActor_TA:ReplicatedRBState')
		if not rb:
			return 0
		last_rb = self.last_rb
		if not last_rb:
			return 0
		p1 = numpy.array(rb['Position'])
		p2 = numpy.array(last_rb['Position'])
		return numpy.linalg.norm(p1 - p2)
