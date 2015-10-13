from evonum_terrarium import *

class SimpleScripter(object):
	def __init__(self, script):
		self._actions = []
		self._world = Terrarium()
		self._solvers = []
		self._forces = []
		self._refresh_rate = [0,0]
		
		for line in script:
			if "#" in line:
				line = line.split("#")[0]
			if line.startswith("World"):
				sets = [item.strip() for item in line.split(":")[1].split(",")]
				settings = {"_max_solvers": int(sets[0]), "_max_forces": int(sets[1]), "_chance_to_survive_prune": int(sets[2])}
				self._world.importAttributes(settings)
				print ("New world created.")
			elif line.startswith("Force"):
				sets = [item.strip() for item in line.split(":")[1].split(",")]
				for x in range(0,int(sets[0])):
					try:
						self._world.addForce(sets[1], sets[2], sets[3])
					except:
						self._world.addForce(sets[1], sets[2]) #This is only here because the equation one can't take conditions yet.
				print ("%d fitness forces added to world of type %s and subtype %s" % (int(sets[0]), sets[1], sets[2]))
			elif line.startswith("Solver"):
				sets = int(line.split(":")[1].strip())
				for x in range(0,sets):
					self._world.addSolver()
				print ("%d solvers added to world." % int(sets))
			
			elif line.startswith("Refresh Solvers"):
				sets = [int(item.strip()) for item in line.split(":")[1].split(",")]
				self._refresh_rate = sets
				if self._refresh_rate[0] == 0:
					print ("Solvers will only be added before starting.")
				else:
					print ("%d fresh solvers will be added every %d days." % (self._refresh_rate[0], self._refresh_rate[1]))
			
			elif line.startswith("Run"):
				duration = int(line.split(":")[1].strip())
				self._actions.append("Run_"+str(duration))
			elif line.startswith("End"):
				sets = [item.strip() for item in line.split(":")[1].split(",")]
				target = int(sets[0])
				duration = int(sets[1])
				self._actions.append("End_"+str(target)+"_"+str(duration))
		
			
#		self._world.printLivingSolvers()
		self._world.runDays(1)
#		self._world.printForces()
		solvers = self._world.exportSolvers()		
#		for item in solvers:
#			print item
	def run(self):
		print ("Running Schedule:")
		for item in self._actions:
			print (item)
		for item in self._actions:
			if item.startswith("Run"):
				lifespan = int(item.split("_")[1])
				if self._refresh_rate[1] > 0:
					blocks = int(lifespan/self._refresh_rate[1])
					block_size = self._refresh_rate[1]
					remainder = lifespan%self._refresh_rate[1]
				else:
					blocks = 1
					block_size = lifespan
					remainder = 0
				print ("blocks: %d, block_size: %d, remainder: %d" % (blocks, block_size, remainder))
				for x in range(0,blocks):
					self._world.runDays(block_size)
					if self._refresh_rate[1] > 0:
						print ("Adding %d new solvers." % self._refresh_rate[0])
						for y in range(0,self._refresh_rate[0]):
							self._world.addSolver()
				if remainder>0:
					self._world.runDays(remainder)
			
			elif item.startswith("End"):
				self._world.endWorld(int(item.split("_")[1]), int(item.split("_")[2]))
		
		self._world.printLivingSolvers()
		outfile = open("output","w")
		solvers = self._world.exportSolvers()
		for item in solvers:
			outfile.write(str(item)+"\n")
		outfile.close()
		
	
class Scripter(object): #TODO: Far from finished
	def __init__(self, script):
		self._actions = []
		self._worlds = []
		self._solvers = []
		self._forces = []

		status = ""
		status_counter = 0
		settings = {}
		for line in script:
		#	if line.startswith("New"):
			#	if status == "world" and len(settings)>0:
			#		self.
			if line == "New World":
				status = "world"
				self._worlds.append(Terrarium())

			elif line.startswith("New Solver"):
				linesplit = line.split(":")
				try:
					status_counter = int(linesplit[1])
				except:
					status_counter = 1
				status = "solver"
					
			elif line.startswith("New Fitness Force"):
				linesplit = line.split(":")
				try:
					status_counter = int(linesplit[1])
				except:
					status_counter = 1
				status = "force"
			
			elif line == "Actions":
				status = "action"
			
			elif status == "world":
				if line.startswith("Max Population"):
					split_line = line.split(":")
					try:
						settings["_max_solvers"] = int(split_line[1])
					except:
						settings["_max_solvers"] = 100
				elif line.startswith("Max Forces"):
					split_line = line.split(":")
					try:
						settings["_max_forces"] = int(split_line[1])
					except:
						settings["_max_forces"] = 5
				elif line.startswith("Savior Chance"):
					split_line = line.split(":")
					try:
						settings["_chance_to_survive_prune"] = float(split_line[1])
					except:
						settings["_chance_to_survive_prune"] = 1
			
				
