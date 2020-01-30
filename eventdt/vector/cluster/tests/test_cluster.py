"""
Run unit tests on the Cluster class
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

from libraries.vector.vector import Vector
from libraries.vector.nlp.document import Document
from libraries.vector.nlp.term_weighting import TF
from libraries.vector.cluster.cluster import Cluster

class TestCluster(unittest.TestCase):
	"""
	Test the Cluster class
	"""

	def test_init(self):
		"""
		Test the Cluster constructor
		"""

		tf = TF()

		c = Cluster()
		e = Vector()
		self.assertEqual(c.get_centroid().get_dimensions(), e.get_dimensions())

		v = [
			Document("", ["a", "b", "a", "c"], scheme=tf),
		]

		c = Cluster(v)
		self.assertEqual(c.get_centroid().get_dimensions(), v[0].get_dimensions())

		v = [
			Document("", ["a", "b", "a", "c"], scheme=tf),
			Document("", ["a", "c"], scheme=tf),
		]
		c = Cluster(v)
		self.assertEqual(c.get_centroid().get_dimensions(), {"a": 1.5, "b": 0.5, "c": 1})

	def test_vector_change(self):
		"""
		Test adding and removing Vectors
		"""

		tf = TF()

		c = Cluster()
		v = [
			Document("", ["a", "b", "a", "c"], scheme=tf),
			Document("", ["a", "c"], scheme=tf),
			Document("", ["b"], scheme=tf),
		]

		e = Vector()

		self.assertEqual(c.get_centroid().get_dimensions(), Vector().get_dimensions())

		c.add_vector(v[0])
		self.assertEqual(c.get_centroid().get_dimensions(), v[0].get_dimensions())

		v[0].set_dimension("d", 1)
		self.assertEqual(c.get_centroid().get_dimension("d"), 0)
		c.add_vector(v[1])
		c.recalculate_centroid()
		self.assertEqual(c.get_centroid().get_dimensions(), {"a": 1.5, "b": 0.5, "c": 1, "d": 0.5})

		c.remove_vector(v[0])
		self.assertEqual(c.get_centroid().get_dimensions(), v[1].get_dimensions())

		c.set_vectors(v)
		self.assertEqual(c.get_centroid().get_dimensions(), {"a": 1, "b": 2./3., "c": 2./3., "d": 1./3.})

		n = Document("", ["a", "b"], scheme=tf)
		self.assertEqual(round(c.similarity(n), 5), round(5./6., 5))

		c.remove_vector(v[0])
		self.assertEqual(round(c.similarity(n), 5), round(math.sqrt(2/3), 5))

	def test_export(self):
		"""
		Test exporting and importing clusters.
		"""

		tf = TF()
		v = [
			Document("", ["a", "b", "a", "c"], scheme=tf),
			Document("", ["a", "c"], scheme=tf),
			Document("", ["b"], scheme=tf),
		]
		c = Cluster(v)

		e = c.to_array()
		r = Cluster.from_array(e)

		for i, vector in enumerate(r.get_vectors()):
			self.assertEqual(vector.__dict__, v[i].__dict__)
