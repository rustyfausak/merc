import logging
import numpy
import sys
from PIL import Image, ImageDraw

im_width = 1000
im_height = 250
im = Image.new('RGB', (im_width, im_height), '#ffffff')
draw = ImageDraw.Draw(im)

def imDone():
	im.save("img.png", "PNG")

class Actor:
	@staticmethod
	def spawn(id, data, time, frame_number):
		actor_class = {
			'TAGame.Team_Soccar_TA': Team,
			'TAGame.Car_TA': Car,
			'TAGame.CarComponent_Boost_TA': Boost,
			'TAGame.CarComponent_Jump_TA': Jump,
			'TAGame.CarComponent_DoubleJump_TA': DoubleJump,
			'TAGame.CarComponent_Dodge_TA': Dodge,
			'TAGame.PRI_TA': PRI,
			'TAGame.Ball_TA': Ball,
		}.get(data['Class'], None)
		if not actor_class:
			return None
		return actor_class(id, data, time, frame_number)

	def __init__(self, id, data, time, frame_number):
		self.id = id
		self.time = time
		self.frame_number = frame_number
		self.object_class = data['Name']
		self.object_superclass = data['Class']
		self.create(data)
		self.updated_props = []

	def create(self, data):
		pass

	def destroy(self, time, frame_number):
		pass

	def update(self, data, time, frame_number):
		self.time = time
		self.frame_number = frame_number
		self.updated_props = []
		self._update(data)

	def _update(self, data):
		pass

	def link(self, actors):
		pass

	def updateProp(self, attr, value):
		setattr(self, attr, value)
		self.updated_props.append(attr)

	def __str__(self):
		return "Actor #%s %s (%s)" % (self.id, self.object_class, self.object_superclass)

class Team(Actor):
	def getColor(self):
		if self.object_class == 'Archetypes.Teams.Team0':
			return 'Blue'
		elif self.object_class == 'Archetypes.Teams.Team1':
			return 'Orange'
		return 'UnknownColor'

class PRI(Actor):
	def create(self, data):
		self.exp = None
		self.is_partied = False
		self.ping = None
		self.team_actor_id = None
		self.team_actor = None
		self.car_actor = None
		self.name = None
		self.body = None
		self.unique_id = None
		self.player = None

	def _update(self, data):
		if 'TAGame.PRI_TA:TotalXP' in data:
			self.updateProp('exp', data['TAGame.PRI_TA:TotalXP']['Value'])
		if 'TAGame.PRI_TA:PartyLeader' in data:
			self.updateProp('is_partied', True)
		if 'Engine.PlayerReplicationInfo:Ping' in data:
			self.updateProp('ping', data['Engine.PlayerReplicationInfo:Ping']['Value'])
		if 'Engine.PlayerReplicationInfo:Team' in data:
			self.updateProp('team_actor_id', str(data['Engine.PlayerReplicationInfo:Team']['Value'][1]))
		if 'Engine.PlayerReplicationInfo:PlayerName' in data:
			self.updateProp('name', data['Engine.PlayerReplicationInfo:PlayerName']['Value'])
		if 'TAGame.PRI_TA:ClientLoadout' in data:
			self.updateProp('body', data['TAGame.PRI_TA:ClientLoadout']['Value']['Body']['Name'])
		if 'Engine.PlayerReplicationInfo:UniqueId' in data:
			self.updateProp('unique_id', data['Engine.PlayerReplicationInfo:UniqueId']['Value'])

	def link(self, actors):
		if self.team_actor:
			return
		if not self.team_actor_id:
			return
		if self.team_actor_id not in actors:
			return
		self.team_actor = actors[self.team_actor_id]

class RigidBody(Actor):
	def create(self, data):
		self.frame_delta = 0
		self.time_delta = 0
		self.rb_update_time = self.time
		self.rb_update_frame_number = self.frame_number
		self.position = numpy.array(data['Position'])
		self.rotation = numpy.array(data['Rotation'])
		self.linear_velocity = None
		self.last_linear_velocity = None
		self.lv_arr = []
		self.angular_velocity = None
		self.distance = None

	def _update(self, data):
		if 'TAGame.RBActor_TA:ReplicatedRBState' in data:
			self.time_delta = self.time - self.rb_update_time
			self.frame_delta = self.frame_number - self.rb_update_frame_number
			self.rb_update_time = self.time
			self.rb_update_frame_number = self.frame_number
			self.last_linear_velocity = self.linear_velocity
			position = numpy.array(data['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Position'])
			self.updateProp('distance', numpy.linalg.norm(position - self.position))
			self.updateProp('position', position)
			self.updateProp('rotation', numpy.array(data['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Rotation']))
			if data['TAGame.RBActor_TA:ReplicatedRBState']['Value']['LinearVelocity']:
				lv = numpy.array(data['TAGame.RBActor_TA:ReplicatedRBState']['Value']['LinearVelocity'])
				self.updateProp('linear_velocity', lv)
				self.lv_arr.insert(0, lv)
				self.lv_arr = self.lv_arr[0:4]
			if data['TAGame.RBActor_TA:ReplicatedRBState']['Value']['AngularVelocity']:
				self.updateProp('angular_velocity', numpy.array(data['TAGame.RBActor_TA:ReplicatedRBState']['Value']['AngularVelocity']))
			self.draw()

	def draw(self):
		mag_lv = 0
		if self.last_linear_velocity is not None:
			mag_lv = numpy.linalg.norm(self.last_linear_velocity) / 10
		mag = mag_lv

		pct = 0
		if len(self.lv_arr) > 3:
			prev_lv = self.lv_arr[3]
			prev_mag = numpy.linalg.norm(prev_lv)
			pct = round(prev_mag / 35000 * 100)

		pct = min(100, max(0, int(pct)))
		color = 'rgb(%s%%,0%%,0%%)' % pct
		y = 0
		if self.distance is not None:
			y = round(self.distance)
		x = round(mag / 3500 * im_width)
		y = abs(y - im_height)
		draw.point((x, y), color)

class Car(RigidBody):
	def create(self, data):
		super().create(data)
		self.pri_actor_id = None
		self.pri_actor = None
		self.throttle = 0
		self.is_boosting = False
		self.component_actors = {}

	def _update(self, data):
		super()._update(data)
		if 'Engine.Pawn:PlayerReplicationInfo' in data:
			self.updateProp('pri_actor_id', str(data['Engine.Pawn:PlayerReplicationInfo']['Value'][1]))
		if 'TAGame.Vehicle_TA:ReplicatedThrottle' in data:
			self.updateProp('throttle', max(-100, min(100, round((data['TAGame.Vehicle_TA:ReplicatedThrottle']['Value'] - 128) / 127 * 100))))
		if 'Boost' in self.component_actors:
			self.is_boosting = self.component_actors['Boost'].is_active

	def link(self, actors):
		if self.pri_actor:
			return
		if not self.pri_actor_id:
			return
		if self.pri_actor_id not in actors:
			return
		pri = actors[self.pri_actor_id]
		self.pri_actor = pri
		pri.car_actor = self

class Ball(RigidBody):
	pass

class Component(Actor):
	def create(self, data):
		self.car_actor_id = None
		self.car_actor = None
		self.is_active = False

	def _update(self, data):
		if 'TAGame.CarComponent_TA:Vehicle' in data:
			self.updateProp('car_actor_id', str(data['TAGame.CarComponent_TA:Vehicle']['Value'][1]))
		if 'TAGame.CarComponent_TA:ReplicatedActive' in data:
			self.updateProp('is_active', data['TAGame.CarComponent_TA:ReplicatedActive']['Value'] % 2 == 1)

	def link(self, actors):
		if self.car_actor:
			return
		if not self.car_actor_id:
			return
		if self.car_actor_id not in actors:
			return
		car = actors[self.car_actor_id]
		self.car_actor = car
		car.component_actors[self.__class__.__name__] = self

class Boost(Component):
	def create(self, data):
		super().create(data)
		self.boost_amount = None
		self.boost_added = 0
		self.boost_consumed = 0

	def _update(self, data):
		super()._update(data)
		if 'TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount' in data:
			new_boost_amount = round(data['TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount']['Value'] / 255 * 100)
			if self.boost_amount is not None:
				diff = new_boost_amount - self.boost_amount
				if diff < 0:
					self.updateProp('boost_consumed', abs(diff))
				elif diff > 0:
					self.updateProp('boost_added', diff)
			self.updateProp('boost_amount', new_boost_amount)

class Jump(Component):
	pass

class DoubleJump(Component):
	pass

class Dodge(Component):
	pass
