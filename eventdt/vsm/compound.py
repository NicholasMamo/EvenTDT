"""
The :class:`~vsm.compound.Compound` class is an extension of the :class:`~vsm.vector.Vector`.
The class represents a group of vectors, not unlike a :class:`~vsm.clustering.cluster.Cluster`.
Differently from a :class:`~vsm.clustering.cluster.Cluster`, however, the :class:`~vsm.compound.Compound` class does not store all the documents.
Instead, it only stores the accumulation of the documents and the number of documents inside of it.
"""
