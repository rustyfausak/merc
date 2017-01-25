class Player:
	def __init__(self, uid):
		self.uid = uid
		self.pri_actors = []
		self.name = None
		self.body = None
		self.team = None
		self.exp = None
		self.is_partied = False
		self.unique_id = None
		self.pings = []
		self.boost_added = 0
		self.boost_consumed = 0
		self.num_jumps = 0
		self.num_doublejumps = 0
		self.num_dodges = 0
		self.distance = 0

	def addPRIActor(self, pri_actor):
		self.pri_actors.append(pri_actor)

	def update(self):
		self.updated_props = []
		for pri_actor in self.pri_actors:
			self.updatePRI(pri_actor)
			if pri_actor.team_actor:
				self.updateTeam(pri_actor.team_actor)
			if pri_actor.car_actor:
				self.updateCar(pri_actor.car_actor)
		return self.updated_props

	def updatePRI(self, pri_actor):
		if self.name is None:
			if 'name' in pri_actor.updated_props:
				self.updateProp('name', getattr(pri_actor, 'name'))
		if self.body is None:
			if 'body' in pri_actor.updated_props:
				self.updateProp('body', getattr(pri_actor, 'body'))
		if self.unique_id is None:
			if 'unique_id' in pri_actor.updated_props:
				self.updateProp('unique_id', getattr(pri_actor, 'unique_id'))
		if self.exp is None:
			if 'exp' in pri_actor.updated_props:
				self.updateProp('exp', getattr(pri_actor, 'exp'))
		if 'ping' in pri_actor.updated_props:
			self.updateProp('pings', self.pings + [getattr(pri_actor, 'ping')])
		if 'is_partied' in pri_actor.updated_props:
			self.updateProp('is_partied', getattr(pri_actor, 'is_partied'))

	def updateTeam(self, team_actor):
		if self.team is None:
			self.updateProp('team', team_actor.getColor())

	def updateCar(self, car_actor):
		if 'distance' in car_actor.updated_props:
			self.updateProp('distance', self.distance + getattr(car_actor, 'distance'))

		if 'Boost' in car_actor.component_actors:
			self.updateBoost(car_actor.component_actors['Boost'])
		if 'Jump' in car_actor.component_actors:
			self.updateJump(car_actor.component_actors['Jump'])
		if 'DoubleJump' in car_actor.component_actors:
			self.updateDoubleJump(car_actor.component_actors['DoubleJump'])
		if 'Dodge' in car_actor.component_actors:
			self.updateDodge(car_actor.component_actors['Dodge'])

	def updateBoost(self, boost_actor):
		if 'boost_added' in boost_actor.updated_props:
			self.updateProp('boost_added', self.boost_added + getattr(boost_actor, 'boost_added'))
		if 'boost_consumed' in boost_actor.updated_props:
			self.updateProp('boost_consumed', self.boost_consumed + getattr(boost_actor, 'boost_consumed'))

	def updateJump(self, jump_actor):
		if 'is_active' in jump_actor.updated_props:
			if jump_actor.is_active:
				self.updateProp('num_jumps', self.num_jumps + 1)

	def updateDoubleJump(self, doublejump_actor):
		if 'is_active' in doublejump_actor.updated_props:
			if doublejump_actor.is_active:
				self.updateProp('num_doublejumps', self.num_doublejumps + 1)

	def updateDodge(self, dodge_actor):
		if 'is_active' in dodge_actor.updated_props:
			if dodge_actor.is_active:
				self.updateProp('num_dodges', self.num_dodges + 1)

	def updateProp(self, attr, value):
		setattr(self, attr, value)
		self.updated_props.append(attr)

	def __str__(self):
		desc = self.uid
		if self.name is not None:
			desc = self.name
		return "Player %s" % (desc)
