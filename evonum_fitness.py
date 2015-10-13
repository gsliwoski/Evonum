from __future__ import print_function
import inspect
import math, random
#from evonum_god import God

def error():
	raise NotImplementedError("%s not implemented" % inspect.stack()[1][3]) #Used for interface

#FitnessInterface is the interface for all the fitness forces that drive evolution. These classes provide a condition (solver input) and desired solver output
class FitnessInterface(object):
	def __init__(self, name):
		error()
	def getConditions(self): #gets the current condition variable and the desired response
		error()
	def getName(self): #returns title of fitness force
		error()
	def beginDay(self): #increment age and calculate conditions
		error()
	def loadConditions(self, *args): #load necessary fitness conditions, different depending on type of Fitness Force
		error()
	def getType(self): #returns the type of fitness necessary for knowing which modules can handle it
		error()
	def getPenalty(self): #returns fitness penalty if no modules are present to deal with this fitness condition
		error()
	def getDescription(self): #return string
		error()

#Concrete Fitness Forces
#Position Fitness force provides one value and expects a specific return value. Fitness can then be calculated as how close the solver came to the expected value. Value provided is the position of the list of expected.
class SimplePosition(FitnessInterface):
	def __init__(self, name="Unnamed Simple Position Fitness Force"):
		self._name = name
		self._expected = []
		self._current_expected = 0
#		self._god = God()
		self._age = 0
		self._current_condition = 0
		self._max = len(self._expected)
		self._min = 0
		self._type = "Simple"
		self._penalty = -99999999999 #Used when a solver has no modules for handling this fitness force.

	def getDescription(self):
		return "%s Fitness. Name: %s Age: %d, Current Condition: %d, Current Desire: %d" % (self._type, self._name, self._age, self._current_condition, self._current_expected)

	def _setConditions(self):
		self._current_condition = random.randint(self._min,self._max)
		self._current_expected = self._expected[self._current_condition-1]

	def beginDay(self):
		self._age += 1
		self._setConditions()

	def getConditions(self):
		return self._current_condition, self._current_expected
		
	def setMax(self, maximum):
		try:
			self._max = int(maximum)
		except:
			print ("\nUnable to set maximum condition to "+ maximum)
		#TODO add tests to make sure max is reasonable int
	def setMin(self, minimum):
		try:
			self._min = int(minimum)
		except:
			print ("\nUnable to set minimum condition to "+minimum)
		#TODO add tests to make sure min is reasonable int
	
	def loadConditions(self, filename):
		try:
			self._expected = [ float(x) for x in open(filename).read().split()]
			self._max = len(self._expected)
		except:
			assert self._name+" Failed to load conditions from "+str(filename)		
		finally:
			assert len(self._expected)>0, "No conditions loaded for position fitness force!"

	
	def getType(self):
		return self._type
	
	def getPenalty(self):
		return self._penalty

#Equation fitness force randomly generates variable and expected is based on a provided equation.
class SimpleEquation(FitnessInterface):
	def __init__(self, name="Unnamed Simple Equation Fitness Force"):
		self._name = name
		self._current_expected = 0
#		self._god = God()
		self._age = 0
		self._current_condition = 0
		self._max = math.pi/2
		self._min = -math.pi/2
		self._type = "Simple"
		self._penalty = -99999999999
		
	def getDescription(self):
		return "%s Fitness. Name: %s Age: %d, Current Condition: %.2f, Current Desire: %.2f" % (self._type, self._name, self._age, self._current_condition, self._current_expected)

	def _setConditions(self):
		self._current_condition = random.random()*(self._max - self._min) + self._min
#		self._current_expected = 5*pow(self._current_condition,2)+50*math.sin(self._current_condition)-90*math.log(self._current_condition,10) #TODO: Remove hard-coded equation
		self._current_expected = math.tan(self._current_condition)
#		self._current_expected = self._current_condition + .05*pow(self._current_condition,2)-.0005*pow(self._current_condition,3)

	def beginDay(self):
		self._age += 1
		self._setConditions()

	def getConditions(self):
		return self._current_condition, self._current_expected
		
	def setMax(self, maximum):
		try:
			self._max = int(maximum)
		except:
			print ("Unable to set maximum condition to "+maximum)
		#TODO add tests to make sure max is reasonable int
	def setMin(self, minimum):
		try:
			self._min = int(minimum)
		except:
			print ("Unable to set minimum condition to "+minimum)
		#TODO add tests to make sure min is reasonable int
	
	def loadConditions(self, filename="nothing"):
		pass
	
	def getType(self):
		return self._type
	
	def getPenalty(self):
		return self._penalty

class DynamicEquation(FitnessInterface): #Adjusts probability of variable selection to favor variables in sections of the equation solvers have not done well with. TODO: Needs further testing and improvements.
	def __init__(self, name="Unnamed Dynamic Equation Fitness Force"):
		self._name = name
		self._current_expected = 0
#		self._god = God()
		self._age = 0
		self._max = math.pi/2
		self._min = -math.pi/2
		self._current_condition = self._min
		self._type = "Dynamic"
		self._penalty = -99999999999
		self._condition_probabilities = [100]*10
		self._avg_fitness = [0, 0]
		self._step_size = float(self._max - self._min)/len(self._condition_probabilities)
		
	def getDescription(self):
		return "%s Fitness. Name: %s Age: %d, Current Condition: %.2f, Current Desire: %.2f" % (self._type, self._name, self._age, self._current_condition, self._current_expected)

	def _setConditions(self):
		running_range_prob = 0
		sum_prob = sum(self._condition_probabilities)
		random_range = random.random()*sum_prob
		range_selection = 9
#		print ("RandomRange = %.2f" % random_range)
		for pos, val in enumerate(self._condition_probabilities):
			if random_range >= running_range_prob and random_range < running_range_prob + val:
				range_selection = pos
#				print ("Range Selection = %d" % range_selection)
				break
			else:
				running_range_prob += val
		current_min = self._min + range_selection * self._step_size
		current_max = current_min + self._step_size
#		print ("step size: %.2f, current_min: %.2f, current_max: %.2f" % (self._step_size, current_min, current_max))
		self._current_condition = random.random()*(current_max - current_min) + current_min
#		self._current_condition = random.random()*((self._max - self._min + 1)/len(self._condition_probabilities)) + self._min + range_selection * (self._max - self._min + 1)/len(self._condition_probabilities)
#		print ("Current condition = %.2f" % self._current_condition)
#		self._current_expected = 5*pow(self._current_condition,2)+50*math.sin(self._current_condition)-90*math.log(self._current_condition,10) #TODO: Remove hard-coded equation
		self._current_expected = math.tan(self._current_condition)
#		self._current_expected = self._current_condition + .05*pow(self._current_condition,2)-.0005*pow(self._current_condition,3)
#		self._current_expected = self._current_condition*self._current_condition + 1

	def beginDay(self):
		self._age += 1
		self._setConditions()

	def getConditions(self):
		return self._current_condition, self._current_expected
		
	def setMax(self, maximum):
		try:
			self._max = int(maximum)
		except:
			print ("Unable to set maximum condition to "+maximum)
		#TODO add tests to make sure max is reasonable int
	def setMin(self, minimum):
		try:
			self._min = int(minimum)
		except:
			print ("Unable to set minimum condition to "+minimum)
		#TODO add tests to make sure min is reasonable int
	
	def loadConditions(self, filename=None):
		pass

	def getType(self):
		return self._type
	
	def getPenalty(self):
		return self._penalty

	def updateConditionProbability(self, condition, increase):
#		print ("Condition: %.2f Increase? %r" % (condition, increase))
		pos = int((condition - self._min)/self._step_size)
		if increase:
			self._condition_probabilities[pos] += 1
		else:
			self._condition_probabilities[pos] -= 1
		if self._condition_probabilities[pos]<1:
			self._condition_probabilities[pos] = 1
		elif self._condition_probabilities[pos]>1000:
			self._condition_probabilities[pos] = 1000
		print (self._condition_probabilities)
	
	def setAverageFitness(self, avg):
		self._avg_fitness = avg

	def getAverageFitness(self):
		return self._avg_fitness
