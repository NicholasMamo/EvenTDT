"""
Test the functionality of the ATE evaluation tool.
"""

import json
import os
import string
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..', '..'),
          os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from evaluation import ate

class TestATE(unittest.TestCase):
    """
    Test the functionality of the ATE evaluation tool.
    """
