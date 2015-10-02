import inspect
import math, random, collections
from copy import deepcopy
from evonum_god import God
from evonum_module import *

class IndividualInterface(object):
	def clone(self):
		error()
	def mutate(self):
		error()
	def calculateFitness(self, fitness):
		error()
	def getFitness(self):
		error()
	def setFitness(self, fitness):
		error()
	def getSize(self):
		error()
	def reproduce(self):
		error()
	def addModule(self, module_type):
		error()
	def getDescription(self):
		error()
	def beginDay(self):
		error()
		
class Solver(IndividualInterface):
	def __init__(self, name):
		self._modules = {"Internal": [Maturity()]}
		self._fitness = -9999
		self._max_modules = 5
		self._size = self._max_modules / 5
		self._module_types = ["Equation"] #all available module types
		self._module_subtypes = {"Equation": ["Power", "Sine", "Log"]}
		self._age = 0
		self._name = name
		self._moduleFactory = ModuleGenerator()

	def clone(self):
		return deepcopy(self)
	
	def getFitness(self):
		return self._fitness

	def setFitness(self, fitness):
		self._fitness = fitness
	
	def calculateUnitFitness(self, force):
		fitness = 0
		if force.getType() not in self._modules:
			return force.getPenalty()
		else:
			for item in self._modules[force.getType()]:
				fitness += item.getFitness(force)
		return fitness
	
	def mutate(self):
		pass
		
	def getSize(self):
		return self._size
	
	def addModule(self, module_type, module_subtype = "Random"):
		if len(self._modules) < self._max_modules:
			if module_type == "Random":
				random.seed()
				module_type = self._module_types[random.randint(0, len(self._module_types)-1)]
			if module_subtype == "Random":
				module_subtype = self._module_subtypes[module_type][random.randint(0, len(self._module_subtypes[module_type])-1)]
			new_module = self._moduleFactory.generateNewModule(module_type, module_subtype)
			if module_type in self._modules:
				self._modules[module_type].append(new_module)
			else:
				self._modules[module_type] = [new_module]

		else:
			print "Max modules reached"
	
	def getDescription(self):
		string = "Solver %s, age=%d\n" % (self._name, self._age)
		if len(self._modules) == 0:
			string += "No modules."
		else:
			string += "Modules:"
			for item in self._modules:
				string +="\n"+"\n".join([x.getDescription() for x in self._modules[item]])
		return string

	def beginDay(self):
		self._age += 1
				
	
