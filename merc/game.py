from merc.actor import Actor
from pprint import pprint
import sys
import numpy
import itertools

class Game:
	def __init__(self, data):
		self.__dict__ = data

	def processFrames(self):
		self.actors = {}
		#dist_max = 0
		#bins = [0, 25, 50, 75, 100, 150, 200, 300, 400]
		#counts = [0] * len(bins)
		num_pc = 0
		for frame in self.Frames:
			for id, data in frame['Spawned'].items():
				self.actors[id] = Actor(data)
			for id, data in frame['Updated'].items():
				self.actors[id].update(data)

			collidables = {k: v for k, v in self.actors.items() if v.isCollidable()}.items()

			'''
			for id, actor in collidables:
				dist = actor.getTravel()
				i = numpy.digitize(dist, bins)
				counts[i] += 1
				if dist > dist_max:
					dist_max = dist
				#print(d)

			'''

			for (_, actor1), (_, actor2) in itertools.combinations(collidables, 2):
				rbstate1 = actor1.getRBState()
				if not rbstate1:
					continue
				rbstate2 = actor2.getRBState()
				if not rbstate2:
					continue
				p1 = numpy.array(rbstate1['Position'])
				p2 = numpy.array(rbstate2['Position'])
				dist = numpy.linalg.norm(p1 - p2)
				if dist < 180:
					num_pc += 1
					#print("Potential collision!")
					#print(dist)

			'''
			for id1, actor1 in collidables:
				rbstate1 = actor1.getRBState()
				if not rbstate1:
					continue
				p1 = numpy.array(rbstate1['Position'])
				radius1 = actor1.getCollisionBubbleRadius()
				for id2, actor2 in collidables:
					if id1 == id2:
						continue
					rbstate2 = actor2.getRBState()
					if not rbstate2:
						continue
					p2 = numpy.array(rbstate2['Position'])
					radius2 = actor1.getCollisionBubbleRadius()
					dist = numpy.linalg.norm(p1 - p2)
					if dist < radius1 + radius2:
						pass
						#print("Potential collision!")
						#print(dist)
			'''

			#input("Press Enter to continue...")
		#pprint(bins)
		#pprint(counts)
		#for k, val in enumerate(counts):
			#print(bins[k-1], "<=", val, "<", bins[k])
		#print("Max distance travelled in one frame: ", dist_max)
		print("Num potential collisions: ", num_pc)
