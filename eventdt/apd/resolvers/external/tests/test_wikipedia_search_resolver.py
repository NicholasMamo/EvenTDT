"""
Test the functionality of the Wikipedia search resolver.
"""

import os
import random
import re
import string
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nltk.corpus import stopwords

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.scorers.local.tf_scorer import TFScorer
from apd.filters.local.threshold_filter import ThresholdFilter
from apd.resolvers.external.wikipedia_search_resolver import WikipediaSearchResolver

from nlp.document import Document
from nlp.tokenizer import Tokenizer
from nlp.weighting.tf import TF

class TestWikipediaSearchResolver(unittest.TestCase):
    """
    Test the implementation and results of the Wikipedia search resolver.
    """

    def no_test_year_check(self):
        """
        Test that when checking for a year, the function returns a boolean.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        article = 'Youssouf Koné (footballer, born 1995)'
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertTrue(resolver._has_year(article))

    def no_test_year_check_range(self):
        """
        Test that when checking for a year in a range, the function returns `True`.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        article = '2019–20 Premier League'
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertTrue(resolver._has_year(article))

        article = '2019-20 Premier League'
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertTrue(resolver._has_year(article))

    def no_test_year_check_short_number(self):
        """
        Test that when checking for a year with a short number, the function does not detect a year.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        article = 'Area 51'
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertFalse(resolver._has_year(article))

    def no_test_year_check_long_number(self):
        """
        Test that when checking for a year with a long number, the function does not detect a year.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        article = '1234567890'
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertFalse(resolver._has_year(article))

    def no_test_remove_brackets(self):
        """
        Test that when removing brackets, they are completely removed.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        article = 'Youssouf Koné (footballer, born 1995)'
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertEqual('Youssouf Koné', resolver._remove_brackets(article).strip())

    def no_test_remove_unclosed_brackets(self):
        """
        Test that when removing brackets that are not closed, they are not removed.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        article = 'Youssouf Koné (footballer, born 1995'
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertEqual('Youssouf Koné (footballer, born 1995', resolver._remove_brackets(article).strip())

    def no_test_get_first_sentence(self):
        """
        Test that when getting the first sentence from text, only the first sentence is returned.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        text = "Memphis Depay (Dutch pronunciation: [ˈmɛmfɪs dəˈpɑi]; born 13 February 1994), \
                commonly known simply as Memphis,[2] is a Dutch professional \
                footballer and music artist who plays as a forward and captains \
                French club Lyon and plays for the Netherlands national team. \
                He is known for his pace, ability to cut inside, dribbling, \
                distance shooting and ability to play the ball off the ground."

        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertEqual("Memphis Depay (Dutch pronunciation: [ˈmɛmfɪs dəˈpɑi]; born 13 February 1994), commonly known simply as Memphis,[2] is a Dutch professional footballer and music artist who plays as a forward and captains French club Lyon and plays for the Netherlands national team.",
                         re.sub('([ \t]+)', ' ', resolver._get_first_sentence(text)).strip())

    def no_test_get_first_sentence_full(self):
        """
        Test that when getting the first sentence from a text that has only one sentence, the whole text is returned.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        text = "Youssouf Koné (born 5 July 1995) is a Malian professional footballer who plays for French side Olympique Lyonnais and the Mali national team as a left-back."
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertEqual(text, resolver._get_first_sentence(text))

    def no_test_get_first_sentence_full_without_period(self):
        """
        Test that when getting the first sentence from a text that has only one sentence, but without punctuation, the whole text is returned.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        text = "Youssouf Koné (born 5 July 1995) is a Malian professional footballer who plays for French side Olympique Lyonnais and the Mali national team as a left-back"
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertEqual(text, resolver._get_first_sentence(text))

    def no_test_get_first_sentence_empty(self):
        """
        Test that when getting the first sentence from an empty string, an empty string is returned.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        text = ""
        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        self.assertEqual(text, resolver._get_first_sentence(text))

    def no_test_score_upper_bound(self):
        """
        Test that the score has an upper bound of 1.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        tokenizer = Tokenizer(min_length=2, stem=True)
        candidate = "Cristiano Ronaldo"
        candidate_document = Document(candidate, tokenizer.tokenize(candidate))
        title_document = Document(candidate, tokenizer.tokenize(candidate))

        text = "Cristiano Ronaldo is a Portuguese professional footballer who plays as a forward for Serie A club Juventus and captains the Portugal national team."
        domain = Document(text, tokenizer.tokenize(text))
        sentence = Document(text, tokenizer.tokenize(text))

        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        resolver.domain = domain
        self.assertEqual(1, round(resolver._compute_score(candidate_document, title_document, sentence), 5))

    def no_test_score_lower_bound(self):
        """
        Test that the score has a lower bound of 0.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        tokenizer = Tokenizer(min_length=2, stem=True)
        candidate = "Cristiano Ronaldo"
        candidate_document = Document(candidate, tokenizer.tokenize(candidate))
        text = "Cristiano Ronaldo is a Portuguese professional footballer who plays as a forward for Serie A club Juventus and captains the Portugal national team."

        title_document = Document(candidate, [ ])
        sentence = Document(text, [ ])
        domain = Document(text, tokenizer.tokenize(text))

        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        resolver.domain = domain
        self.assertEqual(0, round(resolver._compute_score(candidate_document, title_document, sentence), 5))

    def no_test_score_relevance(self):
        """
        Test that when two documents are provided, one more relevant than the other, the score reflects it.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'empty.json')
        tokenizer = Tokenizer(min_length=2, stem=True)
        candidate = "Ronaldo"
        candidate_document = Document(candidate, tokenizer.tokenize(candidate))
        text = "Ronaldo, speaking after Juventus' victory, says Serie A is still wide open"
        domain = Document(text, tokenizer.tokenize(text))

        title_1 = "Cristiano Ronaldo"
        text_1 = "Cristiano Ronaldo is a Portuguese professional footballer who plays as a forward for Serie A club Juventus."
        title_document_1 = Document(title_1, tokenizer.tokenize(title_1))
        sentence_document_1 = Document(text_1, tokenizer.tokenize(text_1))

        title_2 = "Ronaldo"
        text_2 = "Ronaldo is a Brazilian former professional footballer who played as a striker."
        title_document_2 = Document(title_2, tokenizer.tokenize(title_2))
        sentence_document_2 = Document(text_2, tokenizer.tokenize(text_2))

        resolver = WikipediaSearchResolver(TF(), Tokenizer(), 0, path)
        resolver.domain = domain
        score_1 = resolver._compute_score(candidate_document, title_document_1, sentence_document_1)
        score_2 = resolver._compute_score(candidate_document, title_document_2, sentence_document_2)
        self.assertGreater(score_1, score_2)

    def no_test_wikipedia_name_resolver(self):
        """
        Test the Wikipedia search resolver.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=2, stem=True, stopwords=list(stopwords.words("english")))
        resolver = WikipediaSearchResolver(TF(), tokenizer, 0, path)
        resolved, unresolved = resolver.resolve({ 'Chelsea': 1, 'Sarri': 0.5 })
        self.assertTrue('Chelsea F.C.' in resolved)
        self.assertTrue('Maurizio Sarri' in resolved)

    def no_test_all_resolved_or_unresolved(self):
        """
        Test that the resolver either resolves or does not resolve named entities.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=2, stem=True, stopwords=list(stopwords.words("english")))
        resolver = WikipediaSearchResolver(TF(), tokenizer, 0.05, path)
        scores = { 'Chelsea': 1, 'Sarri': 0.5, 'Callum': 0.25, 'Eden': 0.1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertEqual(len(scores), len(resolved) + len(unresolved))
        self.assertEqual([ 'Callum Hudson-Odoi' ], resolved)
        self.assertEqual([ 'Chelsea', 'Sarri', 'Eden' ], unresolved)

    def no_test_random_string_unresolved(self):
        """
        Test that a random string is unresolved.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False)
        resolver = WikipediaSearchResolver(TF(), tokenizer, 0, path)
        random_string = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(32))
        scores = { random_string: 1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertTrue(random_string in unresolved)

    def no_test_zero_threshold(self):
        """
        Test that when the threshold is zero, it excludes no candidates.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=2, stem=True, stopwords=list(stopwords.words("english")))
        resolver = WikipediaSearchResolver(TF(), tokenizer, 0, path)
        scores = { 'Chelsea': 1, 'Sarri': 0.5, 'Callum': 0.25, 'Eden': 0.1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertEqual(4, len(resolved))
        self.assertFalse(unresolved)

    def no_test_threshold(self):
        """
        Test that when the threshold is not zero, it excludes some candidates.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=2, stem=True, stopwords=list(stopwords.words("english")))
        resolver = WikipediaSearchResolver(TF(), tokenizer, 0.05, path)
        scores = { 'Chelsea': 1, 'Sarri': 0.5, 'Callum': 0.25, 'Eden': 0.1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertEqual(len(scores), len(resolved) + len(unresolved))
        self.assertEqual([ 'Chelsea', 'Sarri', 'Eden' ], unresolved)

    def no_test_high_threshold(self):
        """
        Test that when the threshold is high, it excludes all candidates.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=2, stem=True, stopwords=list(stopwords.words("english")))
        resolver = WikipediaSearchResolver(TF(), tokenizer, 1, path)
        scores = { 'Chelsea': 1, 'Sarri': 0.5, 'Callum': 0.25, 'Eden': 0.1 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertFalse(resolved)
        self.assertEqual(4, len(unresolved))

    def no_test_resolve_empty(self):
        """
        Test that when resolving an empty set of candidates, the resolver returns empty lists.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=2, stem=True, stopwords=list(stopwords.words("english")))
        resolver = WikipediaSearchResolver(TF(), tokenizer, 0, path)
        resolved, unresolved = resolver.resolve({scores})
        self.assertFalse(resolved)
        self.assertFalse(unresolved)

    def test_resolve_no_duplicates(self):
        """
        Test that resolution does not include duplicates.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=2, stem=True, stopwords=list(stopwords.words("english")))
        resolver = WikipediaSearchResolver(TF(), tokenizer, 0, path)
        scores = { 'Chelsea': 1, 'Chelsea F.C.': 0.5 }
        resolved, unresolved = resolver.resolve(scores)
        self.assertEqual(1, len(resolved))
        self.assertEqual([ 'Chelsea F.C.' ], resolved)
        self.assertFalse(unresolved)

    def no_test_sorting(self):
        """
        Test that the resolver sorts the named entities in descending order of score.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..',  '..', '..', 'tests', 'corpora', 'CRYCHE-100.json')
        tokenizer = Tokenizer(min_length=1, stem=False, stopwords=list(stopwords.words("english")))
        resolver = WikipediaSearchResolver(TF(), tokenizer, 0, path)
        scores = { 'Chelsea F.C.': 1, 'Maurizio Sarri': 0.5, 'Callum Hudson-Odoi': 0.1, 'Eden Hazard': 0.25 }
        resolved, unresolved = resolver.resolve(scores)

        order = sorted(scores, key=scores.get, reverse=True)
        self.assertEqual(order, resolved)
