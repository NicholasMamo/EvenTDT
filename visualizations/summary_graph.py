import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import networkx as nx
from networkx import edge_betweenness_centrality
from networkx.algorithms import centrality, community

from libraries.graph.graph import Graph, Node

a = Node("A")
b = Node("B")
c = Node("C")
d = Node("D")

x = Node("X")
y = Node("Y")
z = Node("Z")
g = Graph()

g.add_edge(a, b, 0.9)
g.add_edge(a, c, 0.8)
g.add_edge(a, d, 0.7)

g.add_edge(b, c, 0.7)
g.add_edge(b, d, 0.7)

g.add_edge(c, d, 0.8)

g.add_edge(x, y, 0.9)
g.add_edge(x, z, 0.7)

g.add_edge(y, z, 0.9)

g.add_edge(d, x, 0.1)
g.add_edge(b, y, 0.9)

nx_graph = g.to_networkx()
positions = nx.spring_layout(nx_graph)
x_positions = [ x for _, (x, y) in sorted(positions.items(), key=lambda x: x[0]) ]
y_positions = [ y for _, (x, y) in sorted(positions.items(), key=lambda x: x[0]) ]

lines = []
for source, target in nx_graph.edges:
	lines.append((positions[source], positions[target], nx_graph.edges[source, target]["weight"]))

plt.figure(figsize=(10,10))

plt.scatter(x_positions, y_positions)
for (x1, y1), (x2, y2), weight in lines:
	plt.plot([x1, x2], [y1, y2], linewidth=weight)

for node in nx_graph.nodes:
	plt.text(positions[node][0] + 0.025, positions[node][1] + 0.025, nx_graph.node[node]["name"])

plt.axis("off")
plt.xticks([])
plt.yticks([])
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/graph.png")
