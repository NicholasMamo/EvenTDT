"""
Test the functionality of the terms tool.
"""

import json
import os
import re
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

from tools import terms
from ate.application import EFIDF

class TestTerms(unittest.TestCase):
	"""
	Test the functionality of the terms tool.
	"""

	def test_instantiate_efidf_missing_idf(self):
		"""
		Test that when the TF-IDF scheme is not given for the EF-IDF, a SystemExit is raised.
		"""

		self.assertRaises(SystemExit, terms.instantiate, EFIDF)
