class Actor:
	def __init__(self, data):
		self.__dict__ = data

	def update(self, data):
		self.__dict__.update(data)

	def isBall(self):
		return self.Class == 'TAGame.Ball_TA'
