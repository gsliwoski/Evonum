from __future__ import print_function
import math
import random


class Mutations(object):
    """Collection of all potential mutations.
    
    May store attribute-based mutations to make solver mutations easier.
    """
    @staticmethod
    def GaussianMutation(initial, spread):
        """Simple gaussian-based mutation.
        
        Takes center and width and returns new value."""
#		print ("Gaussian Mutation with initial=%d and spread=%.2f" % (initial, spread))
        return random.gauss(initial, spread)

    @staticmethod
    def HardMutation(low, high):
        """Hard int mutation."""
        return random.randrange(low, high)
