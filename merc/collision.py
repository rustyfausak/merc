class Collision:
	CAR_RADIUS = 91 # based on a max car size of 130x86x42
	BALL_RADIUS = 88
	CAR_AND_BALL_RADIUS = CAR_RADIUS + BALL_RADIUS
	CAR_AND_CAR_RADIUS = CAR_RADIUS * 2
	MIN_FRAMES_BETWEEN = 8
	FRAME_CHECK_RADIUS = 300

	def __init__(self, point, frame_number, id_actor1, id_actor2):
		self.point = point
		self.frame_number = frame_number
		self.id_actor1 = id_actor1
		self.id_actor2 = id_actor2
