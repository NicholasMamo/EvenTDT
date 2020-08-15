"""
The term frequency term-weighting scheme is used when there is no need for a global scheme.
The term frequency :math:`tf_{t,d}` of a feature :math:`t` is equivalent to its frequency :math:`f_{t,d}` in document :math:`d`:

.. math::

	tf_{t,d} = f_{t,d}
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from term_weighting import TermWeightingScheme
from term_weighting.local_schemes import tf
from term_weighting.global_schemes.filler import Filler

class TF(TermWeightingScheme):
	"""
	The TF scheme is used when there is no need for a global scheme.
	"""

	def __init__(self):
		"""
		Initialize the TF-IDF term-weighting scheme by supplying the TF and filler schemes.
		"""

		super(TF, self).__init__(tf.TF(), Filler())
