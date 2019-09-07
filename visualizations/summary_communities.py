import json
import math
import os
import re
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import networkx as nx
from networkx import edge_betweenness_centrality
from networkx.algorithms import centrality, community

from libraries.graph.graph import Graph, Node

import palette

plt.style.use(os.path.join(sys.path[0], "ember_pastel.style"))

g = Graph()

HIGHLIGHTED = ["90", "97"]

with open("/home/memonick/output/temp/graph.json", "r") as f:
	summaries = f.readlines()
	summary = json.loads(summaries[8])
	nodes, edges = summary["nodes"], summary["edges"]

	graph_nodes = {}
	for id, node in nodes.items():
		graph_nodes[id] = Node(id, node)
		g.add_node(graph_nodes[id])

	for source in edges:
		for target, weight in edges[source].items():
			g.add_edge(graph_nodes[source], graph_nodes[target], weight)

nx_graph = g.to_networkx()
positions = nx.spring_layout(nx_graph)
# positions = { node: (x/2., y/2.) for node, (x, y) in positions.items() }
ordered_positions = sorted(positions.items(), key=lambda x: x[0])
x_positions = [ x for _, (x, y) in ordered_positions ]
y_positions = [ y for _, (x, y) in ordered_positions ]

lines = []
for source, target in nx_graph.edges:
	lines.append((positions[source], positions[target], nx_graph.edges[source, target]["weight"]))

plt.figure(figsize=(20,20))

for i, node in enumerate(nx_graph.nodes):
	x, y = x_positions[i], y_positions[i]
	highlighted = nx_graph.node[node]["name"] in HIGHLIGHTED
	plt.scatter(x, y, s=500, zorder=2,
		c=palette.primary["yellow"] if highlighted else palette.primary["red"],
		edgecolors=palette.stroke["yellow"] if highlighted else palette.stroke["yellow"],
		label="Summary document" if highlighted else "Document",
	)

for (x1, y1), (x2, y2), weight in lines:
	plt.plot([x1, x2], [y1, y2], zorder=1,
		color=palette.primary["red"],
		linewidth=(1 -weight)*3.5,
		label="Weighted similarity edge")

for node in nx_graph.nodes:
	if nx_graph.node[node]["name"] in HIGHLIGHTED:
		plt.text(positions[node][0],
			positions[node][1] + 0.025,
			re.sub("([!.?]) ", "\g<1>\n", nx_graph.node[node]["document"]),
			bbox=dict(facecolor="white", alpha=0.5))

handles, labels = plt.gca().get_legend_handles_labels()
labels = dict(zip(labels, handles))
labels = dict(sorted(labels.items(), key=lambda x: x[0]))
plt.legend(labels.values(), labels.keys())

plt.axis("off")
plot_margin = 0.25
x0, x1, y0, y1 = plt.axis()
plt.axis((x0 - plot_margin,
          x1 + plot_margin,
          y0 - plot_margin,
          y1 + plot_margin))
plt.xticks([])
plt.yticks([])
# plt.title("The document graph of a single development")
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/summary_communities.png")
