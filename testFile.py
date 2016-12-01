# Test file: Simulate the table clearing task

import networkx as nx

env = nx.read_gpickle("G.gpickle")

# Initiate the class ParallelPlanner(Planar) with this environment. 

# ####
# Inside the class define functions to call the 
# necessary number of processes and run them parallelly until one of them succeeeds. For now run till both terminate individually.
# ####