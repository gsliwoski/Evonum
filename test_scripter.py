from evonum_scripter import *
import pytest
import random

class TestInitializations:
    """!!!Integration Tests!!!"""
    def test_initialize_world(self):
        test_script = ["World: 1, 2, 3"]
        test_world_script = SimpleScripter(test_script)
        assert test_world_script._worlds[0]._max_solvers == 1
        assert test_world_script._worlds[0]._max_forces == 2
        assert test_world_script._worlds[0]._chance_to_survive_prune == 3
    
    def test_initialize_world_bad_settings(self):
        test_script = ["World: a, b, c"]
        with pytest.raises(TypeError):
                test_bad_settings_world = SimpleScripter(test_script)            
    
    def test_initialize_world_no_settings(self):
        test_script = ["World"]
        with pytest.raises(IndexError):
            test_world_missing_settings = SimpleScripter(test_script)
    
    def test_add_force(self):
        test_script = ["World: 1, 2, 3", "Force: 1, Simple, Position, primes_1000.txt"]
        test_import_force = SimpleScripter(test_script)
        assert isinstance(test_import_force._worlds[0]._forces[0], SimplePosition)
    
    def test_add_force_bad_settings(self):
        test_script = ["World: 1, 2, 3", "Force: 1, 2, 3, 4"]
        test_import_bad_force = SimpleScripter(test_script)
        assert len(test_import_bad_force._worlds[0]._forces) == 0
    
    def test_add_force_no_settings(self):
        test_script = ["World: 1, 2, 3", "Force:"]
        test_import_force_no_settings = SimpleScripter(test_script)
        assert len(test_import_force_no_settings._worlds[0]._forces) == 0
    
    def test_add_five_solvers(self):
        test_script = ["World: 1, 2, 3", "Solver: 5"]
        five_solver_addition = SimpleScripter(test_script)
        assert len(five_solver_addition._worlds[0]._solvers) == 5

    def test_not_putting_world_first(self):
        test_script = ["Force: 1, Simple, Position, primes_1000.txt", "World: 1, 2, 3"]
    
class TestDefineSchedule:
    def test_add_run_500_days(self):
        test_script = ["World: 1, 2, 3", "Run: 500"]
        run_500_days_script = SimpleScripter(test_script)
        assert run_500_days_script._actions == ["Run_500"]

    def test_add_run_bad_number_of_days(self):
        test_script = ["World: 1, 2, 3", "Run: oops"]
        with pytest.raises(ValueError):
            bad_number_of_days_script = SimpleScripter(test_script)

    def test_add_end_world(self):
        test_script = ["World: 1, 2, 3", "End: 5, 50"]
        end_world_script = SimpleScripter(test_script)
        assert end_world_script._actions == ["End_5_50"]
    
    def test_add_end_world_bad_settings(self):
        test_script = ["World: 1, 2, 3", "End: idunno"]
        end_world_bad_settings = SimpleScripter(test_script)
        assert end_world_bad_settings._actions == []

class TestRunSchedule:
    """!!!Integration Tests!!!"""
    
    def test_run_5_days(self):
        test_script = ["World: 100, 2, 3", "Run: 2", "Solver: 1"]
        run_5_days = SimpleScripter(test_script)
        run_5_days.run()
        assert len(run_5_days._worlds[0]._solvers) == 4
        
    def test_end_world_10_solvers_to_5(self):
        test_script = ["World: 10, 2, 3", "Solver: 10", "End: 5, 5"]
        end_world_10_to_5 = SimpleScripter(test_script)
        initial_living_population = 0
        for solver in end_world_10_to_5._worlds[0]._solvers:
            if solver.living:
                initial_living_population += 1
        assert initial_living_population == 10
        end_world_10_to_5.run()
        final_living_population = 0
        for solver in end_world_10_to_5._worlds[0]._solvers:
            if solver.living:
                final_living_population += 1
        assert final_living_population == 5       
