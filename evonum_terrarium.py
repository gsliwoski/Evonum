from evonum_fitness import *
from evonum_solvers import *

class Terrarium(object):
	def __init__(self):
		self._current_day = 0
		self._forces = []
		self._solvers = []
		self._max_solvers = 10
		self._max_forces = 1
		
	def addForce(self, force_type, force_subtype):
		if len(self._forces) >= self._max_forces:
			print "Already at max forces"
			return
		elif force_type == "Simple":
			if force_subtype == "Position":
				new_force = SimplePosition("Force"+str(len(self._forces)+1))
				new_force.loadConditions("primes_1000.txt")
			else:
				print "Unknown Simple subtype"
				return
		else:
			print "Unknown force"
			return
		
		self._forces.append(new_force)
	
	def addSolver(self, solver_type):
		if solver_type == "Linear":
			new_solver = LinearSolver("Solver"+str(len(self._solvers)+1))
			self._solvers.append(new_solver)
			
	def runDays(self, total=0):
		if total<1:
			while True:
				self.beginDay()
#				self.printSolvers()
		else:
			for x in range(0,total):
				self.beginDay()
#				self.printSolvers()
				
	def beginDay(self):
		self._current_day += 1
#		print "-"*20+"Beginning Day "+str(self._current_day)+"-"*20
		dead_solvers = []
		for item in self._forces:
			item.beginDay()
		for pos, item in enumerate(self._solvers):
			still_living = item.beginDay()
			if not still_living:
				dead_solvers.append(pos)
		surviving = [sol for pos,sol in enumerate(self._solvers) if pos not in dead_solvers] #Remove dead solvers
		self._solvers = surviving
		self.reproduceSolvers()
		self.evaluateSolvers()
		self.getMetrics()
		self.pruneSolvers()
	
	def reproduceSolvers(self):
		babies = []
		for solver in self._solvers:
			babies.append(solver.reproduce())
		self._solvers += babies
			
	def evaluateSolvers(self):
		for solver in self._solvers:
			solver.calculateFitness(self._forces)
	
	def getMetrics(self):
		fit = 0
		max_fit = None
		min_fit = None
		for item in self._solvers:
			fit += item.getFitness()
			if max_fit == None or item.getFitness() > max_fit:
				max_fit = item.getFitness()
			if min_fit == None or item.getFitness() < min_fit:
					min_fit = item.getFitness()
		avgfit = fit/len(self._solvers)
#		print "="*15+"Daily Metrics"+"="*15
#		print "Average Fitness: %.2f" % avgfit
#		print "Maximum Fitness: %.2f" % max_fit
#		print "Minimum Fitness: %.2f" % min_fit
#		print "="*30
		print "%d\t%.2f" % (self._current_day, max_fit)
		
	def pruneSolvers(self): #Prune the population of solvers of those that had the lowest fitness scores
		if len(self._solvers) < self._max_solvers:
#			print "No pruning necessary"
			pass
		else:
#			print "Population: %s\tMax Population: %s\tNeed to kill: %s" % (len(self._solvers), self._max_solvers, len(self._solvers)-self._max_solvers)
			solver_scores = [[x] for x in self._solvers]
			for item in solver_scores:
				item.append(item[0].getFitness())
			solver_scores.sort(key = lambda x: x[1], reverse=True)
			for item in solver_scores[self._max_solvers:]:
				item[0].Death()
#			for item in solver_scores:
#				print item[0].getName()+"\t"+str(item[1])
					
	def printSolvers(self):
		for solver in self._solvers:
			print solver.getDescription()
			print "Fitness score: %.2f" % solver.getFitness()
	
	
