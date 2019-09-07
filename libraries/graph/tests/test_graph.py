"""
Run unit tests on the Graph
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.append(path)

from libraries.graph.graph import Graph, Node

class TestGraph(unittest.TestCase):
	"""
	Test the Graph class
	"""

	def test_nodes(self):
		"""
		Test the nodes
		"""
		n1, n2 = Node(), Node()

		"""
		Test the node names
		"""
		self.assertEqual(n1.get_name(), "")
		self.assertEqual(n2.get_name(), "")

		n1.set_name("node1")
		n2.set_name("node2")

		self.assertEqual(n1.get_name(), "node1")
		self.assertEqual(n2.get_name(), "node2")

		"""
		Test node attributes
		"""
		n1.set_attribute("type", "c1")
		n2.set_attribute("type", "c2")
		self.assertEqual(n1.get_attribute("type"), "c1")
		self.assertEqual(n2.get_attribute("type"), "c2")

	def test_graph(self):
		"""
		Test the graph
		"""
		n1, n2, n3 = Node(), Node(), Node()
		g = Graph()

		"""
		Test adding and removing nodes
		"""
		self.assertEqual(g.size(), 0)
		g.add_node(n1)
		g.add_node(n2)
		self.assertEqual(g.size(), 2)

		g.remove_node(n1)
		self.assertEqual(g.size(), 1)
		self.assertEqual(g.get_nodes()[0], n2)

		"""
		Duplicate nodes should not be added
		"""
		g.add_node(n2)
		self.assertEqual(g.size(), 1)

		"""
		This should not raise an error
		"""
		g.remove_node(n3)

		g.add_node(n1)
		g.add_node(n2)
		g.add_node(n3)

		"""
		Test adding and removing undirected edges
		"""
		g.add_edge(n1, n2)
		self.assertEqual(g.get_edge(n1, n2), g.get_edge(n2, n1))
		self.assertEqual(g.get_edge(n1, n2), 1)
		g.remove_edge(n1, n2)
		self.assertEqual(g.get_edge(n1, n2), None)
		g.add_edge(n1, n2, weight=0.1)
		self.assertEqual(g.get_edge(n1, n2), 0.1)
		g.remove_edge(n1, n2)

		"""
		Test adding and removing directed edges
		"""
		g.add_edge(n1, n2, directed=True)
		self.assertEqual(g.get_edge(n1, n2), 1)
		self.assertEqual(g.get_edge(n2, n1), None)

		"""
		Test undirected removal
		"""
		g.remove_edge(n2, n1)
		self.assertEqual(g.get_edge(n1, n2), None)

		"""
		Test directed removal
		"""
		g.add_edge(n1, n2, directed=True)
		g.remove_edge(n2, n1, directed=True)
		self.assertEqual(g.get_edge(n1, n2), 1)

		g.add_edge(n1, n3, directed=True)
		self.assertEqual(len(g.get_neighbours(n1)), 2)

		"""
		Test that nodes are stored as references
		"""
		n3.set_attribute("type", "changed")
		print(str(sorted(g.get_neighbours(n1), key=lambda x: x.get_id())[::-1][0]))
		self.assertEqual(sorted(g.get_neighbours(n1), key=lambda x: x.get_id())[::-1][0].get_attribute("type"), n3.get_attribute("type"))

		"""
		Node removal
		"""
		g.remove_node(n3)
		self.assertEqual(g.size(), 2)
		self.assertEqual(len(g.get_neighbours(n1)), 1)
		g.remove_node(n3)
		self.assertEqual(g.size(), 2)
