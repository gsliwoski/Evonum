import inspect
import math, random
from evonum_god import God

def error():
	raise NotImplementedError, "%s not implemented" % inspect.stack()[1][3]

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
	def __init__(self, name="Unnamed Simple Fitness Force"):
		self._name = name
		self._expected = []
		self._current_expected = 0
#		self._god = God()
		self._age = 0
		self._current_condition = 0
		self._max = len(self._expected)
		self._min = 1
		self._type = "Simple"
		self._penalty = -99999999999

	def getDescription(self):
		return "%s Fitness. Name: %s Age: %d, Current Condition: %d, Current Desire: %d" % (self._type, self._name, self._age, self._current_condition, self._current_expected)

	def _setConditions(self):
		random.seed()
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
			print self,"\nUnable to set maximum condition to",maximum
		#TODO add tests to make sure max is reasonable int
	def setMin(self, minimum):
		try:
			self._min = int(minimum)
		except:
			print self,"\nUnable to set minimum condition to",minimum
		#TODO add tests to make sure min is reasonable int
	
	def loadConditions(self, filename):
		try:
			self._expected = [ int(x) for x in open(filename).read().split()]
			self._max = len(self._expected)
		except:
			print self,"\nFailed to load conditions from",filename
	
	def getType(self):
		return self._type
	
	def getPenalty(self):
		return self._penalty

class OldAge(FitnessInterface):
	def __init__(self, name="Maturity"):
		self._name = name
		self._age = 0
		self._ideal_age = 30
		self._type = "Maturity"
	
	def loadConditions(self, ideal):
		self._ideal_age = ideal
	
	def getConditions(self):
		return 0, self._ideal_age
	
