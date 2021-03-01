"""
Test the :class:`~summarization.scorers.domain_scorer.DomainScorer`'s functionality.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from eventdt.summarization.scorers import DomainScorer

from eventdt.nlp.document import Document
from eventdt.nlp.tokenizer import Tokenizer

class TestDomainScorer(unittest.TestCase):
    """
    Test the implementation of the :class:`~summarization.scorers.domain_scorer.DomainScorer`.
    """

    def test_init_list_terms(self):
        """
        Test that when creating the domain scorer with a list of terms, they are saved as such.
        """

        terms = [ 'baller', 'keeper', 'offsid', 'ff', 'equalis', 'gol', 'goalkeep', 'var', 'foul', 'goal' ]
        scorer = DomainScorer(terms)
        self.assertEqual(terms, scorer.terms)

    def test_init_list_terms_copy(self):
        """
        Test that when creating the domain scorer with a list of terms, a copy is actually saved.
        """

        terms = [ 'baller', 'keeper', 'offsid', 'ff', 'equalis', 'gol', 'goalkeep', 'var', 'foul', 'goal' ]
        scorer = DomainScorer(terms)
        self.assertEqual(terms, scorer.terms)

        term = 'card'
        terms.append(term)
        self.assertTrue(term in terms)
        self.assertFalse(term in scorer.terms)

    def test_init_set_terms(self):
        """
        Test that when creating the domain scorer with a set of terms, they are saved as a list, even if the order changes.
        """

        terms = { 'baller', 'keeper', 'offsid', 'ff', 'equalis', 'gol', 'goalkeep', 'var', 'foul', 'goal' }
        scorer = DomainScorer(terms)
        self.assertEqual(set(terms), set(scorer.terms))
        self.assertEqual(list, type(scorer.terms))
