from merc.actor import Actor
from merc.collision import Collision
from merc.player import Player
from pprint import pprint
import sys
import numpy
import itertools
from PIL import Image, ImageDraw, ImageColor

class Game:
	NUM_TWEENS = 5

	def __init__(self, data):
		self.__dict__ = data
		self.frame = None
		self.tween = 0
		self.seconds_remaining = 0
		self.actors = {}
		self.players = {}
		self.ball_actor = None
		self.car_actors = []
		self.pri_actors = []

	def processFrames(self):
		for frame in self.Frames:
			for id, data in frame['Spawned'].items():
				self.actors[id] = Actor(id, data)
			for id, data in frame['Updated'].items():
				self.actors[id].update(data)
			self.frame = frame
			self.state()
			self.link()
			self.collisions()
		for player in self.players.values():
			pprint(vars(player))

	def state(self):
		tagame = None
		self.ball_actor = None
		self.car_actors = []
		self.pri_actors = []
		for actor in self.actors.values():
			if actor.isClass('TAGame.GameEvent_Soccar_TA'):
				tagame = actor
				s = tagame.getProp('TAGame.GameEvent_Soccar_TA:SecondsRemaining', -1)
				if s >= 0:
					self.seconds_remaining = s
			elif actor.isClass('TAGame.PRI_TA'):
				self.pri_actors.append(actor)
			elif actor.isClass('TAGame.Ball_TA'):
				self.ball_actor = actor
			elif actor.isClass('TAGame.Car_TA'):
				self.car_actors.append(actor)

	def link(self):
		# link pri -> team
		for pri in self.pri_actors:
			if hasattr(pri, 'team'):
				continue
			team_prop = pri.getProp('Engine.PlayerReplicationInfo:Team')
			if not team_prop:
				continue
			pri.team = self.findActor(team_prop[1])

		# link car -> pri
		for car in self.car_actors:
			if hasattr(car, 'pri'):
				continue
			pri_prop = car.getProp('Engine.Pawn:PlayerReplicationInfo')
			if not pri_prop:
				continue
			car.pri = self.findActor(pri_prop[1])

		# create / update players
		for car in self.car_actors:
			player_id = car.getPlayerId()
			if not player_id:
				continue
			if player_id not in self.players:
				self.players[player_id] = Player(player_id)
			self.players[player_id].update(car)

	def findActor(self, find_actor_id):
		find_actor_id = int(find_actor_id)
		for actor_id, actor in self.actors.items():
			if int(actor_id) == find_actor_id:
				return actor
		return None

	def collisions(self):
		# we only want to check actors that are within Collisions.FRAME_CHECK_RADIUS units of each other
		# we only want to tween if anyone is within Collisions.FRAME_CHECK_RADIUS units

		# create tuples of actors that we want to check this frame
		pairs = []
		ball = self.ball_actor
		for car in self.car_actors:

			# we dont want to check cars that arent associated with players yet
			player_id = car.getPlayerId()
			if not player_id:
				continue
			player = self.players[player_id]

			# check if the last collision with the ball was within a certain number of frames
			# if it is, we should skip this pair for the whole frame
			last_collision = player.getLastCollisionWithActor(ball.id)
			if last_collision and last_collision.frame_number > self.frame['Number'] - Collision.MIN_FRAMES_BETWEEN:
				continue

			# skip if the distance is over the limit
			dist = self.distance(ball, car)
			if not dist:
				continue
			if dist > Collision.FRAME_CHECK_RADIUS:
				continue

			pairs.append((ball, car))

		# only tween if any actors are within the limit
		if len(pairs) > 0:
			self.tween = 0
			# save which actors have been collided
			collided = []
			for i in range(self.NUM_TWEENS + 1):
				for actor1, actor2 in pairs:
					# combine actor ids into a "unique" key for faster lookup
					key = actor1.id + actor2.id * 1024
					if key in collided:
						# dont allow multiple collisions between the same actors per frame
						continue
					check_radius = Collision.CAR_AND_BALL_RADIUS
					if actor1.isClass('TAGame.Car_TA'):
						if actor2.isClass('TAGame.Car_TA'):
							check_radius = Collision.CAR_AND_CAR_RADIUS
						else:
							check_radius = Collision.CAR_AND_BALL_RADIUS
					collision = self.collides(actor1, actor2, check_radius)
					if collision:
						self.handleCollision(actor1, actor2, collision)
						collided.append(key)
				self.tween += 1

	def handleCollision(self, actor1, actor2, collision):
		if (actor1.isClass('TAGame.Car_TA')):
			player_id = actor1.getPlayerId()
			if player_id:
				self.players[player_id].addCollision(collision)
		if (actor2.isClass('TAGame.Car_TA')):
			player_id = actor2.getPlayerId()
			if player_id:
				self.players[player_id].addCollision(collision)
		print(self.seconds_remaining, self.frame['Number'], self.tween, "[{0}] x [{1}]".format(actor1.getName(), actor2.getName()), collision.point)

	def distance(self, actor1, actor2, return_midpoint=False):
		rval = False
		if return_midpoint:
			rval = (False, False)
		rb1 = actor1.getProp('TAGame.RBActor_TA:ReplicatedRBState')
		if not rb1:
			return rval
		rb2 = actor2.getProp('TAGame.RBActor_TA:ReplicatedRBState')
		if not rb2:
			return rval
		p1 = numpy.array(rb1['Position'])
		p2 = numpy.array(rb2['Position'])
		if self.tween > 0:
			scale = (0.0085 * (1 / (self.NUM_TWEENS + 1) * self.tween))
			v1 = rb1['LinearVelocity']
			v2 = rb2['LinearVelocity']
			if not v1:
				return rval
			if not v2:
				return rval
			v1 = numpy.array(v1) * scale
			v2 = numpy.array(v2) * scale
			p1 = numpy.add(p1, v1)
			p2 = numpy.add(p2, v2)
		dist = numpy.linalg.norm(p1 - p2)
		if return_midpoint:
			return (dist, numpy.median([p1, p2], axis=0))
		return dist

	def collides(self, actor1, actor2, check_radius):
		(dist, midpoint) = self.distance(actor1, actor2, True)
		if not dist:
			return False
		if dist > check_radius:
			return False
		return Collision(midpoint, self.frame['Number'], actor1.id, actor2.id)
