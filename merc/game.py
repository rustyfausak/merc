from merc.actor import Actor
from merc.collision_bounds import CollisionBounds
from pprint import pprint
import sys
import numpy
import itertools
from PIL import Image, ImageDraw, ImageColor

class Game:
	def __init__(self, data):
		self.__dict__ = data

	def processFrames(self):
		self.actors = {}
		im = Image.new('RGB', (255, 255))
		draw = ImageDraw.Draw(im)
		draw.text((0, 0), "Distance Traveled", "#00ff00")
		draw.text((100, 240), "Velocity", "#00ff00")
		draw.line((0, 255) + (255, 0), fill='#bbbbbb')
		for frame in self.Frames:
			for id, data in frame['Spawned'].items():
				self.actors[id] = Actor(data)
			for id, data in frame['Updated'].items():
				self.actors[id].update(data)
			self.link()
			self.noodle(draw)
			#self.collisions()
			#pprint(self.actors)
		im.save('data.png')

	def noodle(self, draw):
		cars = {k: v for k, v in self.actors.items() if v.isCar()}.items()
		colors = ['#ff0000', '#00ff00', '#0000ff', '#ff00ff']
		colorindex = 0
		colormap = {}
		for id, car in cars:
			if not hasattr(car, 'pri'):
				continue
			pri = car.pri
			player_id = pri.getProp('Engine.PlayerReplicationInfo:PlayerID')
			if not player_id:
				continue
			if car.last_rb:
				p1 = numpy.array([0, 0, 0])
				p2 = numpy.array(car.last_rb['LinearVelocity']) / 100 * 0.85
				velocity = numpy.linalg.norm(p2 - p1)
				travel = car.getTravel()
				if pri.getProp not in colormap.keys():
					colormap[player_id] = colors[colorindex % len(colors)]
					colorindex += 1
				color = colormap[player_id]
				draw.point((velocity, travel * -1 + 255), color)

	def link(self):
		pris = {k: v for k, v in self.actors.items() if v.isPRI()}.items()
		for id, pri in pris:
			if hasattr(pri, 'team'):
				continue
			team_prop = pri.getProp('Engine.PlayerReplicationInfo:Team')
			if not team_prop:
				continue
			pri.team = self.findActor(team_prop[1])

		cars = {k: v for k, v in self.actors.items() if v.isCar()}.items()
		for id, car in cars:
			if hasattr(car, 'pri'):
				continue
			pri_prop = car.getProp('Engine.Pawn:PlayerReplicationInfo')
			if not pri_prop:
				continue
			car.pri = self.findActor(pri_prop[1])

	def findActor(self, find_actor_id):
		find_actor_id = int(find_actor_id)
		for actor_id, actor in self.actors.items():
			if int(actor_id) == find_actor_id:
				return actor
		return None

	'''
	def collisions(self):
		cars = {k: v for k, v in self.actors.items() if v.isCar()}.items()
		balls = {k: v for k, v in self.actors.items() if v.isBall()}.items()

		for (id1, car1), (id2, car2) in itertools.combinations(cars, 2):
			if self.collide(car1, car2):
				print("car x car collision", id1, id2)

		for id_ball, ball in balls:
			for id_car, car in cars:
				if self.collide(ball, car):
					print("car x ball collision", id_car, id_ball)

	def collide(self, actor1, actor2):
		rbstate1 = actor1.getRBState()
		if not rbstate1:
			return False
		rbstate2 = actor2.getRBState()
		if not rbstate2:
			return False
		p1 = numpy.array(rbstate1['Position'])
		p2 = numpy.array(rbstate2['Position'])
		dist = numpy.linalg.norm(p1 - p2)
		radius = CollisionBounds.CAR_AND_CAR_RADIUS
		if actor1.isBall() or actor2.isBall():
			radius = CollisionBounds.CAR_AND_BALL_RADIUS
		if dist <= radius:
			return True
	'''
