from evonum_fitness import *
from evonum_solvers import *

class Terrarium(object):
	def __init__(self):
		self._current_day = 0
		self._forces = []
		self._solvers = []
		self._max_solvers = 100
		self._max_forces = 2
		self._chance_to_survive_prune = 1
		
	def addForce(self, force_type, force_subtype, conditions = None):
		if len(self._forces) >= self._max_forces:
			print "Already at max forces"
			return
		elif force_type == "Simple":
			if force_subtype == "Position":
				new_force = SimplePosition("PositionForce"+str(len(self._forces)+1))
				new_force.loadConditions(conditions)
			elif force_subtype == "Equation":
				new_force = SimpleEquation("EquationForce"+str(len(self._forces)+1))
			else:
				print "Unknown Simple subtype"
				return
		elif force_type == "Dynamic":
#			if force_subtype == "Position":
#				new_force = DynamicPosition
			if force_subtype == "Equation":
				new_force = DynamicEquation("DynamicEquationForce"+str(len(self._forces)+1))
		else:
			print "Unknown force"
			return
		
		self._forces.append(new_force)
	
	def addSolver(self, solver_type="Small"):
		name = "Solver"+str(len(self._solvers)+1)+"_"+str(self._current_day)+".1"
		self._solvers.append(SolverFactory.newSolver("Small",name))

	def runDays(self, total=0):
		if total<1:
			while True:
				self.beginDay()
		else:
			for x in range(0,total):
				self.beginDay()
				
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
		self.reproduceSolvers() #Every surviving solver reproduces once at start of day
		self.evaluateSolvers() #Every solver and new progeny gets evaluated
		self.getMetrics() #For printing to screen or other logging
		self.writeDay() #TODO: Will be changed
		self.pruneSolvers() #If more solvers than max for environment, assess solvers based on fitness and flag the failures for death.
	
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
		return max_fit, avgfit
	
	def writeDay(self): #TODO: Move to logging class
		outfile = open("daily_dump.txt", "w") 
		max_fit, avgfit = self.getMetrics()
		outfile.write("Day "+str(self._current_day)+" AvgFit: "+str(avgfit)+" MaxFit: "+str(max_fit)+" Forces:\n")
		for item in self._forces:
			outfile.write(item.getDescription()+"\n")
		outfile.write("\n"+"="*50+"\n")
		solver_scores = [[x] for x in self._solvers]
		for item in solver_scores:
				item.append(item[0].getFitness())
		solver_scores.sort(key = lambda x: x[1], reverse=True)
		outfile.write("Top 5 solvers:\n")
		for item in solver_scores[:4]:
			outfile.write(item[0].getDescription())
		outfile.write("\n")
		outfile.close()
		
		
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
				luckyday = True if random.randint(1,100) <= self._chance_to_survive_prune else False #Each solver failing the fitness check has a last chance to survive
				if not luckyday:
					item[0].Death()
		for item in self._forces: #TODO: Figure out a way to isolate fitness forces, as it is right now, if you have multiple different fitness forces, this average is calculated across them, etc.
			if item.getType() == "Dynamic" and self._current_day > 100: #Dynamic fitness forces adjust the chance of each random variable based on past performance of solvers. Give solvers a 100 days to adapt first.
				avg = item.getAverageFitness()
				if solver_scores[0][1]>=avg[0]:
					increase = False
				else:
					increase = True
				avg[0] = (avg[0]*avg[1]+solver_scores[0][1])/(avg[1]+1)
				avg[1] += 1
				item.setAverageFitness(avg)
				condition, temp = item.getConditions()
				item.updateConditionProbability(condition, increase)
#			for item in solver_scores:
#				print item[0].getName()+"\t"+str(item[1])
					
	def printLivingSolvers(self):
		for solver in self._solvers:
			if solver.isAlive():
				print solver.getDescription()
				print "Fitness score: %.2f" % solver.getFitness()

	def printOldSolvers(self): #Print solvers that have survived at least one day.
		for solver in self._solvers:
			if solver._age > 0:
				print solver.getDescription()
				print "Fitness score: %.2f" % solver.getFitness()
		
	def printForces(self):
		for force in self._forces:
			print force.getDescription()
	
	def importSolver(self, solver):
		self._solvers.append(solver)
	
	def importForce(self, force):
		if len(self._forces) >= self._max_forces:
			print "Already at max forces"
			return
		else:
			self._forces.append(force)
	
	def exportSolvers(self):
		solverdicts = []
		for item in self._solvers:
			solverdicts.append(item.export())
		return solverdicts
	
	def importSolverDicts(self, solverdicts):
		for item in solverdicts:
			self._solvers.append(SolverFactory.importSolver(item))
	
	def clearSolvers(self):
		self._solvers = []
	
	def clearFitness(self):
		self._forces = []
	
	def endWorld(self, days, destination): #End the world in days days, ramp down the maximum population each day to reach final collection of destination of the fittest solvers at the end.
		#initial_max = self._max_solvers
		m = (self._max_solvers-destination)*days/(days-1)
		b = self._max_solvers - m
		for x in range(1,days+1):
			self._max_solvers = int(m/x + b+.5)
#			print "Max solvers:",self._max_solvers
			self.runDays(1)
	
	def importAttributes(self, attributes):
		for item in attributes:
			setattr(self, item, attributes[item])
