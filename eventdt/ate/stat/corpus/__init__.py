"""
Corpus comparison ATE approaches extract domain terms by comparing term incidence in domain corpora with their incidence in general domains.
This package provides a new extractor meant especially for corpus comparison approaches.
Since all corpus comparison approaches require one or more general corpora, they can be provided in the constructor.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from extractor import Extractor

class ComparisonExtractor(Extractor):
    """
    The corpus comparison extractor stores the general corpora as a class variable.
    All domain comparisons use these general corpora to extract terms.

    :ivar general: A list of paths to general corpora, to be used for comparison.
                   Corpus comparison approaches expect the corpora to be tokenized.
    :vartype general: list of str
    """

    def __init__(self, general):
        """
        Create the corpus comparison extractor with the general corpora.

        :param general: A path or a list of paths to general corpora, to be used for comparison.
                        Corpus comparison approaches expect the corpora to be tokenized.
        :type general: str or list of str
        """

        super().__init__()
        self.general = self.to_list(general)

class DummyComparisonExtractor(ComparisonExtractor):
    """
    A dummy comparison extractor that does nothing and returns an empty list of terms.
    It is used only for testing purposes.
    """

    def extract(self, corpora, candidates=None):
        """
        Return an empty list of terms.

        :param corpora: A path to a corpus or a list of paths to corpora where to look for terms.
        :type corpora: str or list of str
        :param candidates: A list of terms which may be extracted.
                     This is useful when calculating scores takes a long time and the list of candidate terms are known in advance.
                     If ``None`` is given, all words are considered to be candidates.
        :type candidates: None or list of str

        :return: An empty list of terms.
        :rtype: dict
        """

        return { }

from .tfdcf import TFDCFExtractor
from .rank import RankExtractor
from .specificity import SpecificityExtractor
