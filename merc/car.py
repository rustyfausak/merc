from merc.box import Box

import numpy

class Car:
	def __init__(self, body):
		self.body = body

	def getBox(self):
		if self.body == 'Backfire':
			return Box(117.1566, 84.67036, 31.39440)
		if self.body == 'Batmobile':
			return Box(128.8198, 84.67036, 29.39440)
		if self.body == 'Breakout':
			return Box(128.9930, 76.36520, 30.30000)
		if self.body == 'DeLorean':
			return Box(123.9424, 83.27995, 29.80000)
		if self.body == 'Dominus':
			return Box(127.9268, 83.27995, 31.30000)
		if self.body == 'Gizmo':
			return Box(122.7370, 83.25725, 37.16797)
		if self.body == 'Grog':
			return Box(119.4957, 81.87707, 36.92777)
		if self.body == 'Hotshot':
			return Box(123.9424, 77.76891, 31.80000)
		if self.body == 'Merc':
			return Box(119.9868, 77.97530, 40.26958)
		if self.body == 'Octane':
			return Box(118.0074, 84.19941, 36.15907)
		if self.body == 'Paladin':
			return Box(123.2510, 76.88635, 29.80000)
		if self.body == 'Ripper':
			return Box(127.5825, 79.09612, 31.43038)
		if self.body == 'RoadHog':
			return Box(117.1566, 84.67036, 31.39440)
		if self.body == 'Scarab':
			return Box(114.9007, 82.74691, 37.66797)
		if self.body == 'Takumi':
			return Box(118.4945, 80.27252, 34.30000)
		if self.body == 'X-Devil':
			return Box(127.6995, 81.88242, 31.80000)
		if self.body == 'Venom':
			return Box(119.0544, 85.74410, 34.76144)
		if self.body == 'Zippy':
			return Box(118.0074, 84.19941, 33.15907)
