import inspect, random, math
from copy import deepcopy
from evonum_mutations import *
from evonum_modules import *

def error():
	raise NotImplementedError, "%s not implemented" % inspect.stack()[1][3]

class SolverFactory(object):
	solver_types = ["Small"]
	@classmethod
	def DefineSolver(self,options):
		if options["Type"]=="Small":
			new_solver = SmallSolver()
			try: new_solver._name = options["Name"]
			except: pass
			try: new_solver._unique = True if options["Unique"]=="True" else False
			except: pass
			try: new_solver._lifespan = int(options["Lifespan"])
			except: pass
			if "Calculator" in options and options["Calculator"]=="Linear":
				new_solver._fitness_calculator = LinearFitness()
			elif "Calculator" in options and options["Calculator"] == "Dynamic":
				new_solver._fitness_calculator = DynamicFitness()
			try: new_solver._spread = options["Spread"]
			except: pass
			try:
				new_solver._total_modules = len(options["Modules"])
				for item in options["Modules"]:
					new_solver.addModule(item.split(",")[0], item.split(",")[1])	
			except: pass
			try: new_solver._module_mutation_chance = float(options["ModuleMutationChance"])
			except: pass
			try: new_solver._property_mutation_chance = float(options["PropertyMutationChance"])
			except: pass
			
		else:
			assert "Unable to import unrecognized main solver type"
		return new_solver
	@classmethod
	def newSolver(self, solver_type, name):
		if solver_type == "Small":
			new_solver = SmallSolver(name)
			return new_solver
			self._solvers.append(new_solver)
	
	@classmethod
	def importSolver(self, solver_dict):
		solver_dict["_name"] += "|Imported|"
		new_solver = self.newSolver(solver_dict["_type"], solver_dict["_name"])
#		try:
		new_solver.importDict(solver_dict)
#		except:
#			print "Unable to import solver; Name = %s, Type = %s" % (solver_dict["_name"], solver_dict["_type"])
		return new_solver
			
class FitnessCalculator(object):
	def calculateFitness(self, fitness_forces, modules): #Overall fitness is the sum of fitness scores for each type of fitness
		fitness = 0
		for item in fitness_forces:
			fitness += self.calculateUnitFitness(item, modules)
		return fitness

	def calculateUnitFitness(self, force, modules): #Different depending on what kind of fitness calculator the solver uses
		error()
		
class LinearFitness(FitnessCalculator): #Linear solver adds up all module responses before calculating fitness
	def calculateUnitFitness(self, force, modules):
		if force.getType() == "Simple":
			running_total = 0
			responded = False
			variable, expected = force.getConditions()
			for item in modules:
				running_total += item.getResponse(variable)
				responded = True
		else: #If it is an unrecognizable fitness force
			return force.getPenalty()

		if responded:
			return -abs(expected - running_total)
		else: #If it has no modules capable of dealing with the recognized force
			return force.getPenalty()
			
class DynamicFitness(FitnessCalculator): #Randomly selects modules to calculate fitness and adds up responses before calculating fitness
	def calculateUnitFitness(self, force, modules):
		if force.getType() == "Simple":
			running_total = 0
			responded = False
			variable, expected = force.getConditions()
			num_modules_used = random.randint(max(1,int(len(modules)/2)), int(1.5*len(modules)+.5)) #Randomly determine the number of modules used between 1/2 total modules to 1.5 * total modules (at least 1 module)
			for x in range(0,num_modules_used):
				running_total += random.choice(modules).getResponse(variable)
				responded = True

		else: #If it is an unrecognizable fitness force
			return force.getPenalty()

		if responded:
			return -abs(expected - running_total)
		if not responded: #If it has no modules capable of dealing with the recognized force
			return force.getPenalty()

		
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
	def softReset(self, new_name): #Resets name, age, and children, returns nothing
		error()
	def hardReset(self): #Resets all properties to default, returns nothing
		error()
	def beginDay(self): #Returns False if Individual has died and must be removed.
		error()
	def calculateFitness(self, fitness_forces): #Returns nothing, accepts a list of fitness forces
		error()
	def getFitness(self): #Returns floating-point fitness score
		error()
	def Death(self): #Returns nothing
		error()
		
class SmallSolver(SolverInterface):
	def __init__(self, name="Unnamed Linear Solver"):
		#Static properties
		self._type = "Small"
		self._fitness = 0
		self._lifespan = 100
		self._living = True
		self._max_modules = 15
		self._name = name
		self._age = 0
		self._children = 0
		self._modules = []
		self._property_chances = [.1,10,10,10] #Index correlations: 0 = spread, 1 = total_modules, 2 = module_mutation_chance, 3 = property_mutation_chance; These are hard-coded for individual and cannot mutate.
		self._unique = True if random.randint(1,2) == 1 else False #Each solver has a 50% chance of being a unique-module solver
		self._fitness_calculator = LinearFitness()

		#Mutatable properties
		self._spread = 10
		self._total_modules = 5
		self._module_mutation_chance = 50
		self._property_mutation_chance = 10
		self._swap_module_mutation_chance = 15 #Chance for a module that will be mutated to swap out with a new module of different subtype instead of mutating.
		self._merge_mutation_chance = 50

	def setSpread(self, spread):
		self._spread = spread
	
	def clone(self):
		return deepcopy(self)
	
	def reproduce(self):
		clone = self.clone()
		self._children += 1
		child_name = self._name.split(".")[0]+"."+str(int(self._name.split(".")[1])+1)
		clone.softReset(child_name)
		clone.mutate()
		return clone
	
	def softReset(self, new_name="Unnamed Small Solver"):
		self._name = new_name
		self._children = 0
		self._age = 0
		self._fitness = 0

	def hardReset(self, new_name="Unnamed Small Solver"):
		self.softReset
		self._modules = {}
		self._max_modules = 5
		self._spread = 10
		self._module_mutation_chance = 50
		self._property_mutation_chance = 10
	
	def mutate(self):
		chances = [random.randint(1,100),random.randint(1,100)] #chances[0] = chance to mutate property
		for x in range(0, len(self._modules)):
			chances.append(random.randint(1,100)) #chances[2-N] = chance to mutate each module for N modules
		
		chances.append(random.randint(1,100)) #chances[N+1] = chance to merge two properties of same type (if not _unique)
		
#		print "Mutation chances:",", ".join(str(x) for x in chances)
		
		# Mutate Solver properties with set chance
		if chances[0] <= self._property_mutation_chance:
			self.mutateProperty()
		
		#Mutate each module with a set chance to mutate
		for x in range(0, len(self._modules)):
			if chances[x+1] <= self._module_mutation_chance:
#				print "%s: Mutating module #%d" % (self._name, (x+1))
				if random.randint(1,100) <= self._swap_module_mutation_chance:
#					print "swapping out",self._modules[x].getSubtype()
					if not self._unique:
						self._modules[x] = ModuleFactory.generateUniqueModule("Fitness",[self._modules[x].getSubtype()])
					else:
						present_subtypes = [y.getSubtype() for y in self._modules]
						self._modules[x] = ModuleFactory.generateUniqueModule("Fitness",present_subtypes)
#					print "swapping in",self._modules[x].getSubtype()
				else:
					self._modules[x].mutate()
		
#		if chances[-1] <= self._merge_mutation_chance and not self._unique: #TODO: change back?
		if chances[-1] <= self._merge_mutation_chance:
			self.mergeModules()
		
	def mutateProperty(self):
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
					self.addModule()
			elif len(self._modules) > self._total_modules:
					for x in range(0, len(self._modules) - self._total_modules):
						self._modules.pop() #Last module added is most susceptible to loss.

			for item in self._modules:
				item.updateSpread(self._spread)

			return True
		
		else:
			return False
	
	def addModule(self):
		if not self._unique:
			self._modules.append(ModuleFactory.generateNewModule("Fitness", "Random"))
		
		else:
			present_subtypes = [x.getSubtype() for x in self._modules]
			self._modules.append(ModuleFactory.generateUniqueModule("Fitness",present_subtypes))
	
	def calculateFitness(self, fitness_forces): 
		self._fitness = self._fitness_calculator.calculateFitness(fitness_forces, self._modules)

	def setFitnessCalculator(self, calculator):
		self._fitness_calculator = calculator
	
	def getFitness(self):
		return self._fitness
		
	def Death(self):
		self._living = False
	
	def getDescription(self):
		desc = "-"*30+"\n"
		if len(self._name) > 50:
			name = self._name[:30]+"..."+self._name[-3:]
		else:
			name = self._name
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
	
	def export(self):
		identity = dict(self.__dict__)
		identity["_modules"] = []
		identity["_fitness_calculator"] = "Linear"
		identity["_type"] = "Small"
		for item in self._modules:
			identity["_modules"].append(item.export())
		return identity
	
	def importDict(self, identity):
		self.__dict__.update(identity)
		imported_modules = []
		for item in identity["_modules"]:
			imported_modules.append(ModuleFactory.importModule(item))
		self._modules = imported_modules
		if identity["_fitness_calculator"] == "Linear":
			self._fitness_calculator = LinearFitness()
	
	def mergeModules(self): #Merge the first two modules found that have the same subtype and add a unique module in the second one's place
		module_subtypes = {}
		for i, item in enumerate(self._modules):
			if item.getSubtype() in module_subtypes:
#				print "Merging modules of subtypes:", item.getSubtype()
#				print "Before merge:"
#				print self.getDescription()
				new_modules = ModuleFactory.mergeFitnessModules(self._modules[i], self._modules[module_subtypes[item.getSubtype()]])
				self._modules[module_subtypes[item.getSubtype()]] = new_modules[0]
				self._modules[i] = new_modules[1]
#				print "After merge:"
#				print self.getDescription()
				break
			else:
				module_subtypes[item.getSubtype()] = i
				
	def isAlive(self):
		return self._living
	
	def importAttributes(self, settings):
		for item in attributes:
			setattr(self, item, attributes[item])
