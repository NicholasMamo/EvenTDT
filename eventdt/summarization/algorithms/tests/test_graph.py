"""
Run unit tests on the MMR implementation.
"""

import math
import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

from libraries.vector.cluster.cluster import Cluster

from libraries.vector.vector_math import cosine

from libraries.vector.nlp.document import Document
from libraries.vector.nlp.tokenizer import Tokenizer
from vector.nlp.term_weighting import TFIDF

from libraries.summarization.algorithms.update.mamo_graph import DocumentGraphSummarizer

class TestGraphSummarization(unittest.TestCase):
	"""
	Test the MMR implementation.
	"""

	def test_graph_summarization(self):
		"""
		Test the fragmented MMR implementation.
		"""

		tokenizer = Tokenizer(min_length=1)
		corpus = [] # the corpus of documents

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

		idf = { ("a" + key if not key == "DOCUMENTS" else key): value
			for key, value in idf.items() }

		posts = [
			"Manchester United falter against Tottenham Hotspur.",
			"Lucas Moura punishes Mourinho's men with a double.",
			"United unable to avoid defeat to Tottenham.",
			"Mourinho under immense pressure.",
			"Powerless Manchester United falter against Tottenham Hotspur.",
			"Jose Mourinho sacked tomorrow?",
			"Luke Shaw only bright spot in dim Manchester United.",
			"Lukaku with a glaring miss, and Mourinho in trouble.",
			"Lukaku and his miss keeps Manchester United in pain.",
			"Tottenham Hotspur star Lucas Moura pictured with Manchester United fans.",
			"Beginning of a crisis?"
		]

		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		cluster = Cluster(corpus)
		summarizer = DocumentGraphSummarizer(tokenizer=tokenizer, scheme=TFIDF(idf))
		breaking_terms = [
			("manchester", 1.), ("united", 1.), ("mourinho", 0.9), ("lukaku", 0.8),
			("lucas", 0.4), ("moura", 0.4), ("tottenham", 0.75), ("hotspur", 0.75) ]
		breaking_terms = [ (tokenizer.tokenize(term)[0], value) for term, value in breaking_terms ]
		summarizer.add_cluster(cluster, breaking_terms, 0)
		summary = summarizer.create_summary().generate_summary()

		self.assertTrue("Lukaku" in summary)
		self.assertTrue("Moura" in summary)
