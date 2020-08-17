"""
TDT algorithms are split broadly into document-pivot and feature-pivot.
The former use clustering algorithms to identify _what_ is being discussed as topics.
The latter identify topics based on _how_ discussion changes.

TDT approaches are broad by nature, but all algorithms must have a mechanism to detect topics from an input.
This functionality is encapsulated in the :func:`~tdt.algorithms.tdt.TDTAlgorithm.detect` method.
"""

from abc import ABC, abstractmethod

class TDTAlgorithm(ABC):
	"""
	Since TDT algorithms vary greatly, there is no general functionality or state.
	All algorithms must, however, implement the :func:`~tdt.algorithms.tdt.TDTAlgorithm.detect` method.
	"""

	@abstractmethod
	def detect(self, *args, **kwargs):
		"""
		Detect breaking topics.
		The parameters accepted by this function as well as the return value change according to the algorithm.
		"""

		pass

from .cataldi import Cataldi
from .eld import ELD
from .zhao import Zhao
