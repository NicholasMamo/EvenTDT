"""
Run unit tests on the document node.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from summarization.timeline.nodes import DocumentNode

class TestDocumentNode(unittest.TestCase):
	"""
	Test the document node.
	"""
