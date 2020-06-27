"""
Statistical approaches perform little linguistic processing.
These ATE algorithms range from simple metrics to more complex scoring mechanisms that rank tokens.
Although statistical approaches are not hybrid, many of them may be combined with linguistic approaches.
For example, statistical ATE algorithms often assume that only nouns can be terms.
"""

from .tf import TFExtractor
from .tfidf import TFIDFExtractor
