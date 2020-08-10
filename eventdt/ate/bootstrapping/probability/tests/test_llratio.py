"""
Test the functionality of the log-likelihood ratio bootstrapper.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate
from ate.bootstrapping.probability import LogLikelihoodRatioBootstrapper
from ate.stat import probability

class TestLogLikelihoodRatioBootstrapper(unittest.TestCase):
	"""
	Test the functionality of the log-likelihood ratio bootstrapper.
	"""

	
