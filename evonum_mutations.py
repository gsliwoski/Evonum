import math, random

class Mutations(object):
	@staticmethod
	def GaussianMutation(initial, spread):
#		print "Gaussian Mutation with initial=%d and spread=%.2f" % (initial, spread)
		return random.gauss(initial, spread)
	@staticmethod
	def HardMutation(low, high):
		return random.randrange(low, high)
#	def GaussianChange(self, initial, spread):
#	def HardChange(self, low, high):		

#randoms = [int (Mutations().GaussianMutation(initial, spread)+.5) for x in range(1,1000)]
#print randoms
