import inspect
import math, random
from evonum_god import God
from evonum_fitness import *
from evonum_module import *
from evonum_individual import *

#Misc functions
def error():
	raise NotImplementedError, "%s not implemented" % inspect.stack()[1][3]



	
#Main application
god = God()
god.loadConfig()
force = Equation("Primer Number Challenge")
force.loadConditions("primes_1000.txt")
force.beginDay()
maturity_force = OldAge("Old Age Kills")

print force
solver = Solver("Greg")
for x in range (1,5):
	solver.addModule("Random")
print solver.getDescription()
fitness = solver.calculateUnitFitness(force)
print fitness
dummy = Solver("Dummy")
for x in range(1,6):
	dummy.addModule("Equation","Power")
print dummy.getDescription()
dummy_fitness = dummy.calculateUnitFitness(force)
print "Greg's fitness was %.2f and the dummy's fitness was %.2f" % (fitness, dummy_fitness)
