from evonum_terrarium import *
import pytest
import random


class TestPopulateTerrarium:

    def test_add_simple_equation_force(self):
        equation_force_world = Terrarium()
        equation_force_world.addForce("Simple", "Equation", "x, 1, 2")
        assert isinstance(equation_force_world._forces[0], SimpleEquation)

    def test_add_too_many_forces(self):
        too_many_forces_world = Terrarium()
        for x in range(1, too_many_forces_world._max_forces + 1):
            too_many_forces_world.addForce(
                "Simple", "Position", "primes_1000.txt")
        too_many_forces_world.addForce("Dynamic", "Equation", "x, 1, 2")
        assert len(too_many_forces_world._forces) == 5

    def test_add_unknown_force(self):
        unknown_force_world = Terrarium()
        unknown_force_world.addForce("Simple", "???", "x = 2x")
        assert len(unknown_force_world._forces) == 0

    def test_add_solver(self):
        solver_world = Terrarium()
        solver_world.addSolver()
        assert isinstance(solver_world._solvers[0], SmallSolver)


class TestRunTerrariumIntegrationTests:

    def test_import_solvers(self):
        """!!!Integration Test!!!"""
        import_solver_world = Terrarium()
        solvers_json = [{"_modules": [{"_subtype": "Cosine_4", "_type_": "Fitness", "coeff": 23.003934813900763, "spread": 10}], "name": "Solver1", "_type_": "Small", "fitness_calculator": "Linear", "spread": 5}, {
            "_modules": [{"_subtype": "Cosine_4", "_type_": "Fitness", "coeff": 14.837854400896619, "spread": 10}], "name": "Solver2", "_type_": "Small", "fitness_calculator": "Linear", "unique": True}]
        import_solver_world.importSolvers(solvers_json)
        assert len(import_solver_world._solvers) == 2
        assert import_solver_world._solvers[0].name == "Solver1"
        assert import_solver_world._solvers[1].name == "Solver2"

    """!!!Integration Test!!!"""

    def test_reproduce_solvers(self):
        reproduce_solver_test_world = Terrarium()
        for x in range(0, 50):
            reproduce_solver_test_world.addSolver()
        reproduce_solver_test_world.reproduceSolvers()
        assert len(reproduce_solver_test_world._solvers) == 100

    def test_run_day(self):
        """!!!Integration Test!!!"""
        test_run_world = Terrarium()
        solvers_json = [{"_modules": [{"_subtype": "Cosine_4", "_type_": "Fitness"}], "name": "Solver1", "_type_": "Small", "fitness_calculator": "Linear"}, {
            "_modules": [{"_subtype": "Cosine_4", "_type_": "Fitness", }], "name": "Solver2", "_type_": "Small", "fitness_calculator": "Linear"}]
        test_run_world.importSolvers(solvers_json)
        test_run_world.runDays(1)
        assert len(test_run_world._solvers) == 4

    def test_export_solvers(self):
        """!!!Integration Test!!!"""
        random.seed(1)
        export_solver_world = Terrarium()
        solvers_json = [{"_modules": [{"_subtype": "Cosine_4", "_type_": "Fitness"}], "name": "Solver1", "_type_": "Small", "fitness_calculator": "Linear"}, {
            "_modules": [{"_subtype": "Cosine_4", "_type_": "Fitness", }], "name": "Solver2", "_type_": "Small", "fitness_calculator": "Linear"}]
        export_solver_world.importSolvers(solvers_json)
        export_solver_world.runDays(1)
        exported_jsons = export_solver_world.exportSolvers()
        assert exported_jsons == ['{\n  "_age": 1, \n  "_children": 1, \n  "_modules": [\n    {\n      "_subtype": "Cosine_4", \n      "_type_": "Fitness", \n      "coeff": -74, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Cosine_1", \n      "_type_": "Fitness", \n      "coeff": -49, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Sine_2", \n      "_type_": "Fitness", \n      "coeff": -11, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Sine_5", \n      "_type_": "Fitness", \n      "coeff": 57, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Power_2", \n      "_type_": "Fitness", \n      "coeff": -95, \n      "spread": 10.0\n    }\n  ], \n  "_type_": "Small", \n  "fitness_calculator": "Linear", \n  "merge_module_chance": 50, \n  "module_mutation_chance": 50, \n  "name": "Solver1", \n  "property_mutation_chance": 10, \n  "resilience": 2, \n  "spread": 10, \n  "swap_module_chance": 15, \n  "total_modules": 5, \n  "unique": false\n}', '{\n  "_age": 1, \n  "_children": 1, \n  "_modules": [\n    {\n      "_subtype": "Cosine_4", \n      "_type_": "Fitness", \n      "coeff": 69, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Cosine_3", \n      "_type_": "Fitness", \n      "coeff": -14, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Cosine_1", \n      "_type_": "Fitness", \n      "coeff": -100, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Sine_1", \n      "_type_": "Fitness", \n      "coeff": 44, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Power_4", \n      "_type_": "Fitness", \n      "coeff": 89, \n      "spread": 10.0\n    }\n  ], \n  "_type_": "Small", \n  "fitness_calculator": "Linear", \n  "merge_module_chance": 50, \n  "module_mutation_chance": 50, \n  "name": "Solver2", \n  "property_mutation_chance": 10, \n  "resilience": 2, \n  "spread": 10, \n  "swap_module_chance": 15, \n  "total_modules": 5, \n  "unique": false\n}',
                                  '{\n  "_age": 1, \n  "_children": 0, \n  "_modules": [\n    {\n      "_subtype": "Power_4", \n      "_type_": "Fitness", \n      "coeff": -13, \n      "spread": 10\n    }, \n    {\n      "_subtype": "Cosine_1", \n      "_type_": "Fitness", \n      "coeff": -48.23136518280748, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Sine_2", \n      "_type_": "Fitness", \n      "coeff": -11, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Sine_5", \n      "_type_": "Fitness", \n      "coeff": 57, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Power_2", \n      "_type_": "Fitness", \n      "coeff": -87.79532403140746, \n      "spread": 10.0\n    }\n  ], \n  "_type_": "Small", \n  "fitness_calculator": "Linear", \n  "merge_module_chance": 50, \n  "module_mutation_chance": 50, \n  "name": "Solver1.1", \n  "property_mutation_chance": 10, \n  "resilience": 2, \n  "spread": 10, \n  "swap_module_chance": 15, \n  "total_modules": 5, \n  "unique": false\n}', '{\n  "_age": 1, \n  "_children": 0, \n  "_modules": [\n    {\n      "_subtype": "Cosine_4", \n      "_type_": "Fitness", \n      "coeff": 75.52220223807572, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Cosine_3", \n      "_type_": "Fitness", \n      "coeff": -7.806249378262811, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Cosine_1", \n      "_type_": "Fitness", \n      "coeff": -100, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Sine_1", \n      "_type_": "Fitness", \n      "coeff": 44, \n      "spread": 10.0\n    }, \n    {\n      "_subtype": "Power_4", \n      "_type_": "Fitness", \n      "coeff": 89, \n      "spread": 10.0\n    }\n  ], \n  "_type_": "Small", \n  "fitness_calculator": "Linear", \n  "merge_module_chance": 50, \n  "module_mutation_chance": 50, \n  "name": "Solver2.1", \n  "property_mutation_chance": 10, \n  "resilience": 2, \n  "spread": 10, \n  "swap_module_chance": 15, \n  "total_modules": 5, \n  "unique": false\n}']

    def test_prune_solvers(self):
        """!!!Integration Test!!!"""
        random.seed(1)
        prune_solver_world = Terrarium()
        solvers_json = [{"_modules": [{"_subtype": "Cosine_4", "_type_": "Fitness"}], "name": "Solver1", "_type_": "Small", "fitness_calculator": "Linear"}, {
            "_modules": [{"_subtype": "Cosine_4", "_type_": "Fitness", }], "name": "Solver2", "_type_": "Small", "fitness_calculator": "Linear"}]
        prune_solver_world.importSolvers(solvers_json)
        prune_solver_world.runDays(1)
        prune_solver_world._max_solvers = 3
        solver_scores = [[solver, 5] for solver in prune_solver_world._solvers]
        prune_solver_world.pruneSolvers(solver_scores)
        total_living = 0
        total_dead = 0
        for solver in prune_solver_world._solvers:
            if solver.living:
                total_living += 1
            else:
                total_dead += 1
        assert total_living == 3
        assert total_dead == 1

    def test_specify_solver_conditions(self):
        """!!!Integration Test!!!"""
        specific_conditions_world = Terrarium()
        conditions = {"total_modules": 3}
        specific_conditions_world.importSolverConditions(conditions)
        specific_conditions_world.addSolver()
        assert specific_conditions_world._solvers[0].total_modules == 3
