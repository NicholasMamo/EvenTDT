"""
A graph is made up of two different objects - nodes and edges.
"""

import os
import sys

import networkx as nx

path = os.path.join(os.path.dirname(__file__), "../")
if path not in sys.path:
    sys.path.append(path)

from objects.attributable import Attributable

class Graph(object):
	"""
	At its core, a Graph object contains a list of nodes.
	Nodes are stored in a dict, with their unique ID being the key, and the value being the node.
	Each node then has a list of edges.

	:ivar _nodes: The list of nodes making up the graph.
	:vartype _nodes: list of :class:`~graph.graph.Node`
	:ivar _edges: The list of edges connecting the nodes together.
	:vartype _edges: dict
	"""

	def __init__(self):
		"""
		Initialize an empty graph.
		"""

		super(Graph, self).__init__()
		self._nodes = {}
		self._edges = {}

	def add_node(self, node):
		"""
		Add a node to the graph.

		:param node: The node to add to the graph.
		:type node: :class:`~graph.graph.Node`
		"""

		"""
		Do not add duplicate nodes
		"""
		if node.get_id() not in self._nodes:
			self._nodes[node.get_id()] = node

	def remove_node(self, node):
		"""
		Remove a node from the graph.

		:param node: The node to remove from the graph.
		:type node: :class:`~graph.graph.Node`
		"""

		if node.get_id() in self._nodes:
			del self._nodes[node.get_id()]

		"""
		And remove all adjacent edges.
		"""
		for source in self._edges:
			if node.get_id() in self._edges[source]:
				del self._edges[source][node.get_id()]

	def get_nodes(self):
		"""
		Get all nodes in the graph.

		:return: A list of :class:`~graph.graph.Node` instances.
		:rtype: list
		"""

		return list(self._nodes.values())

	def size(self):
		"""
		Get the number of nodes in the graph.

		:return: The number of nodes in the graph.
		:rtype: int
		"""

		return len(self._nodes)

	def add_edge(self, source, target, weight=1, directed=False):
		"""
		Add an edge to the graph.
		If the edge is not directed, the edge is also added from the target to the source.

		:param source: The source node.
		:type source: :class:`~graph.graph.Node`
		:param target: The target node.
		:type target: :class:`~graph.graph.Node`
		:param weight: The weight associated with the edge.
		:type weight: float
		:param directed: A flag indicating whether the edge is directed.
		:type directed: bool
		"""

		self.add_node(source)
		self.add_node(target)

		"""
		Crete edge dictionary if need be.
		"""
		self._edges[source.get_id()] = self._edges.get(source.get_id(), {})
		self._edges[source.get_id()].update({ target.get_id() : weight })

		"""
		If the edge is not directed, add an edge from the target to the source as well.
		"""
		if not directed:
			self._edges[target.get_id()] = self._edges.get(target.get_id(), {})
			self._edges[target.get_id()].update({ source.get_id() : weight })

	def remove_edge(self, source, target, directed=False):
		"""
		Remove an edge from the graph
		If the removal is not directed, the edge is also removed from the target to the source.

		:param source: The source node.
		:type source: :class:`~graph.graph.Node`
		:param target: The target node.
		:type target: :class:`~graph.graph.Node`
		:param directed: A flag indicating whether the edge removal is directed.
		:type directed: bool
		"""

		if target.get_id() in self._edges.get(source.get_id(), {}):
			del self._edges.get(source.get_id(), {})[target.get_id()]

		"""
		If the edge is not directed, remove the edge from the target to the source as well.
		"""
		if not directed:
			if source.get_id() in self._edges.get(target.get_id(), {}):
				del self._edges.get(target.get_id(), {})[source.get_id()]

	def get_edges(self):
		"""
		Get all edges in the graph.

		:return: A list of edges.
		:rtype: list
		"""

		return self._edges

	def get_edge(self, source, target):
		"""
		Get the edge between the two nodes.

		:return: A single edge's information if it exists.
		:rtype: dict, or None if the edge does not exist.
		"""

		return self._edges.get(source.get_id(), {}).get(target.get_id(), None)

	def get_neighbours(self, node):
		"""
		Get the node's neighbours.

		:param node: The node whose neighbours are to be retrieved.
		:type node: :class:`~graph.graph.Node`

		:return: All of the node's neighbours.
		:rtype: list of :class:`~graph.graph.Node` instances
		"""

		return [ self._nodes[node_id] for node_id in self._edges.get(node.get_id(), {}).keys() ]

	def to_networkx(self):
		"""
		Convert the graph to a NetworkX graph.

		:return: The graph as a NetworkX graph.
		:rtype: :class:`~networkx.Graph`
		"""

		graph = nx.Graph()

		nodes = [ (node.get_id(), node.get_attributes()) for node in self._nodes.values() ]
		edges = [ (source, target, weight) for source in self._edges for target, weight in self._edges[source].items() ]

		graph.add_nodes_from(nodes)
		graph.add_weighted_edges_from(edges)

		return graph

	def to_array(self):
		"""
		Get the graph as a serializable array.
		Edges and nodes are separated.

		:return: The graph as an array.
		:rtype: dict
		"""

		return {
			"edges": self._edges,
			"nodes": { self._nodes[node].get_id(): self._nodes[node].to_array() for node in self._nodes },
		}

	def __repr__(self):
		"""
		Print the graph.

		:return: The pretty representation of the graph.
		:rtype: str
		"""

		s = ""
		s += "Nodes\n"
		for node in self._nodes:
			s += "\t%s\n" % str(node)

		s += "Edges\n"
		for source in self._edges:
			s += "\t%s\n" % str(source)
			for target, weight in self._edges[source]:
				s += "\t -> %s (%f)" % (str(target), weight)
		return s

class Node(Attributable):
	"""
	The Node class is based on the Attributable so that it may store additional attributes.

	:cvar _cid: A serial number, indicating a unique ID for nodes.
	:vartype _cid: int

	:ivar _name: The name of the node, which may not be unique.
	:vartype _name: str
	"""

	_cid = 0

	def __init__(self, name="", *args, **kwargs):
		"""
		Initialize the node with a unique ID, and an optional name.

		:param name: The node's name.
		:type name: str
		"""

		super(Node, self).__init__(*args, **kwargs)
		self._id = Node._cid
		Node._cid += 1
		self.set_name(name)

	def get_id(self):
		"""
		Get the node's ID.

		:return: The node's unique ID.
		:rtype: int
		"""

		return self._id

	def set_name(self, name):
		"""
		Set the node's pretty name.

		:param name: The node's name.
		:type name: str
		"""

		self._name = name
		self.set_attribute("name", name)

	def get_name(self):
		"""
		Get the node's pretty name.

		:return: The node's pretty name.
		:rtype: str
		"""

		return self._name

	def to_array(self):
		"""
		Get the node as a serializable array.

		:return: The node as an array.
		:rtype: dict
		"""

		attributes = dict(self._attributes)
		attributes["id"] = self.get_id()

		return attributes

	def __repr__(self):
		"""
		Print the node.

		:return: The pretty representation of the node.
		:rtype: str
		"""

		return "%d\t%s" % (self._id, self._name)
