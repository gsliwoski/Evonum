from __future__ import print_function
import inspect
import math, random
#from evonum_god import God
from evonum_mutations import *

def error():
	raise NotImplementedError("%s not implemented" % inspect.stack()[1][3]) #Used for interface

class ModuleFactory(object):
	module_subtypes = ["Power_1", "Power_2", "Power_3", "Power_4", "Power_5", "Log", "Ln", "Sine_1", "Sine_2", "Sine_3", "Sine_4", "Sine_5", "Cosine_1", "Cosine_2", "Cosine_3", "Cosine_4", "Cosine_5"] #TODO: Make dynamic
#	module_subtypes = ["Power_1", "Power_2", "Power_3", "Power_4", "Power_5"]
#	module_subtypes = ["Sine_1", "Sine_2", "Sine_3", "Sine_4", "Sine_5", "Cosine_1", "Cosine_2", "Cosine_3", "Cosine_4", "Cosine_5"]
	max_power = 5
	min_power = -5
	@classmethod
	def generateNewModule(self, module_type, module_subtype):
		if module_type == "Fitness":
			if module_subtype == "Random":
				module_subtype = self.module_subtypes[random.randint(1,len(self.module_subtypes))-1]
			if module_subtype.startswith("Power"):
				new_module = PowerSolution()
				if module_subtype != "Power":
					new_module.setPower(int(module_subtype.split("_")[1]))
			elif module_subtype.startswith("Sine"):
				new_module = SineSolution()
				if module_subtype != "Sine":
					new_module.setPower(int(module_subtype.split("_")[1]))
			elif module_subtype == "Log":
				new_module = LogSolution()
			elif module_subtype == "Ln":
				new_module = NaturalLogSolution()
			elif module_subtype.startswith("Cosine"):
				new_module = CosineSolution()
				if module_subtype != "Cosine":
					new_module.setPower(int(module_subtype.split("_")[1]))
		return new_module
	
	@classmethod
	def generateUniqueModule(self, module_type, present_subtypes): #Generate a module not already part of the present subtypes, used for merging and for solvers with unique True
		if module_type == "Fitness":
			potential_subtypes = []
			for item in self.module_subtypes:
				if item not in present_subtypes:
					potential_subtypes.append(item)
			try:
				sel = random.choice(potential_subtypes)
			except:
				sel = "Random"
			return self.generateNewModule(module_type, sel)
	@classmethod		
	def mergeFitnessModules(self, module_a, module_b): #Merge modules and return a new module of a subtype different from the two merged. If unable to merge modules, returns them unchanged.
		if module_a.getType() == "Fitness" and module_b.getType() == "Fitness":
			if module_a.getSubtype() == module_b.getSubtype():
				merged_module = self.generateNewModule(module_a.getType(), module_a.getSubtype())
				module_a_vals = module_a.getValues()
				module_b_vals = module_b.getValues()
				combined_vals = {}
				for item in module_a_vals:
					combined_vals[item] = module_a_vals[item]+module_b_vals[item]
				merged_module.setValues(combined_vals)
				new_module = self.generateUniqueModule("Fitness",merged_module.getSubtype())
				return merged_module, new_module
			else:
				print ("Failed to merge modules of different subtypes.")
				return module_a, module_b
		else:
			print ("Failed to merge non-fitness modules with mergeFitnessModules.")
			return module_a, module_b

	@classmethod
	def importModule(self, module_dict): #Import predefined module based on its object dictionary.
		new_module = self.generateNewModule(module_dict["_type"], module_dict["_subtype"])
		new_module.importDict(module_dict)
		return new_module
							
class ModuleInterface(object):
	def mutate():
		error()
	def getResponse(self, variable):
		error()
	def updateSpread(self, spread):
		error()
	def getDescription(self):
		error()

class FitnessModuleInterface(object):
	def mutate():
		error()
	def getResponse(self, fitness_power): #returns float calculation of response based on fitness variable
		error()
	def getType(self): #Returns string type
		error()
	def getSubtype(self): #Returns string subtype
		error()
	def setValues(self, value_dictionary): #Accepts dictionary of mutatable values for module. Returns True on success, false on failure.
		error()
	def getValues(self): #returns a dictionary of parameters and their current values that are mutatable.
		error()

class PowerSolution(FitnessModuleInterface): #Returns N * x^P where N is a mutatable coefficient and P is a power, either randomly selected or assigned. 
	def __init__(self):
		self._power = random.randint(1,5) #Randomly select starting power
		self._min_coeff = -100
		self._max_coeff = 100
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff) #Randomly select starting coefficient
		self._type = "Fitness"
		self._subtype = "Power_"+str(self._power)
		self._spread = 0
	
	def getResponse(self, variable):
		return self._coeff * pow(variable, self._power)
	
	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
#Works better without enforcing max and min cutoff.
#		if self._coeff < self._min_coeff:
#			self._coeff = self._min_coeff
#		elif self._coeff > self._max_coeff:
#			self._coeff = self._max_coeff
	
	def setPower(self, power):
		self._power = power
		self._subtype = "Power_"+str(self._power)
	
	def getPower(self):
		return self._power
	
	def getDescription(self):
		string = "%s, %s: Response = %.4f * (variable)^%d" % (self._type, self._subtype, self._coeff, self._power)
		return string
	
	def getType(self):
		return self._type
	
	def getSubtype(self):
		return self._subtype
	
	def updateSpread(self, spread):
		self._spread = spread #TODO: Try allowing modules to have their own mutatable spreads.
	
	def setValues(self, value_dictionary):
		try:
			for item in value_dictionary:
				if item == "coeff":
					self._coeff = float(value_dictionary["coeff"])
			return True
		except:
			return False
	
	def getValues(self):
		vals = {"coeff": self._coeff}
		return vals		
	
	def export(self):
		return dict(self.__dict__)
	
	def importDict(self, identity):
		self.__dict__.update(identity)
		
class SineSolution(FitnessModuleInterface): #Returns N * sine^P(x). N is mutatable, P is assigned.
	def __init__(self):
		self._min_coeff = -100
		self._max_coeff = 100
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
		self._type = "Fitness"
		self._pow = random.randint(1,5) #randomly select power
		self._subtype = "Sine"+"_"+str(self._pow)
		self._spread = 0

	def setPower(self, power):
		self._pow = power
		self._subtype =	"Sine"+"_"+str(self._pow)
	
	def getResponse(self, variable):
		return self._coeff * pow(math.sin(variable),self._pow)
		
	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
#		if self._coeff < self._min_coeff:
#			self._coeff = self._min_coeff
#		elif self._coeff > self._max_coeff:
#			self._coeff = self._max_coeff

	
	def getDescription(self):
		string = "%s, %s: Response = %.2f * sine^%d(variable)" % (self._type, self._subtype, self._coeff, self._pow)
		return string
	
	def getType(self):
		return self._type
	
	def getSubtype(self):
		return self._subtype
	
	def updateSpread(self, spread):
		self._spread = spread
	
	def setValues(self, value_dictionary):
		try:
			for item in value_dictionary:
				if item == "coeff":
					self._coeff = float(value_dictionary["coeff"])
			return True
		except:
			return False
	
	def getValues(self):
		vals = {"coeff": self._coeff}
		return vals
	
	def export(self):
		return dict(self.__dict__)
	
	def importDict(self, identity):
		self.__dict__.update(identity)

class CosineSolution(FitnessModuleInterface): #Returns N * cosine^P(x)
	def __init__(self):
		self._min_coeff = -100
		self._max_coeff = 100
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
		self._type = "Fitness"
		self._pow = random.randint(1,5) #randomly select power
		self._subtype = "Cosine"+"_"+str(self._pow)

		self._spread = 0

	def setPower(self, power):
		self._pow = power
		self._subtype = "Cosine"+"_"+str(self._pow)
	
	def getResponse(self, variable):
		return self._coeff * pow(math.cos(variable),self._pow)
		
	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
#		if self._coeff < self._min_coeff:
#			self._coeff = self._min_coeff
#		elif self._coeff > self._max_coeff:
#			self._coeff = self._max_coeff
	
	def getDescription(self):
		string = "%s, %s: Response = %.2f * cosine^%d(variable)" % (self._type, self._subtype, self._coeff, self._pow)
		return string
	
	def getType(self):
		return self._type
	
	def getSubtype(self):
		return self._subtype
	
	def updateSpread(self, spread):
		self._spread = spread
	
	def setValues(self, value_dictionary):
		try:
			for item in value_dictionary:
				if item == "coeff":
					self._coeff = float(value_dictionary["coeff"])
			return True
		except:
			return False
	
	def getValues(self):
		vals = {"coeff": self._coeff}
		return vals
	
	def export(self):
		return dict(self.__dict__)
	
	def importDict(self, identity):
		self.__dict__.update(identity)

class LogSolution(FitnessModuleInterface): #Returns N * log10(x) #TODO: Try allowing log base to be assigned like powers.
	def __init__(self):
		self._min_coeff = -100
		self._max_coeff = 100
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
		self._base = 10
		self._type = "Fitness"
		self._subtype = "Log"
		self._spread = 0

	def getResponse(self, variable):
		try:
			return self._coeff * math.log(variable, self._base)
		except:
			return 0

	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
#		if self._coeff < self._min_coeff:
#			self._coeff = self._min_coeff
#		elif self._coeff > self._max_coeff:
#			self._coeff = self._max_coeff
	
	def setBase(self, base):
		self._base = base
	
	def getBase(self):
		return self._base

	def getDescription(self):
		string = "%s, %s: Response = %.2f * log[base %d](variable)" % (self._type, self._subtype,self._coeff, self._base)
		return string
	
	def getType(self):
		return self._type
	
	def getSubtype(self):
		return self._subtype
	
	def updateSpread(self, spread):
		self._spread = spread
	
	def setValues(self, value_dictionary):
		try:
			for item in value_dictionary:
				if item == "coeff":
					self._coeff = float(value_dictionary["coeff"])
			return True
		except:
			return False
	
	def getValues(self):
		vals = {"coeff": self._coeff}
		return vals	
	
	def export(self):
		return dict(self.__dict__)
	
	def importDict(self, identity):
		self.__dict__.update(identity)
		
class NaturalLogSolution(FitnessModuleInterface): #Returns N * ln(X)
	def __init__(self):
		self._min_coeff = -100
		self._max_coeff = 100
		self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
		self._type = "Fitness"
		self._subtype = "Ln"
		self._spread = 0
	
	def getResponse(self, variable):
		try:
			return self._coeff * math.log(variable)
		except:
			return 0
	
	def mutate(self):
		self._coeff = Mutations.GaussianMutation(self._coeff, self._spread)
#		if self._coeff < self._min_coeff:
#			self._coeff = self._min_coeff
#		elif self._coeff > self._max_coeff:
#			self._coeff = self._max_coeff
		
	def updateSpread(self, spread):
		self._spread = spread
	
	def getType(self):
		return self._type
	
	def getSubtype(self):
		return self._subtype
	
	def getDescription(self):
		string = "%s, %s: Response = %.2f * Ln(variable)" % (self._type, self._subtype,self._coeff)
		return string

	def setValues(self, value_dictionary):
		try:
			for item in value_dictionary:
				if item == "coeff":
					self._coeff = float(value_dictionary["coeff"])
			return True
		except:
			return False
	
	def getValues(self):
		vals = {"coeff": self._coeff}
		return vals
	
	def export(self):
		return dict(self.__dict__)

	def importDict(self, identity):
		self.__dict__.update(identity)
