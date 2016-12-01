import networkx as nx
import matplotlib.pyplot as plt

# Build directed graph
G = nx.DiGraph()

# Branch factor 2 at the root node (simplified abstract version of table clearing with two tasks?)
H = nx.path_graph(5)
G.add_nodes_from(H)

# Add the edges
G.add_edges_from([(0,1),(0,2),(1,3),(2,4)])

# 0 -> 1 -> 3
# 	-> 2 -> 4

# Save the grpah for later use
nx.write_gpickle(G,"G.gpickle")