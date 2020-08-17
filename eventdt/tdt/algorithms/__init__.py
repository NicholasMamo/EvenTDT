"""
TDT algorithms are split broadly into document-pivot and feature-pivot techniques:

- Document-pivot approaches use clustering to identify `what` is being discussed (read more `here <https://nyphoon.com/2020/07/27/document-pivot-methods-whats-happening/>`_), and
- Feature-pivot approaches identify `how` people are talking (read more `here <https://nyphoon.com/2020/08/06/feature-pivot-methods-did-something-happen/>`_).

Since TDT approaches are so broad by nature, it is difficult to find a general pattern.
However, all algorithms must have a mechanism to detect topics from a specific type input.
This functionality is encapsulated in the :class:`~tdt.algorithms.TDTAlgorithm`, which specifies only a :func:`~tdt.algorithms.TDTAlgorithm.detect` method.
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
