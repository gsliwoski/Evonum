from __future__ import print_function
import random
import sys
from evonum_scripter import *

random.seed()
try:
    filename = sys.argv[1]
except:
    sys.exit("Command line: python run_evonum.py scriptfile.txt")
script = open(filename).readlines()
runner = SimpleScripter(script)
runner.run()
