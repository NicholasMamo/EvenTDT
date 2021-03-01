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

    def test_score_empty_document(self):
        """
        Test that the score of an empty document is 0.
        """

        terms = { 'baller', 'keeper', 'offsid', 'ff', 'equalis', 'gol', 'goalkeep', 'var', 'foul', 'goal' }
        scorer = DomainScorer(terms)

        # create the document
        text = ''
        tokenizer = Tokenizer(stem=True)
        tokens = tokenizer.tokenize(text)
        document = Document(text, dimensions=tokens)

        self.assertEqual(0, scorer.score(document))

    def test_score_exact_matches(self):
        """
        Test that the scorer only counts exact matches, which means that 'offside' does not match 'offsid'.
        """

        terms = { 'baller', 'keeper', 'offsid', 'ff', 'equalis', 'gol', 'goalkeep', 'var', 'foul', 'goal' }
        scorer = DomainScorer(terms)

        # create the document
        text = 'Goal! But the referee chalks it off for offside.'
        tokenizer = Tokenizer(stem=False)
        tokens = tokenizer.tokenize(text)
        document = Document(text, dimensions=tokens)
        self.assertTrue('goal' in document.dimensions)
        self.assertTrue('offside' in document.dimensions)

        self.assertEqual(1, scorer.score(document))

    def test_score_dimensions(self):
        """
        Test that when scoring documents, it is only the dimensions that are considered.
        """

        terms = { 'baller', 'keeper', 'offsid', 'ff', 'equalis', 'gol', 'goalkeep', 'var', 'foul', 'goal' }
        scorer = DomainScorer(terms)

        # create the document with no text, but with tokens
        text = 'Goal! But the referee chalks it off for offside.'
        tokenizer = Tokenizer(stem=True)
        tokens = tokenizer.tokenize(text)
        document = Document('', dimensions=tokens)
        self.assertEqual(2, scorer.score(document))

        # create the same document again, but this time with text, but no dimensions
        document = Document(text)
        self.assertEqual(0, scorer.score(document))

    def test_score_unique_only(self):
        """
        Test that when a term appears multiple times, it is only counted once by the domain scorer.
        """

        terms = { 'baller', 'keeper', 'offsid', 'ff', 'equalis', 'gol', 'goalkeep', 'var', 'foul', 'goal' }
        scorer = DomainScorer(terms)

        # create the document
        text = 'Goal! And what a goal, my word!'
        tokenizer = Tokenizer(stem=True)
        tokens = tokenizer.tokenize(text)
        document = Document(text, dimensions=tokens)

        self.assertTrue('goal' in document.dimensions)
        self.assertEqual(2, document.dimensions['goal'])
        self.assertEqual(1, scorer.score(document))
