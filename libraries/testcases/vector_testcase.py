import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../'))

from vector.nlp.document import Document
from vector.cluster.cluster import Cluster
from vector.cluster.algorithms.nokmeans import NoKMeans

c = Cluster()

v = [
	Document("", {"a": 100, "b": 50}),
	Document("", {"a": 0.5, "b": 1}),
]

c.add_vectors(v)
c.get_centroid().normalize()
print(c.get_centroid().get_dimensions())

d = Cluster()
v[0].normalize()
v[1].normalize()

d.add_vectors(v)
q = d.get_centroid().normalize()
print(d.get_centroid().get_dimensions())
