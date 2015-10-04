import inspect, random, math
from copy import deepcopy
from evonum_mutations import *
from evonum_modules import *


def error():
	raise NotImplementedError, "%s not implemented" % inspect.stack()[1][3]
	
class SolverInterface(object):
	def mutate(self): #Returns nothing
		error()
	def clone(self): #Returns clone
		error()
	def reproduce(self): #Returns progeny of solver type
		error()
	def getDetails(self): #Returns string
		error()
	def softReset(self): #Resets name, age, and children
		error()
	def hardReset(self): #Resets all properties to default
		error()
	def beginDay(self): #Returns False if Individual has died and must be removed.
		error()
	def calculateFitness(self, fitness_forces): #Returns nothing, accepts a list of fitness forces
		error()
	def getFitness(self): #Returns floating-point fitness score
		error()
	def Death(self): #Returns nothing
		error()
		
class LinearSolver(SolverInterface):
	def __init__(self, name="Unnamed Linear Solver"):
		#Static properties
		self._fitness = 0
		self._lifespan = 100
		self._living = True
		self._max_modules = 10
		self._name = name
		self._age = 0
		self._children = 0
		self._modules = []
		self._property_chances = [5,10,10,0] #Index correlations: 0 = spread, 1 = total_modules, 2 = module_mutation_chance, 3 = property_mutation_chance; These are hard-coded for individual and cannot mutate.

		#Mutatable properties
		self._spread = 10
		self._total_modules = 5
		self._module_mutation_chance = 50
		self._property_mutation_chance = 10

	def setSpread(self, spread):
		self._spread = spread
	
	def clone(self):
		return deepcopy(self)
	
	def reproduce(self):
		clone = self.clone()
		self._children += 1
		child_name = self._name + ".%d" % self._children
		clone.softReset(child_name)
		clone.mutate()
		return clone
	
	def softReset(self, new_name="Unnamed Linear Solver"):
		self._name = new_name
		self._children = 0
		self._age = 0
		self._fitness = 0

	def hardReset(self, new_name="Unnamed Linear Solver"):
		self.softReset
		self._modules = {}
		self._max_modules = 5
		self._spread = 10
		self._module_mutation_chance = 50
		self._property_mutation_chance = 10
	
	def mutate(self):
		random.seed()
		chances = [random.randint(1,100)]
		for x in range(0, len(self._modules)):
			chances.append(random.randint(1,100))
#		print "Mutation chances:",", ".join(str(x) for x in chances)
		
		# Mutate Solver properties with set chance
		if chances[0] <= self._property_mutation_chance:
			self.mutateProperty()
		
		#Mutate each module with a set chance to mutate
		for x in range(0, len(self._modules)):
			if chances[x+1] <= self._module_mutation_chance:
#				print "%s: Mutating module #%d" % (self._name, (x+1))
				self._modules[x].mutate()
		
	def mutateProperty(self):
		random.seed()
		selection = random.randint(1,100)
		if selection <= self._property_chances[0]: #Mutate spread
#			print "%s: Mutating Spread" % self._name
			self._spread = Mutations.GaussianMutation(self._spread, 1 if self._spread==0 else self._spread) #Make sure that there is always a chance for some degree of mutation
			if self._spread < 0: 
				self_spread = 0
			elif self._spread > 1000: 
				self._spread = 1000
			for item in self._modules:
				item.updateSpread(self._spread)
		elif selection <= sum(self._property_chances[0:2]): #Mutate total modules
#			print "%s: Mutating Total Modules" % self._name
			self._total_modules = int(Mutations.GaussianMutation(self._total_modules, self._spread*self._total_modules/100)+.5)
			if self._total_modules > self._max_modules:
				self._total_modules = self._max_modules
			elif self._total_modules < 1:
				self._total_modules = 1
		elif selection <= sum(self._property_chances[0:3]): #Mutate module mutation chance
#			print "%s: Mutating Module Mutation Chance" % self._name
			self._module_mutation_chance = Mutations.GaussianMutation(self._module_mutation_chance, self._spread*self._module_mutation_chance/100)
			if self._module_mutation_chance > 100: 
				self._module_mutation_chance = 100
			elif self._module_mutation_chance < 0:
				self._module_mutation_chance = 0
		elif selection <= sum(self._property_chances): #Mutate property mutation chance
#			print "%s: Mutating Property Mutation Chance" % self._name
			self._property_mutation_chance = Mutations.GaussianMutation(self._property_mutation_chance, self._spread*self._property_mutation_chance/100)
			if self._property_mutation_chance > 100:
				self._property_mutation_chance = 100
			elif self._property_mutation_chance < 0:
				self._property_mutation_chance = 0			
			
	def beginDay(self):
		if self._age > self._lifespan:
			self.Death()

		if self._living:
			self._age += 1
			self._fitness = 0
			
			#Check if there are too many or too few modules (Can occure after total_modules has been mutated or when no-parent solver is born)
			if len(self._modules) < self._total_modules:
#				print "Adding modules, Current: %d, Total: %d" % (len(self._modules), self._total_modules)
				for x in range (0, self._total_modules - len(self._modules)):
					self._modules.append(ModuleFactory.generateNewModule("Fitness", "Random"))
			elif len(self._modules) > self._total_modules:
					for x in range(0, len(self._modules) - self._total_modules):
						self._modules.pop() #Last module added is most susceptible to loss.

			for item in self._modules:
				item.updateSpread(self._spread)

			return True
		
		else:
			return False
	
	def calculateFitness(self, fitness_forces): #Linear solver adds up fitness types
		for item in fitness_forces:
			self._fitness += self.calculateUnitFitness(item)

	def calculateUnitFitness(self, force):
		if force.getType() == "Simple":
			running_total = 0 #Linear solver adds up all module responses before calculating fitness
			responded = False
			variable, expected = force.getConditions()
			for item in self._modules:
				if item.getType() == "Fitness":
					running_total += item.getResponse(variable)
					responded = True
		else: #If it is an unrecognizable fitness force
			return force.getPenalty()

		if responded:
			return -abs(expected - running_total)
		if not responded: #If it has no modules capable of dealing with the recognized force
			return force.getPenalty()
	
	def getFitness(self):
		return self._fitness
		
	def Death(self):
		self._living = False
	
	def getDescription(self):
		desc = "-"*30+"\n"
		if len(self._name) > 50:
			name = self._name[:30]+"..."+self._name[-3:]
		desc += "%s, Age: %d, Children: %d" % (name, self._age, self._children)
		if len(self._modules) == 0:
			desc += "\nNo modules."
		else:
			desc += "\nModules:"
			for item in self._modules:
				desc += "\n%s" % item.getDescription()
		desc += "\n"+"-"*30
		return desc
	
	def getName(self):
		return self._name		
