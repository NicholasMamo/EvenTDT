import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../'))

from vector.nlp.document import Document
from vector.cluster.algorithms.nokmeans import NoKMeans

algo = NoKMeans()

v = [
	Document("", ["a", "b", "a", "c"]),
	Document("", ["b"]),
	Document("", ["a", "c"]),
]

algo.cluster(v, threshold=0.5, freeze_period=10)
clusters = algo.get_clusters()
for i, cluster in enumerate(clusters):
	print(i)
	for vector in cluster.get_vectors():
		print("\t", vector.get_dimensions())
