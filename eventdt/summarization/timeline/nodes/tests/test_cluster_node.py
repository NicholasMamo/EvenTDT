"""
Run unit tests on the cluster node.
"""

import math
import os
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from summarization.timeline.nodes import ClusterNode

class TestClusterNode(unittest.TestCase):
	"""
	Test the cluster node.
	"""
