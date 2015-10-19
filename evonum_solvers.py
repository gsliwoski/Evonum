from __future__ import print_function
import inspect
import random
import math
from copy import deepcopy
from evonum_mutations import *
from evonum_modules import *


def error():
    raise NotImplementedError("%s not implemented" %
                              inspect.stack()[1][3])  # Used for interface

def createSolver(solver_type, name, conditions=None):
    """Returns a new solver of supplied type and supplied name
    
    Option third argument is a dictionary of mutatable attributes to import
    """
    
    if solver_type == "Small":
        new_solver = SmallSolver(name, conditions)
    else:
        assert("Unable to create new solver of type: %s" % solver_type)
        new_solver = None
    return new_solver

def importSolver(solver_dict): #TODO: Pickle
    """Import serialized solver"""
    solver_dict["_name"] += "|Imported|"
    new_solver = createSolver(solver_dict["_type"], solver_dict["_name"])
    new_solver.importDict(solver_dict)
    return new_solver


class FitnessCalculator(object):

    # Overall fitness is the sum of fitness scores for each type of fitness
    def calculateFitness(self, fitness_forces, modules):
        fitness = 0
        for item in fitness_forces:
            fitness += self.calculateUnitFitness(item, modules)
        return fitness

    # Different depending on what kind of fitness calculator the solver uses
    def calculateUnitFitness(self, force, modules):
        error()


# Linear solver adds up all module responses before calculating fitness
class LinearFitness(FitnessCalculator):

    def calculateUnitFitness(self, force, modules):
        if force.type_ == "Simple" or force.type_ == "Dynamic":
            running_total = 0
            responded = False
            variable, expected = force.conditions
            for item in modules:
                running_total += item.getResponse(variable)
                responded = True
        else:  # If it is an unrecognizable fitness force
            return force.penalty

        if responded:
            return -abs(expected - running_total)
        else:  # If it has no modules capable of dealing with the recognized force
            return force.penalty


# Randomly selects modules to calculate fitness and adds up responses
# before calculating fitness
class DynamicFitness(FitnessCalculator):

    def calculateUnitFitness(self, force, modules):
        if force.type_ == "Simple" or force.type_ == "Dynamic":
            running_total = 0
            responded = False
            variable, expected = force.conditions
            # Randomly determine the number of modules used between 1/2 total
            # modules to 1.5 * total modules (at least 1 module)
            num_modules_used = random.randint(
                max(1, int(len(modules) / 2)), int(1.5 * len(modules) + .5))
            for x in range(0, num_modules_used):
                running_total += random.choice(modules).getResponse(variable)
                responded = True

        else:  # If it is an unrecognizable fitness force
            return force.penalty

        if responded:
            return -abs(expected - running_total)
        if not responded:  # If it has no modules capable of dealing with the recognized force
            return force.penalty


class SolverInterface(object):

    # Returns nothing
    def mutate(self):  
        error()

    # Returns clone
    def clone(self):  
        error()

    # Returns progeny of solver type
    def reproduce(self):  
        error()

    # Returns string of important properties
    def getDescription(self):  
        error()

    # Resets only properties that progeny need reset (ex: name, age, children)
    def softReset(self, new_name):  
        error()

    # Returns False if Individual has died and must be removed.
    def beginDay(self):
        error()

    # Returns nothing, accepts a list of fitness forces
    def calculateFitness(self, fitness_forces):
        error()

    # Returns nothing
    def Death(self):  
        error()

    # Property management
    @property
    def name(self):
        return self._name
    
    @property
    def living(self):
        """False if solver is over age limit or failed fitness test"""
        return self._living
    
    @property
    def age(self):
        return self._age

    @property
    def fitness(self):
        """Fitness score is used to rank solvers and determine survivors"""
        return self._fitness
    
    @property
    def lifespan(self):
        """Max age in days before living = False"""
        return self._lifespan

class SmallSolver(SolverInterface):

    def __init__(self, name="Unnamed Linear Solver", conditions=None):
        # Static properties
        self._type = "Small"
        self._fitness = 0
        self._lifespan = 100
        self._living = True
        self._max_modules = 15
        self._name = name
        self._age = 0
        self._children = 0
        self._modules = []

        # Index correlations: 0 = spread, 1 = total_modules, 
        # 2 = module_mutation_chance, 3 = property_mutation_chance; These are
        # hard-coded for individual and cannot mutate.
        self._property_chances = [.1, .5, 10, 10]

        # Each solver has a 50% chance of being a unique-module solver
        self._unique = True if random.randint(1, 2) == 1 else False
        
        # Determines the way modules are connected to calculate response
        self._fitness_calculator = LinearFitness()

        # Mutatable properties
        self._spread = 10
        self._total_modules = 5
        self._module_mutation_chance = 50
        self._property_mutation_chance = 10
        self._swap_module_chance = 15
        self._merge_mutation_chance = 50

        if conditions is not None:
            self.importAttributes(conditions)
    
    #Property management
    @property        
    def spread(self):
        """Controls the width of gaussian mutations; Mutatable"""
        return self._spread
    
    @spread.setter
    def spread(self, value):
        if value < 0:
            value = 0
        elif value > 1000:
            value = 1000
        self._spread = value
    
    @property
    def total_modules(self):
        """Current number of modules in a solver; Mutatable"""
        return self._total_modules
    
    @total_modules.setter
    def total_modules(self, value):
        if value > self._max_modules:
            value = self._max_modules
        elif value < 1:
            value = 1
        self._total_modules = value
   
    @property
    def module_mutation_chance(self):
        """Percent chance each module has of mutating during reproduction; Mutatable"""
        return self._module_mutation_chance
    
    @module_mutation_chance.setter
    def module_mutation_chance(self, value):
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        self._module_mutation_chance = value
    
    @property
    def property_mutation_chance(self):
        """Percent chance one of the mutatable properties will mutate; Mutatable"""
        return self._property_mutation_chance
    
    @property_mutation_chance.setter
    def property_mutation_chance(self, value):
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        self._property_mutation_chance = value
    
    @property
    def swap_module_chance(self):
        """Percent chance that a module will be swapped for a module of a different sub-type; Mutatable"""
        return self._swap_module_chance
    
    @swap_module_chance.setter
    def swap_module_chance(self, value):
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        self._swap_module_chance = value
    
    @property
    def merge_module_chance(self):
        """Percent chance two modules of the same subtype will be additively merged; Mutatable"""
        return self._merge_module_chance

    @merge_module_chance.setter
    def merge_module_chance(self, value):
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        self._merge_module_chance = value
    
    @property
    def unique(self):
        """True = module subtypes can not be repeated unless out of new subtypes"""
        return self._unique
    
    @unique.setter
    def unique(self, value):
        if value == "True" or value == 1:
            self._unique = True
        else:
            self._unique = False        

    @property
    def living(self):
        """False = flagged for removal at start of next day"""
        return self._living
    
    @living.setter
    def living(self, value):
        self._living = value

    @property
    def fitness_calculator(self):
        """Method that modules are combined to calculate fitness"""
        return self._fitness_calculator.type_
    
    @fitness_calculator.setter
    def fitness_calculator(self, value):
        if value == "Linear":
            self._fitness_calculator = LinearFitness()
        elif value == "Dynamic":
            self._fitness_calculator = DynamicFitness()
        else:
            assert("Unrecognized fitness calculator type for solver: %s" % value)        
            
    # Reproductive actions
    def clone(self):
        """Return a deepcopy of self"""
        return deepcopy(self)

    # Make a clone, reset name, age, and children, and mutate.
    def reproduce(self):
        """Return a deepcopy of self with fresh name, age, # children and a single mutation. self._children is incremented by 1"""
        clone = self.clone()
        self._children += 1
        child_name = self._name.split(
            ".")[0] + "." + str(int(self._name.split(".")[1]) + 1)
        clone.softReset(child_name)
        clone.mutate()
        clone._age = 1
        return clone

    def softReset(self, new_name="Unnamed Small Solver"):
        """Reset name, age, # children, and unique flag"""
        self._name = new_name
        self._children = 0
        self._age = 0
        self._fitness = 0
        # TODO: Possibly get rid of, testing this:
        self._unique = True if random.randint(1, 2) == 1 else False

    def mutate(self):
        """Randomly mutate solver property and/or module."""
        # chances[0] = chance to mutate property
        chances = [random.randint(1, 100), random.randint(1, 100)]
        for x in range(0, len(self._modules)):
            # chances[2-N] = chance to mutate each module for N modules
            chances.append(random.randint(1, 100))

        # chances[N+1] = chance to merge two properties of same type
        chances.append(random.randint(1, 100))

        # Mutate Solver properties with set chance
        if chances[0] <= self.property_mutation_chance:
            self.mutateProperty()

        # Mutate each module with a set chance to mutate
        for x in range(0, len(self._modules)):
            if chances[x + 1] <= self.module_mutation_chance:
#				print ("%s: Mutating module #%d" % (self._name, (x+1)))
                if random.randint(1, 100) <= self.swap_module_chance:
#					print ("swapping out "+self._modules[x].subtype)
                    if not self.unique:
                        self._modules[x] = createUniqueModule(
                            "Fitness", [self._modules[x].subtype])
                    else:
                        present_subtypes = [y.subtype
                                            for y in self._modules]
                        self._modules[x] = createUniqueModule("Fitness", present_subtypes)
#					print ("swapping in "+self._modules[x].subtype)
                else:
                    self._modules[x].mutate()

        if chances[-1] <= self._merge_mutation_chance:
            self.mergeModules()

    def mutateProperty(self):
        """Mutate a single mutatable property"""
        selection = random.randint(1, 100)
        # Mutate spread
        if selection <= self._property_chances[0]:  
#			print ("%s: Mutating Spread" % self._name)
            # Make sure that there is always a chance for some degree of
            # mutation
            self.spread = Mutations.GaussianMutation(
                self.spread, 1 if self.spread == 0 else self.spread)
            for item in self._modules:
                item.updateSpread(self._spread)
        # Mutate total modules
        elif selection <= sum(self._property_chances[0:2]):
#			print ("%s: Mutating Total Modules" % self._name)
#			print ("Old: %d" % self._total_modules)
#			self._total_modules = int(Mutations.GaussianMutation(self._total_modules, self._spread*self._total_modules/100)+.5)
            self._total_modules = int(Mutations.GaussianMutation(
                self._total_modules, 1))  # hardcode spread to 1 module
#			print ("New: %d" % self._total_modules)
        # Mutate module mutation chance
        elif selection <= sum(self._property_chances[0:3]):
#			print ("%s: Mutating Module Mutation Chance" % self._name)
            self._module_mutation_chance = Mutations.GaussianMutation(
                self._module_mutation_chance, self._spread * self._module_mutation_chance / 100)
        # Mutate property mutation chance
        elif selection <= sum(self._property_chances):
#			print ("%s: Mutating Property Mutation Chance" % self._name)
            self._property_mutation_chance = Mutations.GaussianMutation(
                self._property_mutation_chance, self._spread * self._property_mutation_chance / 100)

    # Survival functions
    def beginDay(self):
        """Return false if no longer living for removal. Increment age. Add or remove modules as needed."""
        if self._age > self._lifespan:
            self.Death()

        if self._living:
            self._age += 1
            self._fitness = 0

            # Check if there are too many or too few modules (Can occure after
            # total_modules has been mutated or when no-parent solver is born)
            if len(self._modules) < self._total_modules:
#				print ("Adding modules, Current: %d, Total: %d" % (len(self._modules), self._total_modules))
                for x in range(0, self._total_modules - len(self._modules)):
                    self.addModule()
            elif len(self._modules) > self._total_modules:
                for x in range(0, len(self._modules) - self._total_modules):
                    # Last module added is most susceptible to loss.
                    self._modules.pop()

            for item in self._modules:
                item.spread = self._spread

            return True

        else:
            return False

    def addModule(self):
        """Add random module to solver"""
        if not self.unique:
            self._modules.append(createModule("Fitness", "Random"))
        else:
            present_subtypes = [x.subtype for x in self._modules]
            self._modules.append(createUniqueModule("Fitness", present_subtypes))

    def calculateFitness(self, fitness_forces):
        """Return and store sum fitness score of each fitness_force in provided list"""
        self._fitness = self._fitness_calculator.calculateFitness(
            fitness_forces, self._modules)

    def Death(self):
        """Flags solver for death at start of next day"""
        self._living = False

    def mergeModules(self):
        """Merge the first two modules found that have the same subtype and add a unique module in the second one's place."""    
        module_subtypes = {}
        for i, item in enumerate(self._modules):
            if item.subtype in module_subtypes:
#				print ("Merging modules of subtypes:", item.subtype)
#				print ("Before merge:")
#				print (self.getDescription())
                new_modules = mergeFitnessModules(self._modules[i], self._modules[module_subtypes[item.subtype]])
                self._modules[module_subtypes[item.subtype]] = new_modules[
                    0]
                self._modules[i] = new_modules[1]
#				print ("After merge:")
#				print (self.getDescription())
                break
            else:
                module_subtypes[item.subtype] = i

    #I/O Functions
    def getDescription(self):
        """Returns string containing important solver properties and modules"""
        desc = "-" * 30 + "\n"
        # Shorten name if too long. TODO: improve naming convention so this isn't needed.
        if len(self._name) > 50:
            name = self._name[:30] + "..." + self._name[-3:]
        else:
            name = self._name
        desc += "%s, Age: %d, Children: %d" % (name, self._age, self._children)
        if len(self._modules) == 0:
            desc += "\nNo modules."
        else:
            desc += "\nModules:"
            for item in self._modules:
                desc += "\n%s" % item.getDescription()
        desc += "\n" + "-" * 30
        return desc

    def export(self):
        """Serialize export solver.""" #TODO: Pickle
        identity = dict(self.__dict__)
        identity["_modules"] = []
        identity["_fitness_calculator"] = "Linear"
        identity["_type"] = "Small"
        for item in self._modules:
            identity["_modules"].append(item.export())
        return identity

    def importDict(self, identity):
        """Serialize import solver""" #TODO: Pickle
        self.__dict__.update(identity)
        imported_modules = []
        for item in identity["_modules"]:
            imported_modules.append(importModule(item))
        self._modules = imported_modules
        if identity["_fitness_calculator"] == "Linear":
            self._fitness_calculator = LinearFitness()

    def importAttributes(self, attributes):
        for item in attributes:
            if item == "spread":
                self.spread = attributes[item]
            elif item == "property_mutation_chance":
                self.property_mutation_chance = attributes[item]
            elif item == "module_mutation_chance":
                self.module_mutation_chance = attributes[item]
            elif item == "total_modules":
                self.total_modules = attributes[item]
            elif item == "swap_module_chance":
                self.swap_module_chance = attributes[item]
            elif item == "merge_module_chance":
                self.merge_module_chance = attributes[item]
            elif item == "unique":
                self.unique = attributes[item]
            else:
                assert("Unrecognized solver attribute: %s" % item)
