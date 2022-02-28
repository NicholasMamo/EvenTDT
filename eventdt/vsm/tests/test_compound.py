"""
Run unit tests on the Compound class.
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '..')
if path not in sys.path:
    sys.path.append(path)

from compound import Compound

class TestCompound(unittest.TestCase):
    """
    Test the Compound class.
    """

    
