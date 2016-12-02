# Test file: Simulate the table clearing task

import matplotlib.pyplot as plt
import networkx as nx
from multiPlanner import *
from monitor import *

#env = nx.read_gpickle("G.gpickle")

#pos = nx.spring_layout(env, iterations=100)
#plt.subplot(111)
#nx.draw(env, pos)

monitor = ActionMonitor()
planner = ParallelPlanner(monitor=monitor)

planner.plan_action(None, None)

#plt.show()



# Initiate the class ParallelPlanner(Planar) with this environment. 

# ####
# Inside the class define functions to call the 
# necessary number of processes and run them parallelly until one of them succeeeds. For now run till both terminate individually.
# ####
