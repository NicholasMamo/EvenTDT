"""
Test the functionality of external extrapolators.
"""

import os
import sys
import unittest
import warnings

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../../../')
if path not in sys.path:
	sys.path.append(path)

from nltk.corpus import stopwords

from libraries.apd.participant_detector import ParticipantDetector
from libraries.apd.extractors.local.entity_extractor import EntityExtractor
from libraries.apd.extrapolators.external.wikipedia_extrapolator import LinkExtrapolator, WikipediaExtrapolator
from libraries.apd.resolvers.external.wikipedia_resolver import WikipediaResolver
from libraries.apd.scorers.local.sum_scorer import SumScorer

from libraries.vector.nlp.document import Document
from libraries.vector.nlp.tokenizer import Tokenizer
from libraries.vector.nlp.term_weighting import TF, TFIDF

def ignore_warnings(test):
	"""
	A decorator function used to ignore NLTK warnings
	From: http://www.neuraldump.net/2017/06/how-to-suppress-python-unittest-warnings/
	More about decorator functions: https://wiki.python.org/moin/PythonDecorators

	:param test: The test to perform.
	:type test: func

	:return: The function output.
	:rtype: obj
	"""
	def perform_test(self, *args, **kwargs):
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			test(self, *args, **kwargs)
	return perform_test

class TestExtrapolators(unittest.TestCase):
	"""
	Test the implementation and results of the different extrapolators.
	"""

	@ignore_warnings
	def test_link_extrapolator(self):
		"""
		Test the link extrapolator.
		"""

		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)

		posts = [
			"Manchester United unable to avoid defeat to Tottenham",
			"Manchester United lost to Tottenham Hotspur",
			"Mourinho under pressure as Manchester United follow with a loss",
			"Manchester United powerless in loss to Tottenham",
			"Manchester United manager Jose Mourinho sacked tomorrow?",
			"Luke Shaw was the only bright spot in dim Manchester United",
			"Beginning of a crisis for Jose Mourinho's Manchester United?",
			"Match report: David De Gea powerless in loss",
			"Manchester United's Fred uninspiring in defeat",
			"Selfie this: Tottenham Hotspur star Lucas Moura pictured with Manchester United fans",
			"Pochettino hails Lucas Moura and Harry Kane",
			"Lucas Moura punishes United",
			"Mauricio Pochettino and Lucas Moura get one over United",
			"Tottenham win without Heung-Min Son",
			"Harry Kane and Christian Eriksen on point for Tottenham",
			"Davinson Sanchez on the bench for Tottenham",
			"Alderweireld and Vertonghen do the job in win over United",
		]

		idf = {
			"DOCUMENTS": 100,
			"crisis": 12,
			"bright": 10,
			"selfie": 5,
			"power": 8,
			"pressure": 5,
			"defeat": 8,
			"fall": 7,
			"falter": 2,
			"spot": 3,
			"dim": 7,
			"spur": 1,
			"against": 10,
			"tomorrow": 3,
			"sack": 2,
			"follow": 8,
		}

		posts = [
			"Looking at the offensive contribution of Tomas Plekanec with the Montreal Canadiens, and his most frequent collaborators.",
			"The imprint of the Kovalev/Plekanec/Kostitsyn line is evident as being to height of Plekanec's offensive output.",
			"Call of the Wilde: Montreal Canadiens’ Carey Price steals one in Calgary",
			"\"Phew, thank goodness that Tkachuk kid isn't in front of the net to tip pucks\" ~ The Montreal Canadiens, probably",
			"It surprised me when I heard his name called in Dallas, as the Montreal Canadiens selected Alexander Romanov in the 2nd round",
			"Canadiens recall Nikita Scherbak",
			"Can Max Domi be a Hart candidate for the Montreal Canadiens?",
		]

		idf = {
			"DOCUMENTS": 100,
			"contribut": 12,
			"frequent": 10,
			"imprint": 5,
			"evident": 8,
			"height": 5,
			"output": 8,
			"steal": 7,
			"call": 2,
			"steal": 3,
			"good": 7,
			"thank": 1,
			"kid": 10,
			"front": 3,
			"net": 2,
			"recall": 8,
		}

		print("%d posts" % len(posts))
		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		participant_detector = ParticipantDetector(corpus, EntityExtractor, SumScorer, WikipediaResolver, LinkExtrapolator)
		resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.1,
			resolver_scheme=TFIDF(idf), resolver_threshold=0.1,
			extrapolator_scheme=TFIDF(idf), extrapolator_participants=30, extrapolator_threshold=0)

		print(resolved)
		print(extrapolated)

	@ignore_warnings
	def no_test_wikipedia_extrapolator(self):
		"""
		Test the Wikipedia extrapolator.
		"""

		# TODO: Complete test

		tokenizer = Tokenizer()

		posts = [
			"Alexis Sanchez mute in Manchester United defeat to Tottenham",
			"Manchester United made to rue Lukaku's miss",
			"Manchester United lost to Tottenham Hotspur",
			"Jose Mourinho under pressure as Manchester United follow with a loss",
			"Manchester United powerless in loss to Tottenham",
			"Manchester United manager Jose Mourinho sacked tomorrow?",
			"Luke Shaw was the only bright spot in dim Manchester United",
			"Beginning of a crisis for Jose Mourinho's Manchester United?",
			"Match report: David De Gea powerless in loss against Tottenham",
			"Manchester United's Fred uninspiring in defeat to Tottenham",
			"Selfie this: Tottenham Hotspur star Lucas Moura pictured with Manchester United fans",
			"Tottenham's Pochettino hails Lucas Moura and Harry Kane",
			"Lucas Moura and Tottenham Hotspur punish United",
			"Mauricio Pochettino and Lucas Moura get one over United",
			"Tottenham Hotspur win without Heung-Min Son",
			"Harry Kane and Christian Eriksen on point for Tottenham",
			"Davinson Sanchez on the bench for Tottenham",
			"Alderweireld and Vertonghen do the job in win over United",
		]

		idf = {
			"DOCUMENTS": 100,
			"crisis": 12,
			"bright": 10,
			"selfie": 5,
			"power": 8,
			"pressure": 5,
			"defeat": 8,
			"fall": 7,
			"falter": 2,
			"spot": 3,
			"dim": 7,
			"spur": 1,
			"against": 10,
			"tomorrow": 3,
			"sack": 2,
			"follow": 8,
		}

		corpus = [] # the corpus of documents
		for post in posts:
			tokens = tokenizer.tokenize(post, case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		participant_detector = ParticipantDetector(corpus, EntityExtractor, SumScorer, WikipediaResolver, WikipediaExtrapolator)
		resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.1,
			resolver_scheme=TFIDF(idf), resolver_threshold=0.1,
			extrapolator_scheme=TFIDF(idf), extrapolator_participants=30, extrapolator_threshold=0)

		self.assertEqual(set(resolved), set(['Match', 'David De Gea', 'Tottenham Hotspur', 'Manchester United', 'Alderweireld', 'Selfie', 'Pochettino', 'Luke Shaw', 'Harry Kane', 'Lucas Moura', 'Sanchez', 'Jose Mourinho', 'Christian Eriksen']))
		self.assertEqual(set(unresolved), set(['Mauricio', 'Davinson']))
		self.assertTrue("Anthony Martial" in extrapolated)
