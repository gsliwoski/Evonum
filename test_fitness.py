from evonum_fitness import *
import pytest

class TestFitnessForceCreation:
    def test_create_simple_position_fitness(self):
        filename = "primes_1000.txt"
        position_fitness = createFitnessForce("Simple", "Position", filename)
        assert position_fitness.type_ == "Simple"
        assert len(position_fitness._expected) == 1000
    
    def test_create_simple_equation_fitness(self):
        equation = "x+2*pow(x,2)"
        minimum = 5
        maximum = 15
        conditions = "x+2*pow(x,2), 5, 15"
        equation_fitness = createFitnessForce("Simple", "Equation", conditions)
        assert equation_fitness.type_ == "Simple"
        assert equation_fitness.min_ == minimum
        assert equation_fitness.max_ == maximum
        assert equation_fitness._equation_string == equation
    
    def test_create_dynamic_equation_fitess(self):
        equation = "tan(x) + 2*x"
        minimum = -5
        maximum = 5
        conditions = "tan(x) + 2*x, -5, 5"
        dynamic_equation_fitness = createFitnessForce("Dynamic", "Equation", conditions)
        assert dynamic_equation_fitness.type_ == "Dynamic"
        assert dynamic_equation_fitness.min_ == minimum
        assert dynamic_equation_fitness.max_ == maximum
        assert dynamic_equation_fitness._equation_string == equation

    def test_create_unknown_fitness_force(self):
        unknown_type_fitness = createFitnessForce("???", "Equation", "x,1,2")
        assert unknown_type_fitness is None
        unknown_subtype_fitness = createFitnessForce("Simple", "???", "x,1,2")
        assert unknown_subtype_fitness is None
    
    def test_create_force_badtype_conditions(self):
        with pytest.raises(TypeError):
            position_badtype_conditions = createFitnessForce("Simple", "Position", 1)
        with pytest.raises(TypeError):
            simple_equation_badtype_conditions = createFitnessForce("Simple", "Equation", False)
        with pytest.raises(TypeError):
            dynamic_equation_badtype_conditions = createFitnessForce("Dynamic", "Equation", 100.5)

class TestBeginDay:
    def test_position_fitness_force(self):
        position_force = createFitnessForce("Simple", "Position", "primes_1000.txt")
        position_force.beginDay()
        assert position_force._current_expected == position_force._expected[position_force._current_condition-1]
    
    def test_simple_equation_fitness_force(self):
        equation_force = createFitnessForce("Simple", "Equation", "x + 5*pow(x,2), 1, 10")
        equation_force.beginDay()
        variable = equation_force._current_condition
        expected = variable + 5*pow(variable,2)
        assert round(equation_force._current_expected) == round(expected)
   
    def test_dynamic_equation_fitness_force(self):
        dynamic_equation_force = createFitnessForce("Dynamic", "Equation", "x + 5*pow(x,2), 1, 10")
        dynamic_equation_force.beginDay()
        variable = dynamic_equation_force._current_condition
        expected = variable + 5*pow(variable,2)
        assert round(dynamic_equation_force._current_expected) == round(expected)
   
    def test_bad_equation_simple(self):
        bad_equation_force = createFitnessForce("Simple","Equation","log(x),-1,-5")
        with pytest.raises(ValueError):
            bad_equation_force.beginDay()
    
    def test_unrecognizable_equation_simple(self):
        unrecognizable_equation_force = createFitnessForce("Simple", "Equation", "siiiwl(x),1,2")
        with pytest.raises(NameError):
            unrecognizable_equation_force.beginDay()
    
    def test_bad_equation_dynamic(self):
        bad_equation_dynamic = createFitnessForce("Simple","Equation","log(x,5),-1,0")
        with pytest.raises(ValueError):
            bad_equation_dynamic.beginDay()
    
    def test_unrecognizable_equation_dynamic(self):
        unrecognizable_equation_dynamic = createFitnessForce("Dynamic","Equation", "roietioeo,2,3")
        with pytest.raises(NameError):
            unrecognizable_equation_dynamic.beginDay()
             
