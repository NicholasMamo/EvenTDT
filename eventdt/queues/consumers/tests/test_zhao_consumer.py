"""
Test the functionality of the Zhao et al. consumer.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from consumers import ZhaoConsumer

class TestZhaoConsumer(unittest.TestCase):
	"""
	Test the implementation of the Zhao et al. consumer.
	"""
