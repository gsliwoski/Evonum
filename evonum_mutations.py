import math, random

class Mutations(object):
	@staticmethod
	def GaussianMutation(initial, spread):
#		print "Gaussian Mutation with initial=%d and spread=%.2f" % (initial, spread)
		return random.gauss(initial, spread)
	@staticmethod
	def HardMutation(low, high):
		return random.randrange(low, high)

