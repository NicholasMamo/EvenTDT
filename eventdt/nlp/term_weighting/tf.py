"""
The TF scheme is used when there is no need for a global scheme.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.append(path)

from scheme import TermWeightingScheme
from local_schemes import tf
from global_schemes.filler import Filler

class TF(TermWeightingScheme):
	"""
	The TF scheme is used when there is no need for a global scheme.
	"""

	def __init__(self):
		"""
		Initialize the TF-IDF term-weighting scheme by supplying the TF and filler schemes.
		"""

		super(TF, self).__init__(tf.TF(), Filler())
