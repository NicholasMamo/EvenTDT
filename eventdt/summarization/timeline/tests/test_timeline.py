"""
Run unit tests on the timeline.
"""

import math
import os
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from summarization.timeline import Timeline

class TestTimeline(unittest.TestCase):
	"""
	Test the timeline.
	"""

	def test_create_empty_timeline(self):
		"""
		Test that when creating an empty timeline, the list of nodes is empty.
		"""

		self.assertEqual([ ], Timeline().nodes)
