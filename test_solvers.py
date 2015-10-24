from evonum_solvers import *
import pytest


class TestSolverCreation:

    def test_create_default_solver(self):
        default_solver = createSolver()
        assert default_solver._type_ == "Small"

    def test_create_unknown_solver_type(self):
        bad_solver = createSolver("???", "???")
        assert bad_solver is None

    def test_create_small_solver_no_name(self):
        unnamed_solver = createSolver("Small")
        assert unnamed_solver.name == "Unnamed Linear Solver"

    def test_create_solver_with_name(self):
        named_solver = createSolver("Small", "TestSolver")
        assert named_solver.name == "TestSolver"

    def test_create_solver_with_legitimate_conditions(self):
        conditions = {"unique": False, "module_mutation_chance": 50}
        designed_solver = createSolver("Small", "DesignedSolver", conditions)
        assert designed_solver.module_mutation_chance == 50
        assert designed_solver.unique == False

    def test_create_solver_with_badtype_conditions(self):
        conditions = ["module_mutation_chance", 30]
        default_module_mutation_chance = 50
        bad_condition_type_solver = createSolver("Small", "Failed", conditions)
        assert bad_condition_type_solver.module_mutation_chance == default_module_mutation_chance

    def test_create_solver_with_nonpermitted_conditions(self):
        conditions = {"permitted": ["permitted"]}
        wrong_conditions_solver = createSolver("Small", "Failed", conditions)
        assert "permitted" not in wrong_conditions_solver.permitted


class TestSolverPropertyManagement:

    def test_set_negative_spread(self):
        neg_spread_solver = createSolver()
        neg_spread_solver.spread = -100
        assert neg_spread_solver.spread == 0

    def test_set_spread_too_high(self):
        high_spread_solver = createSolver()
        high_spread_solver.spread = 1000000000000000
        assert high_spread_solver.spread == 1000

    def test_set_spread_with_string(self):
        string_spread_solver = createSolver()
        default_spread = string_spread_solver.spread
        string_spread_solver.spread = "hi"
        assert string_spread_solver.spread == default_spread

    def test_set_negative_total_modules(self):
        negative_modules_solver = createSolver()
        negative_modules_solver.total_modules = -5
        assert negative_modules_solver.total_modules == 1

    def test_set_total_modules_too_high(self):
        too_high_modules_solver = createSolver()
        max_modules = too_high_modules_solver._max_modules
        too_high_modules_solver.total_modules = max_modules + 1
        assert too_high_modules_solver.total_modules == max_modules

    def test_set_total_modules_bad_type(self):
        bad_type_total_modules_solver = createSolver()
        default_total_modules = bad_type_total_modules_solver.total_modules
        bad_type_total_modules_solver.total_modules = "woops"
        assert bad_type_total_modules_solver.total_modules == default_total_modules

    def test_set_mutation_chances_negative(self):
        neg_mutation_chance_solver = createSolver()
        neg_mutation_chance_solver.module_mutation_chance = -1
        neg_mutation_chance_solver.property_mutation_chance = -1
        neg_mutation_chance_solver.swap_module_chance = -1
        neg_mutation_chance_solver.merge_module_chance = -1
        assert neg_mutation_chance_solver.module_mutation_chance == 0
        assert neg_mutation_chance_solver.property_mutation_chance == 0
        assert neg_mutation_chance_solver.swap_module_chance == 0
        assert neg_mutation_chance_solver.merge_module_chance == 0

    def test_set_mutation_chances_too_high(self):
        max_mutation_chance = 100
        too_high_mutation_chance_solver = createSolver()
        too_high_mutation_chance_solver.module_mutation_chance = max_mutation_chance + 1
        too_high_mutation_chance_solver.property_mutation_chance = max_mutation_chance + 1
        too_high_mutation_chance_solver.swap_module_chance = max_mutation_chance + 1
        too_high_mutation_chance_solver.merge_module_chance = max_mutation_chance + 1
        assert too_high_mutation_chance_solver.module_mutation_chance == max_mutation_chance
        assert too_high_mutation_chance_solver.property_mutation_chance == max_mutation_chance
        assert too_high_mutation_chance_solver.swap_module_chance == max_mutation_chance
        assert too_high_mutation_chance_solver.merge_module_chance == max_mutation_chance

    def test_set_mutation_chances_bad_type(self):
        bad_type_mutation_chance_solver = createSolver()
        bad_type_try = "uh oh."
        original_module_mutation_chance = bad_type_mutation_chance_solver.module_mutation_chance
        original_property_mutation_chance = bad_type_mutation_chance_solver.property_mutation_chance
        original_swap_module_chance = bad_type_mutation_chance_solver.swap_module_chance
        original_merge_module_chance = bad_type_mutation_chance_solver.merge_module_chance
        bad_type_mutation_chance_solver.module_mutation_chance = bad_type_try
        bad_type_mutation_chance_solver.property_mutation_chance = bad_type_try
        bad_type_mutation_chance_solver.swap_module_chance = bad_type_try
        bad_type_mutation_chance_solver.merge_module_chance = bad_type_try
        assert bad_type_mutation_chance_solver.module_mutation_chance == original_module_mutation_chance
        assert bad_type_mutation_chance_solver.property_mutation_chance == original_property_mutation_chance
        assert bad_type_mutation_chance_solver.swap_module_chance == original_swap_module_chance
        assert bad_type_mutation_chance_solver.merge_module_chance == original_merge_module_chance

    def test_set_unique(self):
        set_unique_test_solver = createSolver()
        set_unique_test_solver.unique = True
        assert set_unique_test_solver.unique == True
        set_unique_test_solver.unique = False
        assert set_unique_test_solver.unique == False
        set_unique_test_solver.unique = 1
        assert set_unique_test_solver.unique == True
        set_unique_test_solver.unique = "what?"
        assert set_unique_test_solver.unique == False

    def test_set_fitness_calculator(self):
        set_fitness_calculator_test_solver = createSolver()
        set_fitness_calculator_test_solver.fitness_calculator = "Linear"
        assert isinstance(
            set_fitness_calculator_test_solver._fitness_calculator, LinearFitness)
        set_fitness_calculator_test_solver.fitness_calculator = "Dynamic"
        assert isinstance(
            set_fitness_calculator_test_solver._fitness_calculator, DynamicFitness)
        set_fitness_calculator_test_solver.fitness_calculator = 1
        assert isinstance(
            set_fitness_calculator_test_solver._fitness_calculator, DynamicFitness)


class TestBasicSolverFunctions:

    def test_reproduction(self):
        parent = createSolver("Small", "Parent")
        child = parent.reproduce()
        assert parent._children == 1
        assert child.name == "Parent.1"

    def test_mutate_property(self):
        random.seed(1)
        mutate_property_solver = createSolver()
        mutate_property_solver.property_mutation_chance = 100
        mutate_property_solver.mutate()
        mutated_properties = [mutate_property_solver.spread, mutate_property_solver.total_modules,
                              mutate_property_solver.module_mutation_chance, mutate_property_solver.property_mutation_chance]
        mutated_properties = [round(x) for x in mutated_properties]
        assert mutated_properties == [10, 5, 45, 100]

    def test_begin_day_normal(self):
        test_solver = createSolver()
        response = test_solver.beginDay()
        assert response == True
        assert test_solver._age == 1
        assert len(test_solver._modules) == 5

    def test_solver_death(self):
        death_test_solver = createSolver()
        death_test_solver.death()
        assert death_test_solver.living == False

    def test_begin_day_lifespan_expire(self):
        test_old_solver = createSolver()
        test_old_solver._age = test_old_solver._lifespan
        response = test_old_solver.beginDay()
        assert response == False
        assert test_old_solver.living == False

    def test_get_description(self):
        test_description_solver = createSolver("Small", "Tester")
        description = test_description_solver.getDescription()
        assert description == "------------------------------\nTester, Age: 0, Children: 0\nNo modules.\nFitness score: 0.00\n------------------------------"

    def test_export_solver(self):
        export_test_solver = createSolver("Small", "Tester")
        expected_dict = {'fitness_calculator': 'Linear', '_children': 0, 'module_mutation_chance': 50, '_type_': 'Small', 'property_mutation_chance': 10,
                         'merge_module_chance': 50, 'spread': 10, 'total_modules': 5, '_modules': [], '_age': 0, 'unique': False, 'resilience': 2, 'swap_module_chance': 15, 'name': 'Tester'}
        recieved_dict = export_test_solver.exportDict()
        assert expected_dict == recieved_dict
