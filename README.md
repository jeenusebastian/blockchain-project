# blockchain-project

This is project implemented for showing demonstration of "Effective scheme against 51% Attack on Proof-of-Work Blockchain with History Weighted Information" in simple python.

In this you can see resolve_conflict function implemented according to paper 

Example how to run:

-go to script folder 

-python3 blockchain.py -p 5000

-python3 blockchain.py -p 5001

-python3 blockchain.py -p 5002

This will run nodes at 5000 ,5001 and 5002 nodes.

Run test script by:

-python3 test.py

#you can change for loop change test script and window size in resolve_conflict to experiment with it.

In default one : When we look are last nodes we can see its mined by 1st and 2nd nodes(5000 and 5001) the blocks from malicious node is not accepted.If it was normal the conflict_resolution it malicious node should have been successfully.We can see by modifying it by Effective scheme against 51% Attack onProof-of-Work Blockchain with History Weighted Information we can see attack was not successfull.





