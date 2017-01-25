from merc.box import Box
from merc.car import Car
from merc.sphere import Sphere
from merc.collision import Collision

import numpy

class Actor:
	def __init__(self, id, data):
		self.__dict__ = data
		self.id = id
		self.last_update = 0
		self.last_rb_update = 0

	def update(self, data, frame_number):
		self.last_update = frame_number
		if 'TAGame.RBActor_TA:ReplicatedRBState' in data.keys():
			self.last_rb_update = frame_number
		self.__dict__.update(data)

	def getName(self):
		if self.isClass('TAGame.Car_TA'):
			if hasattr(self, 'pri'):
				return self.pri.getProp('Engine.PlayerReplicationInfo:PlayerName', self.Class)
		return self.Class

	def getRB(self, frame_number=-1, tween=0, tweens=0):
		rb_prop = self.getProp('TAGame.RBActor_TA:ReplicatedRBState')
		if not rb_prop:
			return None
		rb = {
			'Position': numpy.array(rb_prop['Position']),
			'Rotation': numpy.array(rb_prop['Rotation'])
		}
		since_rb_update = 0
		if frame_number > 0 and self.last_rb_update > 0:
			since_rb_update = frame_number - self.last_rb_update
		if tweens > 0:
			scale = (0.0045 * (tween / tweens + since_rb_update))
			v = rb_prop['LinearVelocity']
			if not v:
				return rb
			v = numpy.array(v) * scale
			rb['Position'] = numpy.add(rb['Position'], v)
		return rb

	def getShape(self, frame_number=-1, tween=0, tweens=0):
		rb = self.getRB(frame_number, tween, tweens)
		if not rb:
			return None
		if self.isClass('TAGame.Car_TA'):
			if not hasattr(self, 'pri'):
				return None
			loadout_prop = self.pri.getProp('TAGame.PRI_TA:ClientLoadout')
			car = Car(loadout_prop['Body']['Name'])
			box = car.getBox()
			box.rotate(rb['Rotation'])
			box.translate(rb['Position'])
			return box
		elif self.isClass('TAGame.Ball_TA'):
			return Sphere(numpy.array(rb['Position']), Collision.BALL_RADIUS)
		return None

	def getPlayerId(self):
		if not hasattr(self, 'pri'):
			return None
		return self.pri.getProp('Engine.PlayerReplicationInfo:PlayerID')

	def isClass(self, name):
		return self.Class == name

	def getClass(self):
		return self.Class

	def hasProp(self, name):
		return hasattr(self, name)

	def getProp(self, name, default=None):
		if not self.hasProp(name):
			return default
		prop = self.__dict__.get(name)
		if not prop:
			return default
		return prop['Value']
