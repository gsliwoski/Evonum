# Evonum
Evolution simulator

GUI Branch includes tkinter-based simple GUI for plotting progress. Including the line "Plot" in testscript.txt loads the plotting GUI.

Refresh button plots top solver and displays details. Terminate ends simulation early and outputs top solver information.

Blue plot = Force target. Red plot = top solver.

To run example:
python run_evonum.py testscript.txt

Example runs evolutionary algorithm based on predicting nth prime number given n for 1<=n<=1000

Current top 5 solver details are refreshed in daily_dump.txt

Other examples can be run by changing the forces in the testscript.txt

Force: 1, Simple, Equation, 5.3*pow(x,2)+log(x,e) - uncomment this line to add a force for predicting 5.3*pow(x,2)+log(x,e) for 1<=x<=1000

Force: 1, Dynamic, Equation, tan(x) - uncomment this line to add a force for predicting tan(x) for -pi/2<=x<=pi/2 using dynamic force that adjusts probability of x depending on solver performance.

Force: 1, Simple, Position, primes_1000.txt - this is the prime number force. 

Anything after '#' in script file is ignored.

Detailed explanations can be found in evonum_documentation.odt

test_*.py are unit tests meant to be run with pytest (http://pytest.org/latest/).

