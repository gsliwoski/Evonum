from evonum_modules import *
import pytest

class TestModuleCreation:
    def test_create_unknown_module_type(self):
        unknown_module = createModule("hmm", "ohh")
        assert unknown_module is None
    
    def test_create_unknown_fitness_subtype(self):
        unknown_subtype = createModule("Fitness",190.3)
        assert unknown_subtype is None
    
    def test_create_default_module(self):
        default_module = createModule()
        assert default_module.type_ == "Fitness"
    
    def test_create_random_fitness_module(self):
        potential_subtypes = MODULE_SUBTYPES
        random_fitness_module = createModule("Fitness")
        assert random_fitness_module.subtype in MODULE_SUBTYPES
    
    def test_create_cosine_power_5_module(self):
        cosine_5_module = createModule("Fitness","Cosine_5")
        assert cosine_5_module.subtype == "Cosine_5"
        assert cosine_5_module._pow == 5
    
    def test_create_unique_module(self):
        present_subtypes = MODULE_SUBTYPES[:]
        present_subtypes.pop()
        unique_module = createUniqueModule("Fitness", present_subtypes)
        assert unique_module.subtype == MODULE_SUBTYPES[-1]
    
    def test_create_unique_module_bad_present_subtypes(self):
        present_subtypes = 199
        unique_module = createUniqueModule("Fitness", present_subtypes)
        assert unique_module is None
    
    def test_create_unique_module_no_unique_subtypes_remain(self):
        present_subtypes = MODULE_SUBTYPES[:]
        unique_module = createUniqueModule("Fitness", present_subtypes)
        assert unique_module.subtype in present_subtypes
    
    def test_import_module(self):
        module_dict = {"_type_": "Fitness", "_subtype": "Power_5", "coeff": 10}
        imported_module = importModule(module_dict)
        assert imported_module.subtype == "Power_5"
        assert imported_module._power == 5
        assert imported_module.coeff == 10
        
    def test_import_module_bad_input(self):
        module_dict = {"_type_": "Fitness", "_subtype": "duuuh"}
        imported_module_bad_subtype = importModule(module_dict)
        module_dict_intdict = 5
        imported_module_intdict = importModule(module_dict_intdict)
        assert imported_module_bad_subtype is None
        assert imported_module_intdict is None
    
    def test_import_module_unpermitted_attributes(self):
        module_dict = {"_type_": "Fitness", "_subtype": "Power_5", "_permitted": "everything!"}
        imported_module_unpermitted_attributes = importModule(module_dict)
        assert imported_module_unpermitted_attributes._permitted != "everything!"
    
    def test_import_module_badtype_for_spread(self):
        module_dict = {"_type_": "Fitness", "_subtype": "Power_5", "spread": "idunno"}
        default_module = createModule()
        default_spread = default_module.spread
        imported_module_badtype_for_spread = importModule(module_dict)
        assert imported_module_badtype_for_spread.spread == default_spread

    def test_export_module(self):
        expected_dict = {'coeff': -19, 'spread': 10, '_type_': 'Fitness', '_subtype': 'Power_3'}
        imported_module = importModule(expected_dict)
        recieved_dict = imported_module.exportDict()
        assert expected_dict == recieved_dict
    
class TestFitnessModuleParameterControl:
    def test_improper_spread(self):
        bad_spread_module = createModule()
        bad_spread_module.spread = -1
        assert bad_spread_module.spread == 0
        bad_spread_module.spread = 100000000000000000000000000
        assert bad_spread_module.spread == 1000
        bad_spread_module.spread = "woops"
        assert bad_spread_module.spread == 1000

class TestPowerSubtype:
    def test_coeff_setter(self):
        bad_coefftype = True
        power_module = createModule("Fitness", "Power")
        initial_coeff = power_module.coeff
        power_module.coeff = bad_coefftype
        assert power_module.coeff == initial_coeff
        too_high_coeff = 10000000000000000000000000000000000000
        power_module.coeff = too_high_coeff
        assert power_module.coeff == 100000
        too_low_coeff = -10000000000000000000000000000000000000
        power_module.coeff = too_low_coeff
        assert power_module.coeff == -100000

    def test_get_response(self):
        defined_dict = {'coeff': -19, 'spread': 10, '_type_': 'Fitness', '_subtype': 'Power_3'}
        defined_power_module = importModule(defined_dict)
        variable = 5
        expected = -2375
        recieved = defined_power_module.getResponse(variable)
        assert recieved == expected
        badtype_variable = "bad"
        with pytest.raises(TypeError):
            recieved_badtype_variable = defined_power_module.getResponse(badtype_variable)


            
#    def test_mutate(self): TODO: add to collection of random number dependent tests
#        defined_dict = {'coeff': -19, 'spread': 10, '_type_': 'Fitness', '_subtype': 'Power_3'}
#        defined_power_module = importModule(defined_dict)
#        defined_power_module.mutate()
#        original = -19
#        mutated = defined_power_module.coeff
#        assert original != mutated

    def test_module_description(self):
        defined_dict = {'coeff': -19, 'spread': 10, '_type_': 'Fitness', '_subtype': 'Power_3'}
        defined_power_module = importModule(defined_dict)
        expected_description = "Fitness, Power_3: Response = -19.0000 * (variable)^3"
        recieved_description = defined_power_module.getDescription()
        assert recieved_description == expected_description        

class TestSineSubtype:
    def test_coeff_setter(self):
        bad_coefftype = "aaaahhhh"
        sine_module = createModule("Fitness","Sine")
        initial_coeff = sine_module.coeff
        sine_module.coeff = bad_coefftype
        assert sine_module.coeff == initial_coeff
        too_high_coeff = 1000000000000000000000000000000000
        sine_module.coeff = too_high_coeff
        assert sine_module.coeff == 100000
        too_low_coeff = -1000000000000000000000000000000000
        sine_module.coeff = too_low_coeff
        assert sine_module.coeff == -100000

    def test_getResponse(self):
        defined_dict = {'coeff': -19, 'spread': 10, '_type_': 'Fitness', '_subtype': 'Sine_3'}
        sine_module = importModule(defined_dict)
        variable = 5
        expected = 17
        recieved = round(sine_module.getResponse(variable))
        assert expected == recieved
    
#    def test_mutate(self): TODO: add to collection of random number dependent tests
    
class TestCosineSubtype:
    def test_coeff_setter(self):
        bad_coefftype = "aaaahhhh"
        cosine_module = createModule("Fitness","Cosine")
        initial_coeff = cosine_module.coeff
        cosine_module.coeff = bad_coefftype
        assert cosine_module.coeff == initial_coeff
        too_high_coeff = 1000000000000000000000000000000000
        cosine_module.coeff = too_high_coeff
        assert cosine_module.coeff == 100000
        too_low_coeff = -1000000000000000000000000000000000
        cosine_module.coeff = too_low_coeff
        assert cosine_module.coeff == -100000
    
    def test_get_response(self):
        defined_dict = {'coeff': -19, 'spread': 10, '_type_': 'Fitness', '_subtype': 'Cosine_1'}
        cosine_module = importModule(defined_dict)
        variable = 5
        expected = -5
        recieved = round(cosine_module.getResponse(variable))
        assert expected == recieved

#    def test_mutate(self): TODO: add to collection of random number dependent tests

class TestLogSubtype:
    def test_coeff_setter(self):
        bad_coefftype = "aaaahhhh"
        log_module = createModule("Fitness","Log")
        initial_coeff = log_module.coeff
        log_module.coeff = bad_coefftype
        assert log_module.coeff == initial_coeff
        too_high_coeff = 1000000000000000000000000000000000
        log_module.coeff = too_high_coeff
        assert log_module.coeff == 100000
        too_low_coeff = -1000000000000000000000000000000000
        log_module.coeff = too_low_coeff
        assert log_module.coeff == -100000
    
    def test_get_response(self):
        defined_dict = {'coeff': -19, 'spread': 10, '_type_': 'Fitness', '_subtype': 'Log'}
        log_module = importModule(defined_dict)
        variable = 5
        expected = -13
        recieved = round(log_module.getResponse(variable))        
        assert recieved == expected
        bad_variable = -5
        recieved_bad_variable = log_module.getResponse(bad_variable)
        assert recieved_bad_variable is None

#    def test_mutate(self): TODO: add to collection of random number dependent tests

class TestLnSubtype:
    def test_coeff_setter(self):
        bad_coefftype = "aaaahhhh"
        ln_module = createModule("Fitness","Log")
        initial_coeff = ln_module.coeff
        ln_module.coeff = bad_coefftype
        assert ln_module.coeff == initial_coeff
        too_high_coeff = 1000000000000000000000000000000000
        ln_module.coeff = too_high_coeff
        assert ln_module.coeff == 100000
        too_low_coeff = -1000000000000000000000000000000000
        ln_module.coeff = too_low_coeff
        assert ln_module.coeff == -100000

    def test_get_response(self):
        defined_dict = {'coeff': -19, 'spread': 10, '_type_': 'Fitness', '_subtype': 'Ln'}
        ln_module = importModule(defined_dict)
        variable = 5
        expected = -31
        recieved = round(ln_module.getResponse(variable))        
        assert recieved == expected
        bad_variable = -5
        recieved_bad_variable = ln_module.getResponse(bad_variable)
        assert recieved_bad_variable is None

#    def test_mutate(self): TODO: add to collection of random number dependent tests
