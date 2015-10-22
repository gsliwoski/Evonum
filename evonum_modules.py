from __future__ import print_function
import json
import inspect
import math
import random
from evonum_mutations import *


def error():
    raise NotImplementedError("%s not implemented" %
                              inspect.stack()[1][3])  # Used for interface

#MODULE_SUBTYPES = ["Power_1", "Power_2", "Power_3", "Power_4", "Power_5"] #TODO: store potential subtypes elsewhere and make dynamic
MODULE_SUBTYPES = ["Power_1", "Power_2", "Power_3", "Power_4", "Power_5", "Log", "Ln", "Sine_1", "Sine_2",
                       "Sine_3", "Sine_4", "Sine_5", "Cosine_1", "Cosine_2", "Cosine_3", "Cosine_4", "Cosine_5"]
#MODULE_SUBTYPES = ["Log"]
#MODULE_SUBTYPES = ["Sine_1", "Sine_2", "Sine_3", "Sine_4", "Sine_5", "Cosine_1", "Cosine_2", "Cosine_3", "Cosine_4", "Cosine_5"]

def createModule(module_type, module_subtype):
    """Returns a new module of provided type and subtype.
    
    If provided subtype is "Random" then randomly selects subtype from defined list.
    """
#    max_power = 5
#    min_power = -5

    if module_type == "Fitness":
        if module_subtype == "Random":
            module_subtype = MODULE_SUBTYPES[
                random.randint(1, len(MODULE_SUBTYPES)) - 1]
        if module_subtype.startswith("Power"):
            if module_subtype == "Power":
                new_module = PowerSolution()
            else:
                new_module = PowerSolution(int(module_subtype.split("_")[1]))
        elif module_subtype.startswith("Sine"):
            if module_subtype == "Sine":
                new_module = SineSolution()
            else:
                new_module = SineSolution(int(module_subtype.split("_")[1]))
        elif module_subtype == "Log":
            new_module = LogSolution()
        elif module_subtype == "Ln":
            new_module = NaturalLogSolution()
        elif module_subtype.startswith("Cosine"):
            if module_subtype == "Cosine":
                new_module = CosineSolution()
            else:
                new_module = CosineSolution(int(module_subtype.split("_")[1]))
    return new_module

def createUniqueModule(module_type, present_subtypes):
    """Returns a new module of provided type that is not within the provided list of subtypes.
    
    If provided list of subtypes contain all possible subtypes, new module is of random subtype."""
    if module_type == "Fitness":
        potential_subtypes = []
        for item in MODULE_SUBTYPES:
            if item not in present_subtypes:
                potential_subtypes.append(item)
        try:
            sel = random.choice(potential_subtypes)
        except IndexError:
            sel = "Random"
        return createModule(module_type, sel)

def mergeFitnessModules(module_a, module_b):
    """Merge two fitness modules of the same subtype.
    
    Takes two modules.
    Returns two modules: merged result and new module of different subtype.
    If merge fails, then returns both modules unchanged."""
    
    if module_a.type_ == "Fitness" and module_b.type_ == "Fitness":
        if module_a.subtype == module_b.subtype:
            merged_module = createModule(
                module_a.type_, module_a.subtype)
            module_a_vals = module_a.mutatable()
            module_b_vals = module_b.mutatable()
            combined_vals = {}
            for item in module_a_vals:
                combined_vals[item] = module_a_vals[
                    item] + module_b_vals[item]
            merged_module.importAttributes(combined_vals)
            new_module = createUniqueModule(
                "Fitness", merged_module.subtype)
            return merged_module, new_module
        else:
            print ("Failed to merge modules of different subtypes.")
            return module_a, module_b
    else:
        print ("Failed to merge non-fitness modules with mergeFitnessModules.")
        return module_a, module_b

def importModule(module_dict):
    """Create a new module with a predefined property dictionary.
    
    Takes dictionary and returns module."""
    if "_type_" not in module_dict or "_subtype" not in module_dict:
        print("Error: module type/subtype must be provided for import, no module imported.")
        return None
    new_module = createModule(
        module_dict["_type_"], module_dict["_subtype"])
    if new_module:
        new_module.importAttributes(module_dict)
    else:
        print("Error: unable to import module of type: %s and subtype %s" % (module_dict["_type_"], module_dict["_subtype"]))
        return None
    return new_module


class ModuleInterface(object):

    def mutate():
        error()

    def getResponse(self, variable):
        error()

    def getDescription(self):
        error()

    @property
    def type_(self):
        """Main type of module. Used to match fitness/actions."""
        return self._type_
    
    @property
    def subtype(self):
        """Module subtype. Used to merge/swap/add unique modules."""
        return self._subtype
        

class FitnessModuleInterface(ModuleInterface):

    def mutate(self):
        error()
    
    def getResponse(self, variable):
        """Get module response to fitness power variable.
        
        If module response is undefined for fitness power variable,
        due to math domain/zero division error, return None.
        """
        try:
            variable = float(variable)
        except ValueError:
            raise TypeError("Error: variable sent fitness module is of bad type %s, must be convertable to float." % type(variable))
        try:
            response = self.calculator(variable)
        except (ValueError, ZeroDivisionError):
            response = None
        return response
    
    def calculator(self, variable):
        error()
    
    def importAttributes(self, value_dictionary):
        error()

    def mutatable(self):
        error()
    
    @property
    def permitted(self):
        """Properties that are permitted for import/export"""
        return self._permitted
    
    @property
    def spread(self):
        """Used to define width of gaussian mutation function"""
        return self._spread
    
    @spread.setter
    def spread(self, value):
        try:
            value = float(value)
        except ValueError:
            return
        if value > 1000:
            value = 1000
        elif value < 0:
            value = 0
        self._spread = value

    # Module serialization        
    def exportDict(self):
        """Serial export of module."""
        out_dict = {}
        for item in self._permitted:
            out_dict[item] = getattr(self, item)
            out_dict["_type_"] = self._type_
            out_dict["_subtype"] = self._subtype
        return out_dict
    
    def importAttributes(self, value_dictionary):
#        for item in value_dictionary:
        for item in self._permitted:
            if item in value_dictionary:
                setattr(self, item, value_dictionary[item])
            else:
                continue

class PowerSolution(FitnessModuleInterface):
    """Exponent-style fitness module.
    
    Type: Fitness
    Subtype: Power_n (n is the exponent determined at initialization)
    Initialization takes optional int power, otherwise power is random
    
    Returns coefficient * pow(x, n) given x.
    n is randomly selected from 1-5 at initialization.
    
    Mutatable properties:
    -coefficient
    
    Can only be merged with Power subtypes of equal n.
    """   

    def __init__(self, power=None):
        if power is None:
            self._power = random.randint(1, 5)  
        else:
            try:
                power = int(power)
            except ValueError:
                print("Error: Bad power type %s sent to Power Module, using random power" % type(power))
                power = random.randint(1, 5)
            self._power = int(power)
        # Set boundaries of what coefficient can be initialized at.
        self._min_coeff = -100
        self._max_coeff = 100

        # Randomly select starting coefficient
        self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
        self._type_ = "Fitness"
        self._subtype = "Power_" + str(self._power)
        self._spread = 10
        self._permitted = ["coeff", "spread"]

    # Property management
    @property
    def coeff(self):
        """Coefficient can be between -100,000 and 100,000."""
        return self._coeff
    
    @coeff.setter
    def coeff(self, value):
        try:
            value = float(value)
        except ValueError:
            print("Error: Bad coeff value type %s sent to power module, returning unchanged." % type(value))
            return
        if value > 100000:
            value = 100000
        elif value < -100000:
            value = -100000
        self._coeff = value

    # Module functions        
    def calculator(self, variable):
        """Returns single fitness reponse to single value."""
        return self._coeff * pow(variable, self._power)
            
    def mutate(self):
        """mutate a single mutatable property"""
        self.coeff = Mutations.GaussianMutation(self._coeff, self._spread)

    # I/O
    def getDescription(self):
        """Returns string of important properties"""
        string = "%s, %s: Response = %.4f * (variable)^%d" % (
            self._type_, self._subtype, self._coeff, self._power)
        return string

    def mutatable(self):
        """Returns dictionary of all mutatable properties and current values"""
        vals = {"coeff": self.coeff}
        return vals

# Returns N * sine^P(x). N is mutatable, P is assigned.
class SineSolution(FitnessModuleInterface):
    """Sine-style fitness module.
    
    Type: Fitness
    Subtype: Sine_n (n is the exponent determined at initialization)
    Initialization takes optional int power, otherwise power is random

    Returns coefficient * pow(sin(x),n) given x.
    n is randomly selected from 1-5 at initialization.
    coeff is randomly selected from -100 to 100 at initialization
        
    Mutatable properties:
    -coefficient
    
    Can only be merged with Sine subtypes of equal n.
    """     
    def __init__(self, power=None):
        # Set boundaries of what coefficient can be initialized at.
        self._min_coeff = -100
        self._max_coeff = 100
        self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
        self._type_ = "Fitness"
        if power is None:
            self._pow = random.randint(1, 5)
        else:
            try:
                power = int(power)
            except ValueError:
                print("Error: Bad power type %s sent to Sine Module, using random power" % type(power))
                power = random.randint(1,5)
            self._pow = power
        self._subtype = "Sine" + "_" + str(self._pow)
        self._spread = 0
        self._permitted = ["coeff", "spread"]

    # Property management
    @property
    def coeff(self):
        """Coefficient between -100,000 and 100,000"""
        return self._coeff

    @coeff.setter
    def coeff(self, value):
        try:
            value = float(value)
        except ValueError:
            print("Error: Bad coeff value type %s sent to sine module, returning unchanged." % type(value))
            return
        if value > 100000:
            value = 100000
        elif value < -100000:
            value = -100000
        self._coeff = value
    
    # Module functions
    def calculator(self, variable):
        """Returns single fitness reponse to single value."""
        return self._coeff * pow(math.sin(variable), self._pow)

    def mutate(self):
        """Mutate a single mutatable property"""
        self.coeff = Mutations.GaussianMutation(self._coeff, self._spread)

    def getDescription(self):
        """Returns string of important properties"""
        string = "%s, %s: Response = %.2f * sine^%d(variable)" % (
            self._type_, self._subtype, self._coeff, self._pow)
        return string

    def mutatable(self):
        """Get dict of mutatable properties"""
        vals = {"coeff": self.coeff}
        return vals

# Returns N * cosine^P(x)
class CosineSolution(FitnessModuleInterface):
    """Cosine-style fitness module.
    
    Type: Fitness
    Subtype: Cosine_n (n is the exponent determined at initialization)
    Initialization takes optional int power, otherwise power is random
        
    Returns coefficient * pow(cos(x),n) given x.
    n is randomly selected from 1-5 at initialization.
    coeff is randomly selected from -100 to 100 at initialization
    
    Mutatable properties:
    -coefficient
    
    Can only be merged with Cosine subtypes of equal n.
    """

    def __init__(self, power=None):
        self._min_coeff = -100
        self._max_coeff = 100
        self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
        self._type_ = "Fitness"
        if power is None:
            self._pow = random.randint(1, 5)
        else:
            try:
                power = int(power)
            except ValueError:
                print("Error: Bad power type %s sent to Cosine Module, using random power" % type(power))
                power = random.randint(1,5)
            self._pow = int(power)
        self._subtype = "Cosine" + "_" + str(self._pow)
        self._spread = 0
        self._permitted = ["coeff", "spread"]

    # Property management
    @property
    def coeff(self):
        """Coefficient between -100,000 and 100,000"""
        return self._coeff

    @coeff.setter
    def coeff(self, value):
        try:
            value = float(value)
        except ValueError:
            print("Error: Bad coeff value type %s sent to cosine module, returning unchanged." % type(value))
            return
        if value > 100000:
            value = 100000
        elif value < -100000:
            value = -100000
        self._coeff = value
    
    def calculator(self, variable):
        return self._coeff * pow(math.cos(variable), self._pow)

    def mutate(self):
        self.coeff = Mutations.GaussianMutation(self._coeff, self._spread)

    def getDescription(self):
        string = "%s, %s: Response = %.2f * cosine^%d(variable)" % (
            self._type_, self._subtype, self._coeff, self._pow)
        return string

    def mutatable(self):
        vals = {"coeff": self.coeff}
        return vals

# Returns N * log10(x) #TODO: Try allowing log base to be assigned like powers.
class LogSolution(FitnessModuleInterface):
    """log based 10-style fitness module.
    
    Type: Fitness
    Subtype: Log
    
    Returns coefficient * log(x, 10) given x.
    coeff is randomly selected from -100 to 100 at initialization
    
    Mutatable properties:
    -coefficient
    """

    def __init__(self):
        self._min_coeff = -100
        self._max_coeff = 100
        self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
        self._base = 10
        self._type_ = "Fitness"
        self._subtype = "Log"
        self._spread = 0
        self._permitted = ["coeff", "spread"]

    # Property management
    @property
    def coeff(self):
        """Coefficient between -100,000 and 100,000"""
        return self._coeff

    @coeff.setter
    def coeff(self, value):
        try:
            value = float(value)
        except ValueError:
            print("Error: Bad coeff value type %s sent to log module, returning unchanged." % type(value))
            return
        if value > 100000:
            value = 100000
        elif value < -100000:
            value = -100000
        self._coeff = value

    def calculator(self, variable):
        return self._coeff * math.log(variable, self._base)

    def mutate(self):
        self.coeff = Mutations.GaussianMutation(self._coeff, self._spread)

    def getDescription(self):
        string = "%s, %s: Response = %.2f * log[base %d](variable)" % (
            self._type_, self._subtype, self._coeff, self._base)
        return string

    def mutatable(self):
        """Returns dict of mutatable properties"""
        vals = {"coeff": self._coeff}
        return vals

# Returns N * ln(X)
class NaturalLogSolution(FitnessModuleInterface):  
    """natural log-style fitness module.
    
    Type: Fitness
    Subtype: Ln
    
    Returns coefficient * log(x) given x.
    coeff is randomly selected from -100 to 100 at initialization
    
    Mutatable properties:
    -coefficient
    """

    def __init__(self):
        self._min_coeff = -100
        self._max_coeff = 100
        self._coeff = Mutations.HardMutation(self._min_coeff, self._max_coeff)
        self._type_ = "Fitness"
        self._subtype = "Ln"
        self._spread = 0
        self._permitted = ["coeff", "spread"]

    # Property management
    @property
    def coeff(self):
        """Coefficient between -100,000 and 100,000"""
        return self._coeff

    @coeff.setter
    def coeff(self, value):
        try:
            value = float(value)
        except ValueError:
            print("Error: Bad coeff value type %s sent to ln module, returning unchanged." % type(value))
            return
        if value > 100000:
            value = 100000
        elif value < -100000:
            value = -100000
        self._coeff = value
        
    def calculator(self, variable):
        return self._coeff * math.log(variable)

    def mutate(self):
        self.coeff = Mutations.GaussianMutation(self._coeff, self._spread)

    def getDescription(self):
        string = "%s, %s: Response = %.2f * Ln(variable)" % (
            self._type_, self._subtype, self._coeff)
        return string                

    def mutatable(self):
        """Returns dict of mutatable properties."""
        vals = {"coeff": self._coeff}
        return vals
