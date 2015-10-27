from __future__ import print_function
import types
from evonum_fitness import *
from evonum_solvers import *
import json


def json_out(o):
    return o.exportDict()


class Terrarium(object):

    def __init__(self):
        self._current_day = 0
        self._forces = []
        self._solvers = []
        self._max_solvers = 100
        self._max_forces = 5
        self._chance_to_survive_prune = 1
        self._solver_settings = {}
        self._max_withheld = 100

    def addForce(self, force_type, force_subtype, conditions):
        """Add new fitness force to terrarium with provided type, subtype, and conditions."""
        if len(self._forces) >= self._max_forces:
            print ("Already at max forces. No force added.")
            return
        else:
            new_force = createFitnessForce(
                force_type, force_subtype, conditions)
        if new_force:
            self._forces.append(new_force)
        else:
            print("Error: failed to create force, no force added.")

    def addSolver(self, solver_type="Small"):
        """Add a new solver to terrarium of optional type."""
        # TODO: Solver name convention needs major improvements
        name = "Solver" + str(len(self._solvers) + 1) + \
            "_" + str(self._current_day) + ".1"
        if solver_type == "Small":
            self._solvers.append(createSolver(
                "Small", name, self._solver_settings))
        else:
            print("Error: unknown solver type %s. No solver added." % solver_type)

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
        # For printing to screen or other logging
        solver_scores, withheld_solvers = self.scoreSolvers()
        if len(solver_scores) > 0:
            print ("%d\t%.2f" % (self._current_day, solver_scores[0][1]))
        else:
            print("%d\tAll solvers dead or withheld!" % self._current_day)
        self.pruneWithheld(withheld_solvers)
        self.writeDay(solver_scores, withheld_solvers)  # TODO: Will be changed
        # If more solvers than max for environment, assess solvers based on
        # fitness and flag the failures for death.
        self.pruneSolvers(solver_scores)

    def reproduceSolvers(self):
        """Reproduce all living solvers."""
        babies = []
        for solver in self._solvers:
            if solver.fitness is not None:
                babies.append(solver.reproduce())
        self._solvers += babies

    def evaluateSolvers(self):
        """Evaluate solver fitness."""
        for solver in self._solvers:
            solver.calculateFitness(self._forces)

    def scoreSolvers(self):
        """Returns non-withheld living solvers sorted by fitness as a 
        list with each position [solver object, solver fitness (float), solver age (int)], 
        withheld solvers unsorted."""
        solver_scores = []
        withheld_solvers = []
        fit = 0
        for solver in self._solvers:
            if solver.fitness is None:
                if len(withheld_solvers) < self._max_withheld:
                    withheld_solvers.append(solver)
                else:
                    continue
            elif solver.living:
                solver_scores.append([solver, solver.fitness, solver.age])
        if len(solver_scores) > 0:
            solver_scores.sort(key=lambda x: x[1], reverse=True)
        return solver_scores, withheld_solvers

    def writeDay(self, solver_scores, withheld_solvers):
        """Write daily stats and top solvers for current day into daily_dump.txt"""
        avg = 0
        outfile = open("daily_dump.txt", "w")
        outfile.write("Day " + str(self._current_day))
        if len(solver_scores) > 0:
            for item in solver_scores:
                avg += item[1]
            avg = avg / len(solver_scores)
            outfile.write(" AvgFit: " + str(avg) +
                          " MaxFit: " + str(solver_scores[0][1]))
        else:
            outfile.write(" All solvers dead or withheld!")
        outfile.write("\nForces:\n")
        for item in self._forces:
            outfile.write(item.getDescription() + "\n")
        outfile.write("Total solvers withheld due to math domain failure: %d\n" % len(
            withheld_solvers))
        if len(solver_scores) > 0:
            outfile.write("\n" + "=" * 50 + "\n")
            outfile.write("Top 5 solvers:\n")
            for item in solver_scores[:4]:
                outfile.write(item[0].getDescription())
            outfile.write("\nOldest solvers\n")
            solver_scores.sort(key=lambda x: x[2], reverse=True)
            for item in solver_scores[:2]:
                outfile.write(item[0].getDescription())
            outfile.write("\n")
        outfile.close()

    def pruneSolvers(self, solver_scores):
        """Remove solvers with lowest fitness score."""
        if len(solver_scores) < self._max_solvers:
            #			print ("No pruning necessary")
            pass
        else:
            #			print ("Population: %s\tMax Population: %s\tNeed to kill: %s" % (len(self._solvers), self._max_solvers, len(self._solvers)-self._max_solvers))
            #            solver_scores = [[x] for x in self._solvers]
            for item in solver_scores[self._max_solvers:]:
                # Each solver failing the fitness check has a last chance to
                # survive
                luckyday = True if random.randint(
                    1, 100) <= self._chance_to_survive_prune else False
                if not luckyday:
                    item[0].death()
        for item in self._forces:
            # Dynamic fitness forces adjust the chance of each random variable
            # based on past performance of solvers. Give solvers a 100 days to
            # adapt first.
            if item.type_ == "Dynamic" and self._current_day > 100 and len(solver_scores) > 0:
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

    def pruneWithheld(self, withheld_solvers):
        if len(withheld_solvers) < self._max_withheld:
            pass
        else:
            for item in withheld_solvers[self._max_withheld:]:
                item.death()
        return None

    # Print solvers that have survived at least one day.
    def printSolvers(self):
        """Print descriptions of solvers that have survived at least 1 day."""
        for solver in self._solvers:
            if solver.age > 0 and solver.living:
                print (solver.getDescription())

    def printForces(self):
        """Print descriptions of all loaded forces."""
        for force in self._forces:
            print (force.getDescription())

#    def importForce(self, force):
#        if len(self._forces) >= self._max_forces:
#            print ("Already at max forces")
#            return
#        else:
#            self._forces.append(force)

    def exportSolvers(self):
        """Exports array of all living solvers as json strings"""
        solver_jsons = []
        for item in self._solvers:
            if item.age > 0 and item.living:
                solver_jsons.append(json.dumps(
                    item, default=json_out, indent=2, sort_keys=True))
        return solver_jsons

    def importSolvers(self, solvers_json):
        """Imports list of solvers in json string format."""
        if not isinstance(solvers_json, types.StringTypes):
            prev = len(self._solvers)
            try:
                for item in solvers_json:
                    self._solvers.append(importSolver(item))
                print("%d solvers imported to world." %
                      (len(self._solvers) - prev))
            except TypeError:
                print(
                    "Error: import solvers must recieve iterable list of solver jsons, unable to import.")
        else:
            print(
                "Error: import solvers must recieve iterable list of solver jsons, unable to import.")

    def endWorld(self, days, destination):
        """Ramp down max population each day to reach final value in shape 1/x.

        Takes days, destination where days = number of days to ramp down and destination = target population.
        """
        try:
            days = int(days)
            destination = int(destination)
        except ValueError:
            print("Bad # of days or destination population provided. WorldEnd skipped.")
            return
        if destination > self._max_solvers:
            destination = self._max_solvers
        m = (self._max_solvers - destination) * days / (days - 1)
        b = self._max_solvers - m
        for x in range(1, days + 1):
            self._max_solvers = int(m / x + b + .5)
            self.runDays(1)

    def importSolverSettings(self, conditions):
        self._solver_settings.update(conditions)

    def importSettings(self, settings):
        try:
            for item in settings:
                if item == "_max_solvers":
                    self._max_solvers = settings[item]
                elif item == "_max_forces":
                    self._max_forces = settings[item]
                elif item == "_chance_to_survive_prune":
                    self._chance_to_survive_prune = settings[item]
        except TypeError:
            print("Error: unable to import terrarium settings, leaving at default!")
