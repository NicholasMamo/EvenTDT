"""
Run unit tests on the Cluster class
"""

import math
import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from clustering.cluster import Cluster
from nlp.document import Document
from nlp.term_weighting.tf import TF
from vector import Vector
from vsm.vector import VectorSpace

class TestCluster(unittest.TestCase):
	"""
	Test the Cluster class
	"""

	def test_empty_cluster(self):
		"""
		Test that an empty cluster has a centroid with no dimensions.
		"""

		c = Cluster()
		self.assertEqual({}, c.centroid.dimensions)

	def test_cluster_with_one_vector(self):
		"""
		Test that the centroid of a cluster with a single vector has an equivalent centroid.
		"""

		v = Document("", ["a", "b", "a", "c"], scheme=TF())
		c = Cluster(v)
		self.assertEqual(v.dimensions, c.centroid.dimensions)

	def test_cluster_with_several_vectors(self):
		"""
		Test creating a cluster with several vectors.
		"""

		v = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF()),
		]
		c = Cluster(v)
		self.assertEqual({"a": 1.5, "b": 0.5, "c": 1}, c.centroid.dimensions)

	def test_vectors_reference(self):
		"""
		Test that when a vector changes, the same vector in the cluster also changes.
		"""

		v = Document("", ["a", "b", "a", "c"], scheme=TF())
		c = Cluster(v)
		self.assertEqual(v.dimensions, c.centroid.dimensions)

		v.dimensions["d"] = 1
		self.assertEqual(1, c.vectors[0].dimensions["d"])
		self.assertEqual(0, c.centroid.dimensions["d"])
		c.recalculate_centroid()
		self.assertEqual(1, c.vectors[0].dimensions["d"])
		self.assertEqual(1, c.centroid.dimensions["d"])

	def test_add_vectors(self):
		"""
		Test adding vectors to a cluster gradually.
		"""

		c = Cluster()
		v = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF())
		]

		self.assertEqual({}, c.centroid.dimensions)

		c.add_vector(v[0])
		self.assertEqual(v[0].dimensions, c.centroid.dimensions)

		c.add_vector(v[1])
		self.assertEqual({"a": 1.5, "b": 0.5, "c": 1}, c.centroid.dimensions)

	def test_remove_vectors(self):
		"""
		Test removing vectors from a cluster gradually.
		"""

		v = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF())
		]
		c = Cluster(v)
		self.assertEqual({"a": 1.5, "b": 0.5, "c": 1}, c.centroid.dimensions)
		c.remove_vector(v[0])
		self.assertEqual(1, c.centroid.dimensions['a'])
		self.assertEqual(0, c.centroid.dimensions['b'])
		self.assertEqual(1, c.centroid.dimensions['c'])

		c = Cluster(v)
		self.assertEqual({"a": 1.5, "b": 0.5, "c": 1}, c.centroid.dimensions)
		c.remove_vector(v[1])
		self.assertEqual(v[0].dimensions, c.centroid.dimensions)
		c.remove_vector(v[0])
		self.assertEqual(0, c.centroid.dimensions['a'])
		self.assertEqual(0, c.centroid.dimensions['b'])
		self.assertEqual(0, c.centroid.dimensions['c'])

	def test_setting_vectors(self):
		"""
		Test setting the vectors manually.
		"""

		v = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF())
		]
		c = Cluster()
		self.assertEqual({}, c.centroid.dimensions)
		c.vectors = v
		self.assertEqual(c.centroid.dimensions, {"a": 1.5, "b": 0.5, "c": 1})

	def test_cluster_similarity(self):
		"""
		Test calculating the similarity between a cluster and a new vector.
		"""

		v = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF())
		]
		c = Cluster(v)

		n = Document("", ["a", "b"], scheme=TF())
		self.assertEqual(round((1.5 + 0.5)/(math.sqrt(2) * math.sqrt(1.5 ** 2 + 0.5 ** 2 + 1)), 5), round(c.similarity(n), 5))

		c.remove_vector(v[1])
		self.assertEqual(round(3/(math.sqrt(2) * math.sqrt(2**2 + 1 + 1)), 5), round(c.similarity(n), 5))

	def test_empty_cluster_similarity(self):
		"""
		Test that when calculating the similarity between a vector and an empty cluster, the similarity is 0.
		"""

		c = Cluster()
		v = Document("", ["a", "c"], scheme=TF())
		self.assertEqual(0, c.similarity(v))

	def test_recalculate_centroid(self):
		"""
		Test when a vector changes, and the centroid is re-calculated, it is correct.
		"""

		v = [ Document("", [ ]), Document("", [ ]) ]
		c = Cluster(v)
		self.assertEqual({ }, c.centroid.dimensions)

		v[0].dimensions = { 'a': 1, 'b': 1 }
		self.assertEqual(VectorSpace, type(v[0].dimensions))
		self.assertEqual({ }, c.centroid.dimensions)
		c.recalculate_centroid()
		self.assertEqual({ 'a': 0.5, 'b': 0.5 }, c.centroid.dimensions)

		v[1].dimensions = { 'a': 1 }
		self.assertEqual(VectorSpace, type(v[1].dimensions))
		self.assertEqual({ 'a': 0.5, 'b': 0.5 }, c.centroid.dimensions)
		c.recalculate_centroid()
		self.assertEqual({ 'a': 1, 'b': 0.5 }, c.centroid.dimensions)

	def test_set_vectors_none(self):
		"""
		Test that setting vectors to `None` overwrites existing vectors.
		"""

		v = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF())
		]
		c = Cluster(v)
		self.assertEqual(v, c.vectors)

		c.vectors = None
		self.assertEqual([ ], c.vectors)
		self.assertEqual({ }, c.centroid.dimensions)

	def test_set_one_vectors(self):
		"""
		Test that setting vectors to a single vector overwrites existing vectors.
		"""

		v = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF())
		]
		c = Cluster(v)
		self.assertEqual(v, c.vectors)

		n = Document("", [ 'a' ], scheme=TF())
		c.vectors = n
		self.assertEqual([ n ], c.vectors)
		self.assertEqual(n.dimensions, c.centroid.dimensions)

	def test_set_several_vectors(self):
		"""
		Test that setting vectors to several vectors overwrites existing vectors.
		"""

		v = Document("", [ 'a' ], scheme=TF())
		c = Cluster(v)
		self.assertEqual([ v ], c.vectors)
		self.assertEqual(v.dimensions, c.centroid.dimensions)

		n = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF())
		]

		c.vectors = n
		self.assertEqual(n, c.vectors)
		self.assertEqual({ 'a': 1.5, 'b': 0.5, 'c': 1 }, c.centroid.dimensions)

	def test_get_representative_vector(self):
		"""
		Test ranking the vectors according to their similarity to the cluster.
		"""

		v = [
			Document("", [ 'a', 'b', 'c' ], scheme=TF()),
			Document("", [ 'a', 'a', 'c' ], scheme=TF()),
			Document("", [ 'p' ], scheme=TF()),
		]
		c = Cluster(v)
		self.assertEqual(Document, type(c.get_representative_vectors(1)))
		self.assertEqual(v[1], c.get_representative_vectors(1))

	def test_get_representative_vectors(self):
		"""
		Test ranking the vectors according to their similarity to the cluster.
		"""

		v = [
			Document("", [ 'a', 'b', 'c' ], scheme=TF()),
			Document("", [ 'a', 'a', 'c' ], scheme=TF()),
			Document("", [ 'p' ], scheme=TF()),
		]
		c = Cluster(v)
		self.assertEqual(list, type(c.get_representative_vectors(2)))
		self.assertEqual([ v[1], v[0] ], c.get_representative_vectors(2))

	def test_get_representative_vectors_from_empty_cluster(self):
		"""
		Test that when getting the representative vectors from an empty cluster, an empty list is returned.
		"""

		c = Cluster()
		self.assertEqual(list, type(c.get_representative_vectors(2)))
		self.assertEqual([ ], c.get_representative_vectors(2))

	def test_get_representative_vector_from_empty_cluster(self):
		"""
		Test that when getting the representative vector from an empty cluster, `None` is returned.
		"""

		c = Cluster()
		self.assertEqual(None, c.get_representative_vectors(1))

	def test_intra_similarity_of_empty_cluster(self):
		"""
		Test that the intra-similarity of an empty cluster is 0.
		"""

		c = Cluster()
		self.assertEqual(0, c.get_intra_similarity())

	def test_intra_similarity_of_cluster_with_single_vector(self):
		"""
		Test that the intra-similarity of a cluster with a single vector is equivalent to that vector's similarity with the cluster.
		"""

		v = Document("", [ 'a', 'b' ], scheme=TF())
		c = Cluster(v)
		self.assertEqual(c.similarity(v), c.get_intra_similarity())

	def test_intra_similarity_of_cluster(self):
		"""
		Test that the intra-similarity of a cluster with several vectors is equivalent to the average similarity.
		"""

		v = [
			Document("", [ 'a', 'b' ], scheme=TF()),
			Document("", [ 'a', 'a' ], scheme=TF()),
		]
		c = Cluster(v)
		self.assertEqual((c.similarity(v[0]) + c.similarity(v[1]))/2., c.get_intra_similarity())

	def test_size_empty_cluster(self):
		"""
		Test that the size of an empty cluster is 0.
		"""

		c = Cluster()
		self.assertEqual(0, c.size())

	def test_size(self):
		"""
		Test retrieving the size of a cluster.
		"""

		v = [
			Document("", [ 'a', 'b' ], scheme=TF()),
			Document("", [ 'a', 'a' ], scheme=TF()),
		]
		c = Cluster(v)
		self.assertEqual(len(v), c.size())

	def test_export(self):
		"""
		Test exporting and importing clusters.
		"""

		tf = TF()
		v = [
			Document("", ["a", "b", "a", "c"], scheme=TF()),
			Document("", ["a", "c"], scheme=TF()),
			Document("", ["b"], scheme=TF()),
		]
		c = Cluster(v)

		e = c.to_array()
		r = Cluster.from_array(e)

		for i, vector in enumerate(r.vectors):
			self.assertEqual(vector.__dict__, v[i].__dict__)
