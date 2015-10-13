# Evonum
Evolution simulator

To run example:
python run_evonum.py testscript.txt

Example runs evolutionary algorithm based on predicting nth prime number given n for 1<=n<=1000

Other examples can be run by changing the forces in the testscript.txt
Force: 1, Simple, Equation - uncomment this line to add a force for predicting tan(x) for -pi/2<=x<=pi/2
Force: 1, Dynamic, Equation - uncomment this line to add a force for predicting tan(x) for -pi/2<=x<=pi/2 using dynamic force that adjusts probability of x depending on solver performance.
Force: 1, Simple, Position, primes_1000.txt - this is the prime number force. 

Anything after '#' in script file is ignored.

Detailed explanations can be found in evonum_documentation.odt
