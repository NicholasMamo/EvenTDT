"""
Test the functionality of the package functions.
"""

import json
import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from modeling import *

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the package functions.
    """

    pass
