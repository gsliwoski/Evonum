from evonum_terrarium import *
import json

# Takes script from command line and interprets with extremely limited
# functionality.


class SimpleScripter(object):
    """Simple script file interpreter for setting up simulation and running."""

    def __init__(self, script):
        """Initialize simple scripter and set up run script.

        Requires raw script loaded from text file.
        """
        self._actions = []
        self._worlds = []
        self._solvers = []
        self._forces = []
        self._refresh_rate = [0, 0]
        self._export = None

        for line in script:
            line = line.strip()
            if "#" in line:
                line = line.split("#")[0]
            if line.startswith("World"):
                self._worlds.append(Terrarium())
                sets = [item.strip() for item in line.split(":")[1].split(",")]
                try:
                    settings = {"_max_solvers": int(sets[0]), "_max_forces": int(
                        sets[1]), "_chance_to_survive_prune": float(sets[2])}
                except IndexError:
                    raise IndexError(
                        "Error: World: must be followed with #max solver, #max forces, #chance to survive prune")
                except ValueError:
                    raise TypeError(
                        "Error: Bad type given for world setting(s).")
                # TODO: Complete ability to have multiple worlds running with
                # different solver conditions.
                self._worlds[-1].importSettings(settings)
#                try:
#                    solver_conditions = {"_total_modules": int(sets[3])}
#                except:
#                    solver_conditions = {}
#                self._worlds[-1].updateSolverConditions(solver_conditions)
                print ("New world created.")
            elif line.startswith("Force"):
                if len(self._worlds) == 0:
                    raise ValueError(
                        "Error: world initialization must be first line of script!")
                try:
                    sets = [item.strip()
                            for item in line.split(":")[1].split(",")]
                except IndexError:
                    print(
                        "Error: Force: must be followed with number, type, subtype, conditions. Force skipped.")
                    continue
                try:
                    total = int(sets[0])
                    force_type = sets[1]
                    force_subtype = sets[2]
                    force_conditions = ','.join(sets[3:])
                except (IndexError, ValueError):
                    print(
                        "Error: Force: must be followed with number, type, subtype, conditions. Force skipped.")
                    continue
                for x in range(0, int(sets[0])):
                    initial = len(self._worlds[-1]._forces)
                    self._worlds[-1].addForce(force_type,
                                              force_subtype, force_conditions)
                    if len(self._worlds[-1]._forces) > initial:
                        print ("%d fitness forces added to world of type %s and subtype %s" % (
                            total, force_type, force_subtype))
            elif line.startswith("Solver"):
                if len(self._worlds) == 0:
                    raise ValueError(
                        "Error: world initialization must be first line of script!")
                sets = int(line.split(":")[1].strip())
                for pos, item in enumerate(self._worlds):
                    for x in range(0, sets):
                        item.addSolver()
                    print ("%d solvers added to world%d." %
                           (int(sets), pos + 1))

            elif line.startswith("Import"):
                if len(self._worlds) == 0:
                    raise ValueError(
                        "Error: world initialization must be first line of script!")
                filename = line.split(":")[1].strip()
                print("Importing solvers from %s" % filename)
                solver_json = open(filename)
                solvers = json.load(solver_json)
                for world in self._worlds:
                    world.importSolvers(solvers)

            elif line.startswith("Refresh Solvers"):
                if len(self._worlds) == 0:
                    raise ValueError(
                        "Error: world initialization must be first line of script!")
                try:
                    sets = [item.strip()
                            for item in line.split(":")[1].split(",")]
                    self._refresh_rate = [int(sets[0]), int(sets[1])]
                    if self._refresh_rate[0] < 0:
                        self._refresh_rate[0] = 0
                    if self._refresh_rate[1] < 1:
                        self._refresh_rate[1] = 0
                except ValueError:
                    print("Error: bad type for refresh rate.")
                except IndexError:
                    print(
                        "Error: Refresh Solvers: must be followed with #solvers to refresh and #days between refresh.")
                if self._refresh_rate[0] == 0 or self._refresh_rate[1] == 0:
                    print ("Solvers will only be added before starting.")
                else:
                    print ("%d fresh solvers will be added every %d days." %
                           (self._refresh_rate[0], self._refresh_rate[1]))

            elif line.startswith("Run"):
                if len(self._worlds) == 0:
                    raise ValueError(
                        "Error: world initialization must be first line of script!")
                try:
                    duration = int(line.split(":")[1].strip())
                except (IndexError, ValueError):
                    raise ValueError(
                        "Error: Run: must be followed by int number of days to run.")
                self._actions.append("Run_" + str(duration))
            elif line.startswith("End"):
                try:
                    sets = [item.strip()
                            for item in line.split(":")[1].split(",")]
                    target = int(sets[0])
                    duration = int(sets[1])
                except (IndexError, ValueError):
                    print(
                        "Error: End: must be followed by target population and duration of end. Skipping end.")
                else:
                    self._actions.append(
                        "End_" + str(target) + "_" + str(duration))

            elif line.startswith("Export"):
                if len(self._worlds) == 0:
                    raise ValueError(
                        "Error: world initialization must be first line of script!")
                try:
                    self._export = line.split(":")[1].strip()
                except IndexError:
                    self._export = ""
                print("Solvers will be exported at run completion")

    # Run the schedule defined by the scripter after loading forces and
    # solvers into world.
    def run(self):
        """Run the schedule defined by the scripter after loading world, forces, and solvers."""
        print ("Running Schedule:")
        for item in self._actions:
            print (item)
        for item in self._actions:
            if item.startswith("Run"):
                lifespan = int(item.split("_")[1])
                if self._refresh_rate[1] > 0:
                    blocks = int(lifespan / self._refresh_rate[1])
                    block_size = self._refresh_rate[1]
                    remainder = lifespan % self._refresh_rate[1]
                else:
                    blocks = 1
                    block_size = lifespan
                    remainder = 0
                for x in range(0, blocks):
                    for y in range(0, block_size):
                        for each_world in self._worlds:
                            each_world.runDays(1)
                    if self._refresh_rate[1] > 0:
                        print ("Adding %d new solvers." %
                               self._refresh_rate[0])
                        for each_world in self._worlds:
                            for adding_solvers in range(0, self._refresh_rate[0]):
                                each_world.addSolver()
                for x in range(0, remainder):
                    for each_world in self._worlds:
                        each_world.runDays(1)

            elif item.startswith("End"):
                for all_worlds in self._worlds:
                    all_worlds.endWorld(
                        int(item.split("_")[1]), int(item.split("_")[2]))

        for pos, world in enumerate(self._worlds):
            world.printSolvers()
            solvers = world.exportSolvers()
            if self._export is not None:
                if len(solvers) > 0:
                    outfile = open(self._export + "world" +
                                   str(pos + 1) + "_solvers.json", "w")
                    outfile.write("[\n")
                    for item in solvers[:-1]:
                        outfile.write(item + ",\n")
                    outfile.write(solvers[-1] + "\n]\n")
                    outfile.close()
                else:
                    print("No solvers to export from world%d" % (pos + 1))
