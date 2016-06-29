from merc.game import Game
import json

class Merc:
	def __init__(self, file):
		self.file = file

	def analyze(self):
		with open(self.file, encoding='utf-8') as fstream:
			data = json.loads(fstream.read())
		game = Game(data)
		game.processFrames()
