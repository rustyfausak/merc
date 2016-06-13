from merc.game import Game
import json

def analyze(file):
	with open(file, encoding='utf-8') as file:
		data = json.loads(file.read())
	game = Game()
