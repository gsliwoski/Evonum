import inspect
import math, random
from evonum_god import God

class ModuleGenerator(object):
	def generateNewModule(self, module_type, module_subtype):
		if module_type == "Equation":
			if module_subtype == "Power":
				new_module = PowerSolution()
				random.seed()
				new_module.setPower(random.randint(1,5))
			elif module_subtype == "Sine":
				new_module = SineSolution()
			elif module_subtype == "Log":
				new_module = LogSolution()
		new_module.mutate()
		return new_module

class ModuleInterface(object):
	def mutate():
		error()
	def getResponse(self, variable):
		error()

class SolutionModuleInterface(object):
	def mutate():
		error()
	def getFitness(self, fitness_power):
		error()
	def getType(self):
		error()

class PowerSolution(SolutionModuleInterface):
	def __init__(self, power=1):
		self._coeff = 0
		self._power = power
		self._min_coeff = -1000
		self._max_coeff = 1000
		self._type = "Equation"
		self._subtype = "Power"
	
	def getResponse(self, variable):
		return self._coeff * pow(variable, self._power)
	
	def getFitness(self, fitness_power):
		variable, desire = fitness_power.getConditions()
		response = self.getResponse(variable)
		fitness = -abs(response - desire)
		return fitness
	
	def mutate(self):
		random.seed()
		self._coeff = random.randint(self._min_coeff,self._max_coeff)
	
	def setPower(self, power):
		self._power = power
	
	def getPower(self):
		return self._power
	
	def getDescription(self):
		string = "%s, %s: Response = %d * (variable)^%d" % (self._type, self._subtype, self._coeff, self._power)
		return string
	
	def getType(self):
		return self._type
		
class SineSolution(SolutionModuleInterface):
	def __init__(self):
		self._coeff = 0
		self._min_coeff = -1000
		self._max_coeff = 1000
		self._type = "Equation"
		self._subtype = "Sine"

	def getFitness(self, fitness_power):
		variable, desire = fitness_power.getConditions()
		response = self.getResponse(variable)
		fitness = -abs(response - desire)
		return fitness
		
	def getResponse(self, variable):
		return self._coeff * math.sin(variable)
		
	def mutate(self):
		random.seed()
		self._coeff = random.randint(self._min_coeff,self._max_coeff)
	
	def getDescription(self):
		string = "%s, %s: Response = %d * sine(variable)" % (self._type, self._subtype, self._coeff)
		return string

class LogSolution(SolutionModuleInterface):
	def __init__(self):
		self._coeff = 0
		self._min_coeff = -1000
		self._max_coeff = 1000
		self._base = 10
		self._type = "Equation"
		self._subtype = "Log"

	def getResponse(self, variable):
		return self._coeff * math.log(variable, self._base)

	def getFitness(self, fitness_power):
		variable, desire = fitness_power.getConditions()
		response = self.getResponse(variable)
		fitness = -abs(response - desire)
		return fitness
	
	def mutate(self):
		random.seed()
		self._coeff = random.randint(self._min_coeff,self._max_coeff)
	
	def setBase(self, base):
		self._base = base
	
	def getBase(self):
		return self._base

	def getDescription(self):
		string = "%s, %s: Response = %d * log[base %d](variable)" % (self._type, self._subtype,self._coeff, self._base)
		return string

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
