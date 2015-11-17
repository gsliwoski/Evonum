from __future__ import print_function
import inspect
import random
import math
import types
from copy import deepcopy
from evonum_mutations import *
from evonum_modules import *


def error():
    raise NotImplementedError("%s not implemented" %
                              inspect.stack()[1][3])  # Used for interface


def badAttribute(attribute, bad_type, solver_name):
    """Error message when attempting to assign new value of bad type to a solver property."""
    print("Error: Bad %s type %s sent to solver %s, returning unchanged." %
          (attribute, bad_type, solver_name))


def createSolver(solver_type="Small", name=None, conditions=None):
    """Returns a new solver of supplied type and supplied name

    Option third argument is a dictionary of mutatable attributes to import
    """

    if solver_type == "Small":
        new_solver = SmallSolver(name, conditions)
    else:
        print("Unknown solver type: %s" % solver_type)
        new_solver = None
    return new_solver


def importSolver(solver_dict):
    """Import serialized solver"""
    if "_type_" not in solver_dict:
        print("Error: solver type must be provided for import, no solver imported.")
        return None
    solver_dict["_type_"] = str(solver_dict["_type_"])
    try:
        solver_dict["name"] = str(solver_dict["name"])
    except KeyError:
        solver_dict["name"] = "NoName"
    new_solver = createSolver(solver_dict["_type_"], solver_dict["name"])
    if new_solver:
        new_solver.importAttributes(solver_dict)
    return new_solver


class FitnessCalculator(object):
    # Overall fitness is the sum of fitness scores for each type of fitness
    
    def mutate(self):
        """Specialized fitness calculators have parameters than can mutate.
        
        Standard fitness calculators do not mutate and mutate calls pass."""
        pass
        
    def calculateFitness(self, fitness_forces, modules):
        """Calculate overall solver fitness.

        Takes list of fitness force objects and list of module objects.
        Returns fitness value.
        Fitness is a sum of individual fitness force scores.
        If solver failed to respond to a fitness force due to math domain error,
        fitness returns None.
        """
        fitness = 0
        for item in fitness_forces:
            response = self.calculateUnitFitness(item, modules)
            if response is None:
                return None
            else:
                fitness += response
        return fitness

    # Different depending on what kind of fitness calculator the solver uses
    def calculateUnitFitness(self, force, modules):
        error()


class LinearFitness(FitnessCalculator):
    """Sums all module responses before calculating fitness."""
    @property
    def type_(self):
        return "Linear"

    def calculateUnitFitness(self, force, modules):
        if force.type_ == "Simple" or force.type_ == "Dynamic":
            self._responded = False
            variable, expected = force.conditions
            response = self.getSimpleResponse(variable, modules)
            if response is None:
                return None
        else:  # If it is an unrecognizable fitness force
            return force.penalty
        if self._responded:
            return -abs(expected - response)
        else:  # If it has no modules capable of dealing with the recognized force
            return force.penalty
    
    def getSimpleResponse(self, variable, modules):
        variable = float(variable)
        running_total = 0
        for item in modules:
            response = item.getResponse(variable)
            if response is None:
                return None
            else:
                running_total += response
            self._responded = True
        return running_total           

class DynamicFitness(FitnessCalculator):
    """Randomly select modules to calculate fitness and sum responses."""
    @property
    def type_(self):
        return "Dynamic"

    def calculateUnitFitness(self, force, modules):
        if force.type_ == "Simple" or force.type_ == "Dynamic":
            self._responded = False
            variable, expected = force.conditions
            response = self.getSimpleResponse(variable, modules)
            if response is None:
                return None
        else:  # If it is an unrecognizable fitness force
            return force.penalty
        if self._responded:
            return -abs(expected - response)
        else:  # If it has no modules capable of dealing with the recognized force
            return force.penalty
    
    def getSimpleResponse(self, variable, modules):
        variable = float(variable)
        running_total = 0
        # Randomly determine the number of modules used between 1/2 total
        # modules to 1.5 * total modules (at least 1 module)
        num_modules_used = random.randint(
            max(1, int(len(modules) / 2)), int(1.5 * len(modules) + .5))
        for x in range(0, num_modules_used):
            response = random.choice(modules).getResponse(variable)
            if response is None:
                return None
            else:
                running_total += response
                self._responded = True
        return running_total
        
class TeiredFitness(FitnessCalculator):
    """Modules are teired with variable operations allowing for complex combinations.
    
    Stacks are designed to handle modules up to max_stack_length (100) and will ignore addition modules.
    Stacks are adjusted to reflect number of modules they recieve. However, they will not react to module
    merging.
    Stacks can take settings during initialization that specify a predefined module_stack.
    Added stacks will always be the [5, "Add"]
    Last stack operation is always ignored.
    Teir range is enforced at 1 - 10.
    """

    def __init__(self, settings=None):
        self._module_stack = [[5, "Add"]]*5
        if settings is not None:
            try:
                stack_settings = self.translate_settings(settings)
            except ValueError:
                print("Error: bad settings for Stack Fitness calculator. Returning unchanged.")
                stack_settings = self._module_stack
            self._module_stack = stack_settings
        self._operations = ["Add", "Subtract", "Multiply", "Divide"]
        self._plasticity = 1
        self._max_stack_length = 100
        self._mutate_operation_chance = 50
        self._mutate_teir_chance = 50
          
    @property
    def type_(self):     
        string = "_".join(["Teired", "_".join(["_".join([str(y) for y in x]) for x in self.module_stack])])
        return string
    
    @property
    def plasticity(self):
        """Specifies max # of module wrappers can be mutated in one pass. Max = 100, Min = 0"""
        return self._plasticity
    
    @plasticity.setter
    def plasticity(self, value):
        try:
            value = int(value)
        except ValueError:
            print("Error: bad plasticity value sent to teired fitness. Returning unchanged.")
            return
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        self._plasticity = value
    
    @property
    def module_stack(self):
        """List of module wrappers, each wrapper defines the module's teir and operation."""
        return self._module_stack
    
    @module_stack.setter
    def module_stack(self, value):
        try:
            holder = []
            for item in value:
                checked_item = self.check_stack_value(item)
                holder.append(checked_item)
        except TypeError:
            print("Error: bad type sent to module_stack, returning unchanged.")
            return
        self._module_stack = holder
    
    def check_stack_value(self, stack):
        """Checks individual stack values during assignment for recognizable values.
        
        Returns correct stack if successful. Raises TypeError otherwise.
        """
        if len(stack) != 2:
            raise TypeError
        stack[0] = int(stack[0])
        if stack[0] < 1:
            stack[0] = 1
        elif stack[0] > 10:
            stack[0] = 10
        stack[1] = str(stack[1])
        if stack[1] in self._operations:
            return stack
        else:
            raise TypeError

    def translate_settings(self, settings):
        """Translates the string settings into module_stack list.
           
        Settings must be in the form: tier_operation_tier_operation_...
        ex: 1_Add_3_Subtract_3_Subtract
        This list will be further checked when it is assigned to self.module_stack.
        """
        try:
            raw_list = settings.split("_")
        except AttributeError:
            raise ValueError
        stack_list = []
        if len(raw_list)%2 != 0:
            raise ValueError
        for x in range(0, len(raw_list)-1, 2):
            stack_list.append([int(raw_list[x]), raw_list[x+1]])
        return stack_list

    def calculateUnitFitness(self, force, modules):
        if force.type_ == "Simple" or force.type_ == "Dynamic":
            module_list = []
            for item in modules:
                if item.type_ == "Fitness":
                    module_list.append(item)
            self.adjust_module_stack(len(module_list))
            #response_stack = []
            self._responded = False
            variable, expected = force.conditions
            final_solution = self.getSimpleResponse(variable, modules)
        if final_solution is None:
            return None
        if self._responded:
            return -abs(expected - final_solution)
        else:  # If it has no modules capable of dealing with the recognized force
            return force.penalty        

    def getSimpleResponse(self, variable, modules):
        response_stack = []
        for pos, item in enumerate(modules):
            response = item.getResponse(variable)
            if response is None:
                return None
            else:
                response_stack.append([self._module_stack[pos][0], self._module_stack[pos][1], response])
            self._responded = True
        if self._responded:
            current_teir = response_stack[:]
            for teir in range(10, 0, -1):
                next_teir = list()
                current_solution = list()
                insert_pos = None
                for pos, response in enumerate(current_teir):
                    if response[0] < teir:
                        next_teir.append(response)
                    else:
                        if insert_pos is None:
                            insert_pos = pos
                        current_solution.append(str(response[2]))
                        if response[1] == "Add" or response[1] == "+":
                            current_solution.append("+")
                        elif response[1] == "Subtract" or response[1] == "-":
                            current_solution.append("-")
                        elif response[1] == "Multiply" or response[1] == "*":
                            current_solution.append("*")
                        else:
                            current_solution.append("/")
                current_equation = "".join(current_solution[:-1])
                if current_equation == "":
                    continue
                else:
                    try:                
                        solution = eval(current_equation)
                    except (ValueError, ZeroDivisionError):
                        return None
                    next_teir.insert(insert_pos,[teir-1, current_solution[-1], solution])
                current_teir = next_teir
            final_solution = solution        
        return final_solution
        
    def mutate(self):
        """Mutating teired fitness changes 1 or more module teir and/or operation.
        
        Number of modules that can be mutated in one pass is defined by plasticity attribute.
        """
        stack_order = [x for x in range(0, len(self._module_stack))]
        random.shuffle(stack_order)
        mutated_stacks = [x[:] for x in self.module_stack]
        mutations = 0
        # Randomly attempt to mutate teir and/or operation for each stack (in random order)
        # If the number of mutated stacks has reached plasticity threshold, no more mutations
        # are possible.
        for position in stack_order:
            if mutations == self._plasticity:
                break
            mutation_chances = [Mutations.HardMutation(1,100)]*2
            mutated = False
            if mutation_chances[0] < self._mutate_teir_chance:
                mutated = True                
                mutated_stacks[position][0] = Mutations.GaussianMutation(mutated_stacks[position][0], 1)
            if mutation_chances[1] < self._mutate_operation_chance:
                mutated = True
                mutated_stacks[position][1] = random.choice(self._operations)
            if mutated:
                mutations += 1
        self.module_stack = mutated_stacks
        
    def adjust_module_stack(self, target):
        """Add or remove elements from the end of the module stack to equal # of modules in solver."""
        if len(self.module_stack) == target:
            return
        elif len(self.module_stack) < target:
            for x in range(0, (target-len(self.module_stack))):
                self._module_stack.append([5, "Add"])
        else:
            for x in range(0, (len(self.module_stack) - target)):
                self._module_stack.pop()
           
            
class SolverInterface(object):

    def mutate(self):
        error()

    def clone(self):
        error()

    def reproduce(self):
        error()

    def getDescription(self):
        error()

    def softReset(self, new_name):
        error()

    def beginDay(self):
        error()

    def calculateFitness(self, fitness_forces):
        error()

    def death(self):
        error()

    def exportDict(self):
        error()

    def importAttributes(self, attribute_dictionary):
        error()

    # Property management
    @property
    def type_(self):
        return self._type_

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

    @property
    def permitted(self):
        """List of properties that may be imported"""
        return self._permitted

    @property
    def resilience(self):
        """int times remaining a solver can survive a math domain error without dieing

        When a solver survives a domain error, it is excluded from 1 pruning and 1 reproduction.
        Resilience of -1 means solver always survives domain errors.
        """
        return self._resilience

    @resilience.setter
    def resilience(self, value):
        try:
            value = int(value)
        except ValueError:
            badAttribute("resilience", type(value), self._resilience)
            return
        if value > 1000000:
            value = 1000000
        elif value < 0:
            value = 0
        self._resilience = value


class SmallSolver(SolverInterface):
    """Small solvers calculate fitness based on collection of modules

    Reproduction invokes deepcopy clone and 1 round of mutations.
    Modules may be combined as linear or dynamic."""

    def __init__(self, name=None, conditions=None):
        # Static properties
        if name is None:
            name = "Unnamed Solver"
        self._name = name
        self._type_ = "Small"
        self._fitness = 0
        self._lifespan = 100
        self._living = True
        self._max_modules = 15
        self._age = 0
        self._children = 0
        self._modules = []
        self._resilience = 2

        # Index correlations: 0 = spread, 1 = total_modules,
        # 2 = module_mutation_chance, 3 = property_mutation_chance; These are
        # hard-coded for individual and cannot mutate.
        self._property_chances = [1, 1, 60, 30]

        # Each solver has a 50% chance of being a unique-module solver
#        self._unique = True if random.randint(1, 2) == 1 else False
        self._unique = False

        # Determines the way modules are connected to calculate response
#        self._fitness_calculator = LinearFitness()
        self._fitness_calculator = LinearFitness()

        # Mutatable properties
        self._spread = 10
        self._total_modules = 5
        self._module_mutation_chance = 50
        self._property_mutation_chance = 10
        self._swap_module_chance = 15
        self._merge_module_chance = 50
        self._permitted = ["_age", "_children", "unique", "fitness_calculator", "spread", "total_modules",
                           "module_mutation_chance", "property_mutation_chance", "swap_module_chance", "merge_module_chance", "resilience"]
        if conditions:
            self.importAttributes(conditions)
    # Property management

    @property
    def spread(self):
        """Controls the width of gaussian mutations; Mutatable"""
        return self._spread

    @spread.setter
    def spread(self, value):
        try:
            value = float(value)
        except ValueError:
            badAttribute("coefficient", type(value), self._name)
            return
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
        try:
            value = int(value)
        except ValueError:
            badAttribute("total_modules", type(value), self._name)
            return
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
        try:
            value = float(value)
        except ValueError:
            badAttribute("module_mutation_chance", type(value), self._name)
            return
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
        try:
            value = float(value)
        except ValueError:
            badAttribute("property_mutation_chance", type(value), self._name)
            return
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
        try:
            value = float(value)
        except ValueError:
            badAttribute("swap_module_chance", type(value), self._name)
            return
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
        try:
            value = float(value)
        except ValueError:
            badAttribute("merge_module_chance", type(value), self._name)
            return
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
        if value == True or value == 1 or (isinstance(value, types.StringTypes) and value.upper()) == "TRUE":
            self._unique = True
        else:
            self._unique = False

    @property
    def living(self):
        """False = flagged for removal at start of next day"""
        return self._living

    @property
    def fitness_calculator(self):
        """Method that modules are combined to calculate fitness"""
        return self._fitness_calculator.type_

    @fitness_calculator.setter
    def fitness_calculator(self, value):
        value = str(value)
        if value == "Linear":
            self._fitness_calculator = LinearFitness()
        elif value == "Dynamic":
            self._fitness_calculator = DynamicFitness()
        elif value.startswith("Teired"):
            value = value.split("_")
            if len(value) == 1:
                self._fitness_calculator = TeiredFitness()
            else:
                value = "_".join(value[1:])
                self._fitness_calculator = TeiredFitness(value)
        else:
            badAttribute("fitness_calculator", value, self._name)
            return

    # Reproductive actions
    def clone(self):
        """Return a deepcopy of self"""
        return deepcopy(self)

    # Make a clone, reset name, age, and children, and mutate.
    def reproduce(self):
        """Return a deepcopy of self with fresh name, age, # children and a single mutation. self._children is incremented by 1"""
        if self._fitness is not None:
            clone = self.clone()
            self._children += 1
            try:
                child_name = self._name.split(
                    ".")[0] + "." + str(int(self._name.split(".")[1]) + 1)
            except IndexError:
                child_name = self._name + "." + str(self._children)
            clone.softReset(child_name)
            clone.mutate()
            clone._age = 1
            return clone
        else:
            return None

    def softReset(self, new_name="Unnamed Small Solver"):
        """Reset name, age, and # children"""
        self._name = str(new_name)
        self._children = 0
        self._age = 0
        self._fitness = 0
        # TODO: More testing with unique vs non-unique
        #self._unique = True if random.randint(1, 2) == 1 else False

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
                if random.randint(1, 100) <= self.swap_module_chance:
                    if not self.unique:
                        self._modules[x] = createUniqueModule(
                            "Fitness", [self._modules[x].subtype])
                    else:
                        present_subtypes = [y.subtype
                                            for y in self._modules]
                        self._modules[x] = createUniqueModule(
                            "Fitness", present_subtypes)
                else:
                    self._modules[x].mutate()

        if chances[-1] <= self._merge_module_chance:
            self.mergeModules()
        
        # Currently, all solvers have a 100% chance of calling their fitness_calculator mutate
        # Most fitness calculator mutates do nothing, those that did should have their own internal probabilities.
        self._fitness_calculator.mutate()
        
    def mutateProperty(self):
        """Mutate a single mutatable property"""
        selection = random.randint(1, 100)
        # Mutate spread
        if selection <= self._property_chances[0]:
            # Make sure that there is always a chance for some degree of
            # mutation
            self.spread = Mutations.GaussianMutation(
                self.spread, 1 if self.spread == 0 else self.spread)
            for item in self._modules:
                item.spread = self._spread
        # Mutate total modules
        elif selection <= sum(self._property_chances[0:2]):
            self.total_modules = int(Mutations.GaussianMutation(
                self._total_modules, 1))  # hardcode spread to 1 module
        # Mutate module mutation chance
        elif selection <= sum(self._property_chances[0:3]):
            self.module_mutation_chance = Mutations.GaussianMutation(
                self._module_mutation_chance, self._spread * self._module_mutation_chance / 100)
        # Mutate property mutation chance
        elif selection <= sum(self._property_chances):
            self.property_mutation_chance = Mutations.GaussianMutation(
                self._property_mutation_chance, self._spread * self._property_mutation_chance / 100)

    # Survival functions
    def beginDay(self):
        """Return false if no longer living for removal. Increment age. Add or remove modules as needed."""
        if self._age >= self._lifespan:
            self.death()

        if self._living:
            self._age += 1
            self._fitness = 0

            # Check if there are too many or too few modules (Can occure after
            # total_modules has been mutated or when no-parent solver is born)
            if len(self._modules) < self._total_modules:
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
            self._modules.append(createUniqueModule(
                "Fitness", present_subtypes))

    def calculateFitness(self, fitness_forces):
        """store sum fitness score of each fitness_force in provided list.

        Math domain errors return None and dock a resilient."""
        self._fitness = self._fitness_calculator.calculateFitness(
            fitness_forces, self._modules)
        if self._fitness is None:
            #            print("Solver %s failed the math domain and lost resilience." % self.name)
            if self._resilience == 0:
                #                print("Solver %s ran out of resilience and is DEAD!" % self.name)
                self.death()
            elif self._resilience > 0:
                self._resilience -= 1

    def getSimpleResponse(self, variable):
        """Return a single response to a single variable."""
        response = self._fitness_calculator.getSimpleResponse(variable, self._modules)
        return response

    def death(self):
        """Flags solver for death at start of next day"""
        self._living = False

    def mergeModules(self):
        """Merge the first two modules found that have the same subtype and add a unique module in the second one's place."""
        module_subtypes = {}
        for i, item in enumerate(self._modules):
            if item.subtype in module_subtypes:
                new_modules = mergeFitnessModules(self._modules[i], self._modules[
                                                  module_subtypes[item.subtype]])
                self._modules[module_subtypes[item.subtype]] = new_modules[
                    0]
                self._modules[i] = new_modules[1]
                break
            else:
                module_subtypes[item.subtype] = i

    # I/O Functions
    def getDescription(self):
        """Returns string containing important solver properties and modules"""
        desc = "-" * 30 + "\n"
        # Shorten name if too long. TODO: improve naming convention so this
        # isn't needed.
        if len(self._name) > 50:
            name = self._name[:30] + "..." + self._name[-3:]
        else:
            name = self._name
        desc += "%s, Age: %d, Children: %d" % (name, self._age, self._children)
        desc += "\nFitness Calculator: "+self._fitness_calculator.type_
        if len(self._modules) == 0:
            desc += "\nNo modules."
        else:
            desc += "\nModules:"
            for item in self._modules:
                desc += "\n%s" % item.getDescription()
        if self._fitness is None:
            desc += "\nNo fitness score available, solver currently withheld!"
        else:
            desc += "\nFitness score: %.2f" % self._fitness
        desc += "\n" + "-" * 30
        return desc

    def exportDict(self):
        """export all solver properties."""
        out_dict = {}
        for item in self._permitted:
            out_dict[item] = getattr(self, item)
        out_dict["_modules"] = []
        for item in self._modules:
            out_dict["_modules"].append(item.exportDict())
        out_dict["_type_"] = "Small"
        out_dict["name"] = self._name
        return out_dict

    def importAttributes(self, attributes):
        """Import pre-defined properties for solver."""
        try:
            for item in self._permitted:
                # Type-check the ~private variables since they have no setter.
                if item in attributes:
                    if item == "_age":
                        try:
                            attributes[item] = int(attributes[item])
                        except ValueError:
                            attributes[item] = 1
                    elif item == "name":
                        continue
                    elif item == "_children":
                        try:
                            attributes[item] = int(attributes[item])
                        except ValueError:
                            attributes[item] = 0
                    setattr(self, item, attributes[item])
            # Modules require individual import
            if "_modules" in attributes:
                imported_modules = []
                for mod in attributes["_modules"]:
                    imported_modules.append(importModule(mod))
                self._modules = imported_modules
        except TypeError:
            print("Error: unable to import conditions, unrecognized type sent.")
