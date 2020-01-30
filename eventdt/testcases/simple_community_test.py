import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../../'))

import networkx as nx
from networkx import edge_betweenness_centrality
from networkx.algorithms import centrality, community

from libraries.graph.graph import Graph, Node

class test():

	def set_weight(self, a):
		return a

	def most_central_edge(self, G):
		centrality = edge_betweenness_centrality(G, weight='weight')
		for (source, target), c in centrality.items():
			# print("%s-%s (%d-%d) %.2f" % (G.nodes[source]["name"], G.nodes[target]["name"], source, target, c))
			pass
		edge = max(centrality, key=centrality.get)
		return edge

	def testcase(self):
		a = Node("A")
		b = Node("B")
		c = Node("C")
		d = Node("D")
		e = Node("E")
		
		f = Node("F")
		h = Node("H")
		i = Node("I")
		j = Node("J")
		k = Node("K")
		
		g = Graph()
		g.add_node(a)
		g.add_node(b)
		g.add_node(c)
		g.add_node(d)
		g.add_node(e)
		g.add_node(f)
		g.add_node(h)
		g.add_node(i)
		g.add_node(j)
		g.add_node(k)

		g.add_edge(a, b, self.set_weight(0.4))
		g.add_edge(a, c, self.set_weight(0.3))
		g.add_edge(a, d, self.set_weight(0.1))
		g.add_edge(a, e, self.set_weight(0.2))
		
		g.add_edge(f, h, self.set_weight(0.4))
		g.add_edge(f, i, self.set_weight(0.3))
		g.add_edge(f, j, self.set_weight(0.5))
		g.add_edge(f, k, self.set_weight(0.2))

		# g.add_edge(c, d, self.set_weight(0.8))

		nx_graph = g.to_networkx()
		# print(nx_graph.node[0])
		# print("Directed" if nx.is_directed(nx_graph) else "Undirected")
		# print(nx_graph.edges)

		# centrality_scores = centrality.eigenvector_centrality(nx_graph) # calculate the centrality of nodes
		# print(centrality_scores)
		# centrality_scores = centrality.eigenvector_centrality(nx_graph, weight='weight') # calculate the centrality of nodes
		# print(centrality_scores)

		communities = community.girvan_newman(nx_graph, most_valuable_edge=self.most_central_edge)
		for i in range(0, 5):
			top_level_partitions = next(communities)
		
			for partition in top_level_partitions:
				print("Community", ', '.join([ nx_graph.nodes[node]["name"] for node in partition ]))
			print()

test().testcase()
