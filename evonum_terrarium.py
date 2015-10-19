from __future__ import print_function
from evonum_fitness import *
from evonum_solvers import *


class Terrarium(object):

    def __init__(self):
        self._current_day = 0
        self._forces = []
        self._solvers = []
        self._max_solvers = 100
        self._max_forces = 2
        self._chance_to_survive_prune = 1
        self._solver_conditions = {}

    def addForce(self, force_type, force_subtype, conditions):
        """Add new fitness force to terrarium with provided type, subtype, and conditions."""
        if len(self._forces) >= self._max_forces:
            print ("Already at max forces")
            return None
        elif force_type == "Simple":
            if force_subtype == "Position":
                new_force = SimplePosition(
                    "PositionForce" + str(len(self._forces) + 1))
            elif force_subtype == "Equation":
                new_force = SimpleEquation(
                    "EquationForce" + str(len(self._forces) + 1))
            elif force_subtype == "Identity":
                new_force = SimpleIdentity(
                    "IdentityForce" + str(len(self._forces) + 1))
            else:
                print ("Unknown Simple subtype")
                return None
        elif force_type == "Dynamic":
#			if force_subtype == "Position": #TODO: Add dynamic position fitness force
#				new_force = DynamicPosition
            if force_subtype == "Equation":
                new_force = DynamicEquation(
                    "DynamicEquationForce" + str(len(self._forces) + 1))
        else:
            print ("Unknown force")
            return None
        new_force.loadConditions(conditions)
        self._forces.append(new_force)

    def addSolver(self, solver_type="Small"):
        """Add a new solver to terrarium of optional type."""
        # TODO: Solver name convention needs major improvements
        name = "Solver" + str(len(self._solvers) + 1) + \
            "_" + str(self._current_day) + ".1"
        self._solvers.append(createSolver("Small", name, self._solver_conditions))

    def runDays(self, total=0):
        """Run for provided number of days. If nothing provided, run indefinitely."""
        if total < 1:
            while True:
                self.beginDay()
        else:
            for x in range(0, total):
                self.beginDay()

    def beginDay(self):
        """Increment day, reproduce living solvers, evaluate solver fitness, and prune solvers based on fitness rank."""
        self._current_day += 1
#        print("-"*20+"Beginning Day "+str(self._current_day)+"-"*20)
        dead_solvers = []
        for item in self._forces:
            item.beginDay()
        for pos, item in enumerate(self._solvers):
            still_living = item.beginDay()
            if not still_living:
                dead_solvers.append(pos)
        surviving = [sol for pos, sol in enumerate(
            self._solvers) if pos not in dead_solvers]  # Remove dead solvers
        self._solvers = surviving
        self.reproduceSolvers()  # Every surviving solver reproduces once at start of day
        self.evaluateSolvers()  # Every solver and new progeny gets evaluated
        maxfit, avgfit = self.getMetrics()  # For printing to screen or other logging
        print ("%d\t%.2f" % (self._current_day, maxfit))
        self.writeDay()  # TODO: Will be changed
        # If more solvers than max for environment, assess solvers based on
        # fitness and flag the failures for death.
        self.pruneSolvers()

    def reproduceSolvers(self):
        """Reproduce all living solvers."""
        babies = []
        for solver in self._solvers:
            babies.append(solver.reproduce())
        self._solvers += babies

    def evaluateSolvers(self):
        """Evaluate solver fitness."""
        for solver in self._solvers:
            solver.calculateFitness(self._forces)

    def getMetrics(self):
        """Get daily metrics such as avg fitness, max fitness, min fitness"""
        fit = 0
        max_fit = None
        min_fit = None
        for item in self._solvers:
            fit += item.fitness
            if max_fit == None or item.fitness > max_fit:
                max_fit = item.fitness
            if min_fit == None or item.fitness < min_fit:
                min_fit = item.fitness
        avgfit = fit / len(self._solvers)
#		print ("="*15+"Daily Metrics"+"="*15)
#		print ("Average Fitness: %.2f" % avgfit)
#		print ("Maximum Fitness: %.2f" % max_fit)
#		print ("Minimum Fitness: %.2f" % min_fit)
#		print ("="*30)
        return max_fit, avgfit

    def writeDay(self):
        """Write daily stats and top solvers for current day into daily_dump.txt"""
        outfile = open("daily_dump.txt", "w")
        max_fit, avgfit = self.getMetrics()
        outfile.write("Day " + str(self._current_day) + " AvgFit: " +
                      str(avgfit) + " MaxFit: " + str(max_fit) + " Forces:\n")
        for item in self._forces:
            outfile.write(item.getDescription() + "\n")
        outfile.write("\n" + "=" * 50 + "\n")
        solver_scores = [[x] for x in self._solvers]
        for item in solver_scores:
            item.append(item[0].fitness)
        for item in solver_scores:
            item.append(item[0].age)
        solver_scores.sort(key=lambda x: x[1], reverse=True)
        outfile.write("Top 5 solvers:\n")
        for item in solver_scores[:4]:
            outfile.write(item[0].getDescription())  
        outfile.write("\nOldest solvers\n")
        solver_scores.sort(key=lambda x: x[2], reverse=True)
        for item in solver_scores[:2]:
            outfile.write(item[0].getDescription())
        outfile.write("\n")      
        outfile.close()

    def pruneSolvers(self):
        """Remove solvers with lowest fitness score."""
        if len(self._solvers) < self._max_solvers:
#			print ("No pruning necessary")
            pass
        else:
#			print ("Population: %s\tMax Population: %s\tNeed to kill: %s" % (len(self._solvers), self._max_solvers, len(self._solvers)-self._max_solvers))
            solver_scores = [[x] for x in self._solvers]
            for item in solver_scores:
                item.append(item[0].fitness)
            solver_scores.sort(key=lambda x: x[1], reverse=True)
            for item in solver_scores[self._max_solvers:]:
                # Each solver failing the fitness check has a last chance to
                # survive
                luckyday = True if random.randint(
                    1, 100) <= self._chance_to_survive_prune else False
                if not luckyday:
                    item[0].Death()
        for item in self._forces:
            # Dynamic fitness forces adjust the chance of each random variable
            # based on past performance of solvers. Give solvers a 100 days to
            # adapt first.
            if item.type_ == "Dynamic" and self._current_day > 100:
                avg = item.avg_fitness
                if solver_scores[0][1] >= avg[0]:
                    increase = False
                else:
                    increase = True
                avg[0] = (avg[0] * avg[1] + solver_scores[0][1]) / (avg[1] + 1)
                avg[1] += 1
                item.avg_fitness = avg
                condition, temp = item.conditions
                item.updateConditionProbability(condition, increase)
#			for item in solver_scores:
#				print (item[0].name+"\t"+str(item[1]))

    def printLivingSolvers(self):
        for solver in self._solvers:
            if solver.living:
                print (solver.getDescription())
                print ("Fitness score: %.2f" % solver.fitness)

    # Print solvers that have survived at least one day.
    def printOldSolvers(self):
        for solver in self._solvers:
            if solver.age > 0:
                print (solver.getDescription())
                print ("Fitness score: %.2f" % solver.fitness)

    def printForces(self):
        for force in self._forces:
            print (force.getDescription())

    def importSolver(self, solver):
        self._solvers.append(solver)

    def importForce(self, force):
        if len(self._forces) >= self._max_forces:
            print ("Already at max forces")
            return
        else:
            self._forces.append(force)

    def exportSolvers(self): #TODO: pickle
        solverdicts = []
        for item in self._solvers:
            solverdicts.append(item.export())
        return solverdicts

    def importSolverDicts(self, solverdicts): #TODO: pickle
        for item in solverdicts:
            self._solvers.append(importSolver(item))

    def clearSolvers(self):
        self._solvers = []

    def clearFitness(self):
        self._forces = []

    def endWorld(self, days, destination):
        """Ramp down max population each day to reach final value in shape 1/x.
    
        Takes days, destination where days = number of days to ramp down and destination = target population.
        """
        m = (self._max_solvers - destination) * days / (days - 1)
        b = self._max_solvers - m
        for x in range(1, days + 1):
            self._max_solvers = int(m / x + b + .5)
#			print ("Max solvers:",self._max_solvers)
            self.runDays(1)

    def importAttributes(self, attributes):#TODO: remove or improve
        for item in attributes:
            setattr(self, item, attributes[item])
    
    def updateSolverConditions(self, conditions):
        self._solver_conditions.update(conditions)   
