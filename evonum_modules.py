import inspect
import math, random
from evonum_god import God
from evonum_mutations import *

def error():
	raise NotImplementedError, "%s not implemented" % inspect.stack()[1][3]

class ModuleFactory(object):
	@staticmethod
	def generateNewModule(module_type, module_subtype):
		fitness_subtypes = ["Power", "Sine", "Log"]
		if module_type == "Fitness":
			if module_subtype == "Random":
				random.seed()
				module_subtype = fitness_subtypes[random.randint(1,len(fitness_subtypes))-1]
			if module_subtype == "Power":
				new_module = PowerSolution()
				random.seed()
				new_module.setPower(random.randint(1,5))
			elif module_subtype == "Sine":
				new_module = SineSolution()
			elif module_subtype == "Log":
				new_module = LogSolution()
#		new_module.mutate()
		return new_module


class ModuleInterface(object):
	def mutate():
		error()
	def getResponse(self, variable):
		error()
	def updateSpread(self, spread):
		error()

class FitnessModuleInterface(object):
	def mutate():
		error()
	def getFitness(self, fitness_power):
		error()
	def getType(self):
		error()

class PowerSolution(FitnessModuleInterface):
	def __init__(self, power=1):
		self._power = power
		self._min_coeff = -1000
		self._max_coeff = 1000
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
		self._type = "Fitness"
		self._subtype = "Power"
		self._spread = 0
	
	def getResponse(self, variable):
		return self._coeff * pow(variable, self._power)
	
	def getFitness(self, fitness_power):
		variable, desire = fitness_power.getConditions()
		response = self.getResponse(variable)
		fitness = -abs(response - desire)
		return fitness
	
	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
	
	def setPower(self, power):
		self._power = power
	
	def getPower(self):
		return self._power
	
	def getDescription(self):
		string = "%s, %s: Response = %d * (variable)^%d" % (self._type, self._subtype, self._coeff, self._power)
		return string
	
	def getType(self):
		return self._type
	
	def updateSpread(self, spread):
		self._spread = spread
		
class SineSolution(FitnessModuleInterface):
	def __init__(self):
		self._min_coeff = -1000
		self._max_coeff = 1000
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
		self._type = "Fitness"
		self._subtype = "Sine"
		self._spread = 0

	def getFitness(self, fitness_power):
		variable, desire = fitness_power.getConditions()
		response = self.getResponse(variable)
		fitness = -abs(response - desire)
		return fitness
		
	def getResponse(self, variable):
		return self._coeff * math.sin(variable)
		
	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
	
	def getDescription(self):
		string = "%s, %s: Response = %d * sine(variable)" % (self._type, self._subtype, self._coeff)
		return string
	
	def getType(self):
		return self._type
	
	def updateSpread(self, spread):
		self._spread = spread

class LogSolution(FitnessModuleInterface):
	def __init__(self):
		self._min_coeff = -1000
		self._max_coeff = 1000
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
		self._base = 10
		self._type = "Fitness"
		self._subtype = "Log"
		self._spread = 0

	def getResponse(self, variable):
		return self._coeff * math.log(variable, self._base)

	def getFitness(self, fitness_power):
		variable, desire = fitness_power.getConditions()
		response = self.getResponse(variable)
		fitness = -abs(response - desire)
		return fitness
	
	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
	
	def setBase(self, base):
		self._base = base
	
	def getBase(self):
		return self._base

	def getDescription(self):
		string = "%s, %s: Response = %d * log[base %d](variable)" % (self._type, self._subtype,self._coeff, self._base)
		return string
	
	def getType(self):
		return self._type
	
	def updateSpread(self, spread):
		self._spread = spread
	
class NaturalLogSolution(FitnessModuleInterface):
	def __init__(self):
		self._min_coeff = -1000
		self._max_coeff = 1000
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
		self._type = "Fitness"
		self._subtype = "Ln"
		self._spread = 0
	
	def getResponse(self, variable):
		return self._coeff * math.log(variable)
	
	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
		
	def updateSpread(self, spread):
		self._spread = spread

class Maturity(ModuleInterface):
	def __init__(self):
		self._type = "Internal"
		self._subtype = "Maturity"
	
	def getResponse(self, variable):
		return variable
	
	def getFitness(self, fitness_power):
		variable, desire = fitness_power.getConditions()
	
	def getDescription(self):
		string = "%s, %s: Response = Difference from ideal age" % (self._type, self._subtype)	
		return string
