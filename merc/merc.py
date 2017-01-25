from merc.actors import Actor
from merc.actors import Car
from merc.actors import Ball
from merc.actors import PRI
from merc.player import Player
from merc.actors import imDone
import json
import sys
import logging
import hashlib
from pprint import pformat

class Merc:
	def __init__(self, file):
		self.file = file
		self.data = None
		self.frame_index = 0
		self.actors = {}
		self.time = None
		self.frame_number = None
		self.players = {}

	def process(self):
		"""
		Open the replay file, parse the json, then process the frames.
		"""
		with open(self.file, encoding='utf-8') as fstream:
			self.data = json.loads(fstream.read())
		if 'Frames' not in self.data:
			raise Exception("'Frames' not found in replay json.")
		logging.debug("Starting frame processing..")
		while self.frame_index < len(self.data['Frames']):
			self.processFrame(self.data['Frames'][self.frame_index])
			self.frame_index += 1
		logging.debug("End of frame processing.")
		imDone()
		for uid, player in self.players.items():
			print(pformat(vars(player)))

	def processFrame(self, frame):
		"""
		Process a single frame.
		"""
		self.time = frame['Time']
		self.frame_number = frame['Number']
		#logging.debug("Processing frame #%d @ %s" % (self.frame_number, self.time))
		self.spawnActors(frame['Spawned'])
		self.updateActors(frame['Updated'])
		self.destroyActors(frame['Destroyed'])
		self.linkActors()
		self.buildPlayers()
		self.updatePlayers()
		#self.checkCollisions()

	def spawnActors(self, block):
		for id, data in block.items():
			actor = Actor.spawn(id, data, self.time, self.frame_number)
			if not actor:
				#logging.debug("Skipped actor #%s (%s)" % (id, data['Class']))
				continue
			self.actors[id] = actor
			#logging.debug("+ Spawned actor %s" % actor)

	def updateActors(self, block):
		for id, data in block.items():
			if id not in self.actors:
				#logging.debug("Skipped actor #%s" % id)
				continue
			actor = self.actors[id]
			actor.update(data, self.time, self.frame_number)
			#logging.debug("~ Updated actor %s" % actor)
		for id, actor in self.actors.items():
			if actor.frame_number != self.frame_number:
				actor.update({}, self.time, self.frame_number)

	def destroyActors(self, block):
		for id in map(str, block):
			if id not in self.actors:
				#logging.debug("Skipped actor #%s" % id)
				continue
			self.actors[id].destroy(self.time, self.frame_number)
			self.actors.pop(id, None)
			#logging.debug("x Destroyed actor #%s" % id)

	def linkActors(self):
		for id, actor in self.actors.items():
			actor.link(self.actors)

	def buildPlayers(self):
		for id, actor in self.actors.items():
			if not isinstance(actor, PRI):
				continue
			if actor.player:
				continue
			if not actor.unique_id:
				continue
			j = json.dumps(actor.unique_id, sort_keys=True)
			uid = hashlib.md5(j.encode('utf-8')).hexdigest()
			if uid not in self.players.items():
				self.players[uid] = Player(uid)
			self.players[uid].addPRIActor(actor)
			actor.player = self.players[uid]

	def updatePlayers(self):
		for uid, player in self.players.items():
			updated_props = player.update()
			if not len(updated_props):
				continue
			logging.debug("%s" % player)
			for prop in updated_props:
				logging.debug("\t%s => %s" % (prop, getattr(player, prop)))

	def checkCollisions(self):
		cars = []
		ball = None
		for id, actor in self.actors.items():
			if isinstance(actor, Car):
				cars.append(actor)
			elif isinstance(actor, Ball):
				ball = actor



