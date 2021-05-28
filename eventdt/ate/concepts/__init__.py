"""
Lexical concepts are clusters of terms extracted using :mod:`~ate`.
By grouping terms together, word clustering gives terms better concepts.
For example, by grouping *yellow* and *card* together, the new concept is a clearer, less ambiguous reference to a football domain concept.
"""

from abc import ABC, abstractmethod

class TermClusteringAlgorithm(ABC):
    """
    The term cluster algorithm is an algorithm to group together terms.

    The goal of the class is not to calculate the similarity between terms, but to group terms together based on similarities.
    Therefore by default, the :class:`~ate.concepts.TermClusteringAlgorithm` class expects terms similarities.
    It is also far more efficient to calculate term similarities (using any algorithm in the :mod:`~ate.bootstrapping` module) and re-using them when creating lexical concepts.
    Derived classes may, however, override this requirement if they have specific process to calculate the similarity between terms.

    The :class:`~ate.concepts.TermClusteringAlgorithm` loads the term similarities from a file created by the :mod:`~tools.correlation` tool and stores them in its state.

    :ivar ~.similarity: The correlation between all given terms.
                        This is returned as a dictionary of dictionaries.
                        The outer level is each term.
                        The inner level is the outer level term's correlation with the other terms.
    :vartype ~.similarity: dict of dict
    """

    def __init__(self, file):
        """
        Initialize the term clustering algorithm by loading the term similarities from file.

        :param file: The open file wrapper.
                     This function loads the term similarities from this file.
        :class file: :class:`_io.TextIOWrapper`
        """

        self.similarity = { }

    @abstractmethod
    def cluster(self, *args, **kwargs):
        """
        Create lexical concepts by clustering the terms.
        This function returns sets of terms.

        :return: A group of term clusters.
        :rtype: set of set
        """

        pass

class DummyTermClusteringAlgorithm(TermClusteringAlgorithm):
    """
    A dummy test clustering algorithm that returns trivial clusters.
    This algorithm should only be used for testing purposes.
    """

    def cluster(self):
        """
        Create lexical concepts by clustering the terms.
        This function returns sets of terms.

        :return: A group of term clusters.
        :rtype: set of set
        """

        return set( )
