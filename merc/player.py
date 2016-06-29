class Player:
	def __init__(self, id):
		self.id = id
		self.name = ''
		self.collisions = []

	def update(self, car_actor):
		self.name = car_actor.getName()

	def addCollision(self, collision):
		self.collisions.append(collision)

	def getLastCollisionWithActor(self, actor_id):
		for collision in reversed(self.collisions):
			if collision.id_actor1 == actor_id or collision.id_actor2 == actor_id:
				return collision
		return None
