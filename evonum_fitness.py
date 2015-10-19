from __future__ import print_function
import inspect
from math import *
import random


def error():
    raise NotImplementedError("%s not implemented" %
                              inspect.stack()[1][3])  # Used for interface

class FitnessInterface(object):

    def __init__(self, name):
        error()
    
    def beginDay(self):  
        error()

    def loadConditions(self, *args):
        error()

    def getDescription(self):
        error()

    @property
    def type_(self):
        """Type of fitness force used to match with solver modules"""
        return self._type_
   
    @property
    def penalty(self):
        """Fitness penalty if solver has no modules to handle force"""
        return self._penalty

    @property
    def name(self):
        return self._name

    @property
    def age(self):
        """Number of days fitness force has been active"""
        return self._age
    
    @property
    def conditions(self):
        """Returns tuple of value and expected response"""
        return self._current_condition, self._current_expected
                        
# Concrete Fitness Forces
class SimplePosition(FitnessInterface):
    """Randomly selects position and expects value at given position
    
    Type = Simple
    Initialize with optional string name
    
    Penalty = -99999999999
    
    LoadConditions takes a string filename containing ordered list of 
                   expected values
    """

    def __init__(self, name="Unnamed Simple Position Fitness Force"):
        self._name = name
        self._expected = []
        self._current_expected = 0
        self._age = 0
        self._current_condition = 0
        self._max_ = len(self._expected)
        self._min_ = 0
        self._type_ = "Simple"   
        self._penalty = -99999999999

    def getDescription(self):
        return "%s Fitness. Name: %s Age: %d, Current Condition: %d, Current Desire: %d" % (self._type_, self._name, self._age, self._current_condition, self._current_expected)

    # Randomly select a variable and get the expected value at that position
    def _setConditions(self):
        """Randomly selects position and sets expected as value at that position"""
        self._current_condition = random.randint(self._min_, self._max_)
        self._current_expected = self._expected[self._current_condition - 1]

    def beginDay(self):
        """Increments age by 1 and sets day's conditions"""
        self._age += 1
        self._setConditions()

    # Conditions are loaded for this fitness force as an ordered list of values from a file.
    def loadConditions(self, filename):
        """Load ordered list of values from provided filename"""
        try:
            self._expected = [float(x) for x in open(filename).read().split()]
            self._max_ = len(self._expected)
        except:
            assert self._name + \
                " Failed to load conditions from " + str(filename)
        finally:
            assert len(
                self._expected) > 0, "No conditions loaded for position fitness force!"

# Equation fitness force randomly generates variable and calculates expected
# based on a provided equation.
class SimpleEquation(FitnessInterface):
    """Randomly selects variable (between min and max) and expects value determined with equation
    
    Type = Simple
    Initialize with optional string name
    
    Penalty = -99999999999
    
    LoadConditions takes a string pythonic equation, minimum random value, maximum random value
    """

    def __init__(self, name="Unnamed Simple Equation Fitness Force"):
        self._name = name
        self._current_expected = 0
        self._age = 0
        self._current_condition = 0
        self._max_ = 1000000
        self._min_ = -1000000
        self._type_ = "Simple"
        self._penalty = -99999999999
        # Permitted operations are specified to avoid unsecure behavior of eval.
        self._operations = ['math', 'cos', 'sin', 'tan', 'log', 'log10', 'pow', 'pi', 'e', 'exp', 'pow', 'sqrt', 'fabs', 'acos', 'asin', 'atan']
        self._permitted = {item: globals().get(item) for item in self._operations}
        self._equation_string = ''

    #Property management
    @property
    def max_(self):
        """Maximum random variable; limits are -1,000,000 and 1,000,000"""
        return self._max_
    
    @max_.setter
    def max_(self, value):
        if value > 1000000:
            value = 1000000
        elif value < self._min_:
            value = self._min_
        self._max_ = value
    
    @property
    def min_(self):
        """Minimum random variable; limits are -1,000,000 and 1,000,000"""
        return self._min_
        
    @min_.setter
    def min_(self, value):
       if value < -1000000:
          value = -1000000
       elif value > self._max_:
          value = self._max_
       self._min_ = value
        
    def getDescription(self):
        return "%s Fitness. Name: %s Age: %d, Current Condition: %.2f, Current Desire: %.2f" % (self._type_, self._name, self._age, self._current_condition, self._current_expected)

    def _setConditions(self):
        """Randomly select value and calculated expected value using provided equation."""
        self._current_condition = random.random() * (self._max_ - self._min_) + self._min_
        self._permitted['x']=self._current_condition
        try: 
            self._current_expected = eval(self._equation_string,{"__builtins__":None}, self._permitted)
        except ValueError:
            raise ValueError("Equation is undefined for some value(s) within range. Value attempted: %.2f" % self._current_condition)

    def beginDay(self):
        """Increment age by 1 and set day's conditions"""
        self._age += 1
        self._setConditions()

    def loadConditions(self, conditions):
        print(conditions)
        """Takes string  of equation, minimum random variable, maximum random variable"""
        conditions = conditions.split(",")
        self._equation_string = ",".join(conditions[:-2])
        self.max_ = max(float(conditions[-2]), float(conditions[-1]))
        self.min_ = min(float(conditions[-2]), float(conditions[-1]))
        print(self.max_)
        print(self.min_)

#TODO: Needs further testing and improvements
class DynamicEquation(FitnessInterface):
    """Randomly selects variable (between min and max) and expects value determined with equation
    
    Type = Dynamic [probability of random value changes depending on solver performance]
    Initialize with optional string name
    
    Penalty = -99999999999
    
    LoadConditions takes a string pythonic equation, minimum random value, maximum random value
    """

    def __init__(self, name="Unnamed Dynamic Equation Fitness Force"):
        self._name = name
        self._current_expected = 0
        self._age = 0
        self._max_ = 1000000
        self._min_ = -1000000
        self._current_condition = self._min_
        self._type_ = "Dynamic"
        self._penalty = -99999999999
        # Permitted operations are specified to avoid unsecure behavior of eval.
        self._operations = ['math', 'cos', 'sin', 'tan', 'log', 'log10', 'pow', 'pi', 'e', 'exp', 'pow', 'sqrt', 'fabs', 'acos', 'asin', 'atan']
        self._permitted = {item: globals().get(item) for item in self._operations}
        self._equation_string = ''
        # Initialize vector of 50 equal probabilities. Values are broken into 50 sets.
        self._condition_probabilities = [100] * 10
        
        # Store past solver performance
        self._avg_fitness = [0, 0]
        
        # Calculate section size
        self._step_size = float(self._max_ - self._min_) / len(self._condition_probabilities)

    #Property management
    @property
    def max_(self):
        """Maximum random variable; limits are -1,000,000 and 1,000,000"""
        return self._max_
    
    @max_.setter
    def max_(self, value):
        if value > 1000000:
            value = 1000000
        elif value < self._min_:
            value = self._min_
        self._max_ = value
    
    @property
    def min_(self):
        """Minimum random variable; limits are -1,000,000 and 1,000,000"""
        return self._min_
        
    @min_.setter
    def min_(self, value):
       if value < -1000000:
          value = -1000000
       elif value > self._max_:
          value = self._max_
       self._min_ = value

       
    # Required for dynamic behavior
    @property
    def avg_fitness(self):
        """Average fitness performance for adjusting values probability"""
        return self._avg_fitness

    @avg_fitness.setter
    def avg_fitness(self, value):
        self._avg_fitness = value
        
    def getDescription(self):
#        print ("Current condition: %.2f Current expected: %.2f" % (self._current_condition, self._current_expected))
        return "%s Fitness. Name: %s Age: %d, Current Condition: %.2f, Current Desire: %.2f" % (self._type_, self._name, self._age, self._current_condition, self._current_expected)

    def _setConditions(self):
        """Randomly select value based on probabilities and calculate expected with equation"""
        running_range_prob = 0
        sum_prob = sum(self._condition_probabilities)
        random_range = random.random() * sum_prob
        range_selection = 9
#		print ("RandomRange = %.2f" % random_range)
      
        # Randomly select a section of potential variables based on all sections' probability of being selected.
        for pos, val in enumerate(self._condition_probabilities):
            if random_range >= running_range_prob and random_range < running_range_prob + val:
                range_selection = pos
                break
            else:
                running_range_prob += val
        # Set up the current section of potential variables and select day's variable
        current_min = self._min_ + range_selection * self._step_size
        current_max = current_min + self._step_size
#        print("range selection: "+str(range_selection))
#        print ("step size: "+str(self._step_size))
#        print ("min: "+str(current_min)+" max: "+str(current_max))
        self._current_condition = random.random() * (current_max - current_min) + current_min
        self._permitted['x']=self._current_condition
#        print(self._avg_fitness)
        try: 
            self._current_expected = eval(self._equation_string,{"__builtins__":None}, self._permitted)
        except ValueError:
            raise ValueError("Equation is undefined for some value(s) within range. Value attempted: %.2f" % self._current_condition)
        
#		print ("step size: %.2f, current_min: %.2f, current_max: %.2f" % (self._step_size, current_min, current_max))

    def beginDay(self):
        """Increment age by 1 and set day's conditions"""
        self._age += 1
        self._setConditions()
#        print (self.conditions)

    def loadConditions(self, conditions):
        conditions = conditions.split(",")
        self._equation_string = ",".join(conditions[:-2])
        self.max_ = max(float(conditions[-2]), float(conditions[-1]))
        self.min_ = min(float(conditions[-2]), float(conditions[-1]))
        self._step_size = float(self._max_ - self._min_) / len(self._condition_probabilities)
#        print (self._min_,self._max_,self._step_size)

    # Increase or decrease the probability of today's variable section's future selection based on solver performance
    def updateConditionProbability(self, condition, increase):
        #		print ("Condition: %.2f Increase? %r" % (condition, increase))
        pos = int((condition - self._min_) / self._step_size)
        if increase:
            self._condition_probabilities[pos] += 1
        else:
            self._condition_probabilities[pos] -= 1
        if self._condition_probabilities[pos] < 1:
            self._condition_probabilities[pos] = 1
        elif self._condition_probabilities[pos] > 1000:
            self._condition_probabilities[pos] = 1000
        print (self._condition_probabilities)

#Identity is the simplest fitness force which randomly selects a value and expects the same value       
class SimpleIdentity(FitnessInterface): #TODO: Remove?

    def __init__(self, name="Unnamed Simple Identity Fitness Force"):
        self._name = name
        self._current_expected = 0
        self._age = 0
        self._current_condition = 0
        self._max_ = 1000
        self._min_ = 0
        self._type_ = "Simple"
        
        # Used when a solver has no modules for handling this fitness force.
        self._penalty = -99999999999

    def getDescription(self):
        return "%s Fitness. Name: %s Age: %d, Current Condition: %d, Current Desire: %d" % (self._type_, self._name, self._age, self._current_condition, self._current_expected)

    # Randomly select a variable and get the expected value at that position
    def _setConditions(self):
        self._current_condition = random.randint(self._min_, self._max_)
        self._current_expected = self._current_condition

    def beginDay(self):
        self._age += 1
        self._setConditions()

    # Conditions are loaded for this fitness force as an ordered list of values from a file.
    def loadConditions(self, min_max):
        min_max = min_max.split(",")
        self._min_ = float(min_max[0])
        self._max_ = float(min_max[1])
