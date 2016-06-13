import numpy

class Actor:
	# the max distance that the ball or player seems to travel in a single frame
	# ive found to be about 200
	MAX_DIST_IN_FRAME = 0

	def __init__(self, data):
		self.__dict__ = data
		self.cache = {}

	def update(self, data):
		if self.isCollidable():
			rbstate = self.getRBState()
			if rbstate:
				self.__dict__['TAGame.RBActor_TA:ReplicatedRBState:prev'] = rbstate
		self.__dict__.update(data)

	def isBall(self):
		return self.Class == 'TAGame.Ball_TA'

	def isPlayer(self):
		return self.Class == 'TAGame.Car_TA'

	def isCollidable(self):
		return self.isBall() or self.isPlayer()

	def getCollisionBubbleRadius(self):
		if self.isBall():
			return self.MAX_DIST_IN_FRAME + 88
		if self.isPlayer():
			# based on a max car size of 130x86x42
			return self.MAX_DIST_IN_FRAME + 91

	def getRBState(self):
		key = 'TAGame.RBActor_TA:ReplicatedRBState'
		if not hasattr(self, key):
			return None
		return self.__dict__.get(key)['Value']

	def getRBStatePrev(self):
		key = 'TAGame.RBActor_TA:ReplicatedRBState:prev'
		if not hasattr(self, key):
			return None
		return self.__dict__.get(key)

	def getTravel(self):
		rbstate = self.getRBState()
		rbstate_prev = self.getRBStatePrev()
		if not rbstate or not rbstate_prev:
			return 0
		p1 = numpy.array(rbstate['Position'])
		p2 = numpy.array(rbstate_prev['Position'])
		return numpy.linalg.norm(p1 - p2)
