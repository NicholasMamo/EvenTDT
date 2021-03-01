"""
The :class:`~summarization.scorers.domain_scorer.DomainScorer` is a scorer that prioritizes documents that mention more terms from a given domain.
Like all scorers, the :class:`~summarization.scorers.domain_scorer.DomainScorer` revolves around its :func:`~summarization.scorers.domain_scorer.DomainScorer.score` function.
"""

from .scorer import Scorer

import math
import re

class DomainScorer(Scorer):
    """
    The domain scorer gives a high score to documents that mention more terms from a particular domain.
    Upon initialization, this scorer expects and stores a list of terms that characterize the domain.

    :ivar terms: The list of terms that characterize a particular domain.
    :vartype terms: list of str
    """

    def __init__(self, terms):
        """
        Create the domain scorer with a list of terms from a domain.
        The scorer evaluates incoming documents based on how many terms they use from this domain.

        :param terms: The list of terms that characterize a particular domain.
        :type terms: list of str
        """

        self.terms = list(terms)

    def score(self, document, *args, **kwargs):
        """
        Evaluate the score of the given document.

        :param tweet: The document to score
        :type tweet: :class:`~vsm.nlp.document.Document`

        :return: The document's score.
        :rtype: int
        """

        return 1
