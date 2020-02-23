"""
Test the different scorers' functionality.
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

from libraries.vector.nlp.cleaners.tweet_cleaner import TweetCleaner
from libraries.summarization.scorers.scorer import Scorer
from libraries.summarization.scorers.tweet_scorer import TweetScorer

from libraries.vector.nlp.document import Document
from libraries.vector.nlp.tokenizer import Tokenizer

class TestScorers(unittest.TestCase):
	"""
	Test the implementation and results of the different scorers.
	"""

	def test_scorer(self):
		"""
		Test the most basic scorer.
		"""

		scorer = Scorer()
		self.assertEqual(scorer.score(Document()), 1)

	def test_tweet_scorer(self):
		"""
		Test :class:`~summarization.cleaner.tweet_scorer.TweetScorer`
		"""

		scorer = TweetScorer()
		cleaner = TweetCleaner()
		tokenizer = Tokenizer(min_length=1)

		tweet = "RT @KriiCamilleri92: #SouthKorea win the U23 Asian Games final! Which means #HeungMinSon will only have to serve 4 weeks in the military! So happy for the lad :D"
		clean_tweet = cleaner.clean(tweet)
		tokens = tokenizer.tokenize(clean_tweet)
		document = Document(tweet, tokens, { "tokens": tokens })

		self.assertTrue(scorer._brevity_score(tokens, 10) == 1)
		self.assertTrue(scorer._brevity_score(tokens, 28) == 1)
		self.assertTrue(scorer._brevity_score(tokens, 29) < 1)
