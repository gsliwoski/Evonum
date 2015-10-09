import random, sys
from evonum_terrarium import *
from evonum_solvers import SolverFactory
from evonum_scripter import *
import matplotlib.pyplot as plt
import numpy as np


x = np.linspace(0,2,100)
plt.plot(x,x,label='linear')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.draw()
#plt.close()
plt.clf
plt.plot(x,x**2,label='ha')
plt.show()

random.seed()
#try:
filename = sys.argv[1]
print filename
script = open(filename).readlines()
runner = SimpleScripter(script)
#runner.run()
#plt.ioff()


#except:
#	print "Unable to open script. Run as:"
#	print "python tests.py SCRIPTFILE"

#greg = LinearSolver("Greg")
#greg.beginDay()
#print greg.getDescription()
#solvers = [greg]
#solvers.append(greg.reproduce())
#for item in solvers:
#	item.beginDay()
#	print item.getDescription()
#print solvers[1].getDescription()
#print solvers[1].__dict__
#for item in solvers:
#	print item.getDescription()
#	print item.__dict__

#fitness = [SimplePosition("Beefcake")]
#fitness[0].loadConditions("primes_1000.txt")
#for item in fitness:
#	item.beginDay()
#	print item.getDescription()
#for item in solvers:
#	item.calculateFitness(fitness)
#	print item.getDescription()
#	print "Fitness score: %.2f" % item.getFitness()
	

#world = Terrarium()
#world.addForce("Simple", "Position")
#world.addForce("Simple","Equation")
#world.addForce("Simple","Equation")
#for x in range(0,5):
#world.addSolver("Small")
#world.runDays(1)
#print "*"*50,"Printing Solvers"
#world.printSolvers()
#print "*"*50,"Exporting Solvers"
#solvers = world.exportSolvers()
#for item in solvers:
#	print item
#print "*"*50,"Clearing Solvers"
#world.clearSolvers()
#print "*"*50,"Adding empty Solver"
#world.addSolver("Small")
#world.printSolvers()
#print "*"*50,"Importing Solvers"
#world.importSolvers(solvers)
#print "*"*50,"Printing Solvers"
#world.printSolvers()
#world.runDays(1)
#world.printSolvers()
#defined_solvers = [{'_type': 'Small', '_fitness_calculator': 'Linear', '_living': True, '_swap_module_mutation_chance': 5, '_max_modules': 10, '_unique': True, '_modules': [{'_type': 'Fitness', '_spread': 10, '_coeff': 1, '_subtype': 'Power_2', '_max_coeff': 100, '_power': 2, '_min_coeff': -100}], '_module_mutation_chance': 50, '_lifespan': 100, '_age': 0, '_property_mutation_chance': 10, '_children': 0, '_fitness': -1.2430673920511952e+16, '_name': 'Solver1.1', '_spread': 10, '_total_modules': 1, '_property_chances': [5, 10, 10, 0]}]
#world.importSolvers(defined_solvers)
#world.printSolvers()
#world.runDays(1)
#world.printForces()
#world.printSolvers()

#pow2 = SolverFactory.
#world.runDays(100)
#y=0
#for z in range(0,100):
#	y+=1
#	for x in range(1,51):
#		defined_solver = {"Type": "Small", "Name": "Linear_NonUnique"+str(y)+"-"+str(x), "Unique": "False", "Calculator": "Linear"}
#		new_solver = SolverFactory.DefineSolver(defined_solver)
#		world.importSolver(new_solver)
#	for x in range(1,51):
#		defined_solver = {"Type": "Small", "Name": "Linear_Unique"+str(y)+"-"+str(x), "Unique": "True", "Calculator": "Linear"}
#		new_solver = SolverFactory.DefineSolver(defined_solver)
#		world.importSolver(new_solver)
#	world.runDays(100)
	
#for x in range(1,6):
#	defined_solver = {"Type": "Small", "Name": "Dynamic_NonUnique"+str(x), "Unique": "False", "Calculator": "Dynamic"}
#	new_solver = SolverFactory.DefineSolver(defined_solver)
#	world.importSolver(new_solver)
#for x in range(1,6):
#	defined_solver = {"Type": "Small", "Name": "Dynamic_Unique"+str(x), "Unique": "True", "Calculator": "Dynamic"}
#	new_solver = SolverFactory.DefineSolver(defined_solver)
#	world.importSolver(new_solver)

#world.printForces()
#world.printOldSolvers()
#for x in range(0,10):
#	world.addSolver("Small")
#world.runDays(10)
#world.endWorld(10,5)

