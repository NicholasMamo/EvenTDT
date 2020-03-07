"""
Run unit tests on Mamo et al. (2019)'s ELD algorithm.
"""

import math
import os
import random
import string
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from algorithms import ELD
from nutrition.memory import MemoryNutritionStore
class TestELD(unittest.TestCase):
	"""
	Test Mamo et al. (2019)'s ELD algorithm.
	"""
