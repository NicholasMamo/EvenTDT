"""
Test the functionality of the model tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import model

logger.set_logging_level(logger.LogLevel.WARNING)

class TestModel(unittest.TestCase):
    """
    Test the functionality of the model tool.
    """