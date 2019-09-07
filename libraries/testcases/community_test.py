import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../../'))

import networkx as nx
from networkx import edge_betweenness_centrality
from networkx.algorithms import centrality, community

from libraries.graph.graph import Graph, Node

class test():

	def set_weight(self, a):
		return 1 - a

	def most_central_edge(self, G):
		centrality = edge_betweenness_centrality(G, weight='weight')
		for (source, target), c in centrality.items():
			pass
			# print("%s-%s (%d-%d) %.2f" % (G.nodes[source]["name"], G.nodes[target]["name"], source, target, c))
		edge = max(centrality, key=centrality.get)
		print('removing edge', G.nodes[edge[0]]['name'], '-', G.nodes[edge[1]]['name'])
		return edge

	def testcase(self):
		a = Node("A")
		b = Node("B")
		c = Node("C")
		d = Node("D")
		g = Graph()

		g.add_edge(a, b, self.set_weight(0.5))
		g.add_edge(a, c, self.set_weight(0.5))
		g.add_edge(a, d, self.set_weight(0.5))

		g.add_edge(b, a, self.set_weight(0.5))
		g.add_edge(b, c, self.set_weight(0.5))
		g.add_edge(b, d, self.set_weight(0.5))

		g.add_edge(c, a, self.set_weight(0.5))
		g.add_edge(c, b, self.set_weight(0.5))
		g.add_edge(c, d, self.set_weight(0.5))
		
		nx_graph = g.to_networkx()

		centrality_scores = centrality.eigenvector_centrality(nx_graph) # calculate the centrality of nodes
		# print(centrality_scores)
		centrality_scores = centrality.eigenvector_centrality(nx_graph, weight='weight') # calculate the centrality of nodes
		# print(centrality_scores)
		
		gn = community.girvan_newman(nx_graph, most_valuable_edge=self.most_central_edge)

		for i in range(0, 3):
			top_level_partitions = next(gn)
			print(i, len(top_level_partitions))

			for partition in top_level_partitions:
				print(', '.join([ nx_graph.nodes[node]["name"] for node in partition ]))

test().testcase()
