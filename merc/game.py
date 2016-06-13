from merc.actor import Actor
from pprint import pprint
import sys

class Game:
	def __init__(self, data):
		self.__dict__ = data

	def processFrames(self):
		self.actors = {}
		for frame in self.Frames:
			for actor_id, spawn_data in frame['Spawned'].items():
				self.actors[actor_id] = Actor(spawn_data)
			for actor_id, update_data in frame['Updated'].items():
				self.actors[actor_id].update(update_data)

			for ball_id, ball in {k: v for k, v in self.actors.items() if v.isBall()}.items():
				pprint(ball)
			sys.exit()


