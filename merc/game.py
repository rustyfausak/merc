from merc.actor import Actor
from merc.collision import Collision
from merc.player import Player
from pprint import pprint

import sys
import json
import numpy
import itertools
from PIL import Image, ImageDraw, ImageColor

class Game:
	NUM_TWEENS = 10

	def __init__(self, data):
		"""
		`data` should contain the JSON output of Octane
		"""
		self.__dict__ = data
		self.frame = None
		self.tween = 0
		self.seconds_remaining = 0
		self.actors = {}
		self.players = {}
		self.ball_actor = None
		self.grouped_actors = {}

	def processFrames(self):
		"""
		Step through the frames one by one. Build the actors, update the game state,
		link the actors, and generate stats.
		"""
		for frame in self.Frames:
			self.frame = frame
			for id, data in frame['Spawned'].items():
				self.actors[id] = Actor(id, data)
			for id, data in frame['Updated'].items():
				self.actors[id].update(data, self.frame['Number'])
			self.updateState()
			self.linkActors()
			#self.checkCollisions()

	def updateState(self):
		"""
		Update the game state. Creates a sort of cache to help find commonly used stuff.
		"""
		self.ball_actor = None
		self.grouped_actors = {}
		for actor in self.actors.values():
			actor_class = actor.getClass()
			if actor_class == 'TAGame.GameEvent_Soccar_TA':
				# shortcut for the time remaining
				s = actor.getProp('TAGame.GameEvent_Soccar_TA:SecondsRemaining', -1)
				if s >= 0:
					self.seconds_remaining = s
			elif actor_class == 'TAGame.Ball_TA':
				# shortcut to find the ball actor
				self.ball_actor = actor
			else:
				# group similar actors together
				if not actor_class in self.grouped_actors:
					self.grouped_actors[actor_class] = []
				self.grouped_actors[actor_class].append(actor)

	def linkActors(self):
		"""
		Some actors have relationships with each other, so we set those relationships here.
		"""

		'''
		components -> car -> pri -> team
		'''

		# link pri -> team
		if 'TAGame.PRI_TA' in self.grouped_actors:
			for pri_actor in self.grouped_actors['TAGame.PRI_TA']:
				if hasattr(pri_actor, 'team'):
					continue
				team_prop = pri_actor.getProp('Engine.PlayerReplicationInfo:Team')
				if not team_prop:
					continue
				pri_actor.team = self.findActor(team_prop[1])

		# link components to car
		components = [
			'TAGame.CarComponent_Boost_TA',
			'TAGame.CarComponent_Jump_TA',
			'TAGame.CarComponent_DoubleJump_TA',
			'TAGame.CarComponent_Dodge_TA',
			'TAGame.CarComponent_FlipCar_TA',
		]
		for component in components:
			if component in self.grouped_actors:
				for component_actor in self.grouped_actors[component]:
					if hasattr(component_actor, 'car'):
						continue
					car_prop = component_actor.getProp('TAGame.CarComponent_TA:Vehicle')
					if not car_prop:
						continue
					component_actor.car = self.findActor(car_prop[1])

		if 'TAGame.Car_TA' in self.grouped_actors:
			# link car -> pri
			for car_actor in self.grouped_actors['TAGame.Car_TA']:
				if hasattr(car_actor, 'pri'):
					continue
				pri_prop = car_actor.getProp('Engine.Pawn:PlayerReplicationInfo')
				if not pri_prop:
					continue
				car_actor.pri = self.findActor(pri_prop[1])

			# create / update players
			for car_actor in self.grouped_actors['TAGame.Car_TA']:
				player_id = car_actor.getPlayerId()
				if not player_id:
					continue
				if player_id not in self.players:
					self.players[player_id] = Player(player_id)
				self.players[player_id].update(car_actor)

	def findActor(self, find_actor_id):
		"""
		Attempts to find and return an actor with the given `find_actor_id`. Returns
		None when the actor cannot be found.
		"""
		find_actor_id = int(find_actor_id)
		for actor_id, actor in self.actors.items():
			if int(actor_id) == find_actor_id:
				return actor
		return None

	def checkCollisions(self):
		"""
		Determine when and where each collision happened during this game. Save
		the collision data in `self.players`.
		"""
		if 'TAGame.Car_TA' not in self.grouped_actors:
			# no need to check collisions when no cars exist
			return

		# each frame, we only want to check actors that are within Collisions.FRAME_CHECK_RADIUS
		# units of each other

		# each frame, we only want to tween if anyone is within Collisions.FRAME_CHECK_RADIUS
		# units of each other

		# create tuples of actors that we want to check this frame
		pairs = []
		ball = self.ball_actor
		for car in self.grouped_actors['TAGame.Car_TA']:
			# we dont want to check cars that arent linked with players yet
			player_id = car.getPlayerId()
			if not player_id:
				continue
			player = self.players[player_id]

			# check if the last collision with the ball was within a certain number of frames
			# if it is, we should skip this pair
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

		if len(pairs) <= 0:
			# only tween if any pairs need to be checked
			return

		self.tween = 0
		# save which actors have collided
		collided = []
		for i in range(self.NUM_TWEENS):
			for actor1, actor2 in pairs:
				# combine actor ids into a key for faster lookup
				key = actor1.id + actor2.id * 1024
				if key in collided:
					# dont allow multiple collisions between the same actors per frame
					continue

				# determine the check radius
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
		self.tween = 0

	def handleCollision(self, actor1, actor2, collision):
		"""
		Handles a single collision between two actors.
		"""
		if (actor1.isClass('TAGame.Car_TA')):
			player_id = actor1.getPlayerId()
			if player_id:
				self.players[player_id].addCollision(collision)
		if (actor2.isClass('TAGame.Car_TA')):
			player_id = actor2.getPlayerId()
			if player_id:
				self.players[player_id].addCollision(collision)
		print("*** Collision! ***", self.seconds_remaining, self.frame['Number'], self.tween, "[{0}] x [{1}]".format(actor1.getName(), actor2.getName()), collision.point)

	def distance(self, actor1, actor2, return_midpoint=False):
		"""
		Returns the distance between two actors. Optionally also returns the midpoint
		between those two actors.
		"""
		rval = False
		if return_midpoint:
			rval = (False, False)
		rb1 = actor1.getRB(self.frame['Number'], self.tween, self.NUM_TWEENS)
		rb2 = actor2.getRB(self.frame['Number'], self.tween, self.NUM_TWEENS)
		if not rb1 or not rb2:
			return rval
		p1 = numpy.array(rb1['Position'])
		p2 = numpy.array(rb2['Position'])
		dist = numpy.linalg.norm(p1 - p2)
		if return_midpoint:
			return (dist, numpy.median([p1, p2], axis=0))
		return dist

	def collides(self, actor1, actor2, check_radius):
		"""
		Returns a Collision if the two actors intersect. Otherwise returns False.
		"""
		(dist, midpoint) = self.distance(actor1, actor2, True)
		if not dist:
			return False
		if dist > check_radius + Collision.TOLERANCE:
			return False
		shape1 = actor1.getShape(self.frame['Number'], self.tween, self.NUM_TWEENS)
		shape2 = actor2.getShape(self.frame['Number'], self.tween, self.NUM_TWEENS)
		if not shape1 or not shape2:
			return False
		if shape1.intersects(shape2, Collision.TOLERANCE):
			return Collision(midpoint, self.frame['Number'], actor1.id, actor2.id)
		return False
