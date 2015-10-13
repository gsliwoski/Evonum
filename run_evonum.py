from __future__ import print_function
import random, sys
from evonum_terrarium import *
from evonum_solvers import SolverFactory
from evonum_scripter import *

random.seed()
try:
	filename = sys.argv[1]
except:
	sys.exit("Command line: python run_evonum.py scriptfile.txt")
script = open(filename).readlines()
runner = SimpleScripter(script)
runner.run()
