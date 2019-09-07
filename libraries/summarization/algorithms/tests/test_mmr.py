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

from libraries.vector.vector_math import cosine

from libraries.vector.cluster.cluster import Cluster
from libraries.vector.nlp.document import Document
from libraries.vector.nlp.tokenizer import Tokenizer

from libraries.summarization.algorithms.mmr import MMR
from libraries.summarization.algorithms.update.mamo_mmr import FragmentedMMR

class TestMMR(unittest.TestCase):
	"""
	Test the MMR implementation.
	"""

	def test_mmr(self):
		"""
		Test the MMR implementation.
		Test based on the following worked example:
			http://www.cs.bilkent.edu.tr/~canf/CS533/hwSpring14/eightMinPresentations/handoutMMR.pdf
		"""

		similarity = [
			[1, 	0.11, 	0.23, 	0.76, 	0.25, 	0.91],
			[0.11, 	1, 		0.29, 	0.57, 	0.51, 	0.9],
			[0.23, 	0.29,	1, 		0.02, 	0.2, 	0.5],
			[0.76, 	0.57, 	0.02,	1,		0.33, 	0.06],
			[0.25,	0.51,	0.2,	0.33, 	1,		0.63],
			[0.91,	0.9,	0.5,	0.06,	0.63,	1]
		]

		collection = [
			Document(attributes={"text": "1"}, label="1"),
			Document(attributes={"text": 2}, label="2"),
			Document(attributes={"text": "3"}, label="3"),
			Document(attributes={"text": 4}, label="4"),
			Document(attributes={"text": "5"}, label="5"),
		]

		query = Document(label="Q")
		summary = MMR(collection, query, l=0.5, similarity_table=similarity)
		self.assertTrue(collection[0] in summary.get_documents())
		self.assertTrue(collection[1] in summary.get_documents())
		self.assertTrue(collection[2] in summary.get_documents())

		posts = [
			"Chelsea and Manchester United",
			"Manchester City and Arsenal",
			"Chelsea and Arsenal",
		]

		tokenizer = Tokenizer(min_length=1)
		corpus = []
		for post in posts:
			tokens = tokenizer.tokenize(post)
			document = Document(post, tokens, { "tokens": tokens })
			corpus.append(document)

		# print("Start")
		# summary = MMR(corpus)
		# print("End")
		# print(summary.generate_summary())

	def test_fragmented_mmr(self):
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
		summarizer = FragmentedMMR()
		breaking_terms = [
			("manchester", 1.), ("united", 1.), ("mourinho", 0.9), ("lukaku", 0.8),
			("lucas", 0.4), ("moura", 0.4), ("tottenham", 0.75), ("hotspur", 0.75) ]
		breaking_terms = [ (tokenizer.tokenize(term)[0], value) for term, value in breaking_terms ]
		summarizer.add_cluster(cluster, breaking_terms, 0)
		summary = summarizer.create_summary().generate_summary()

		self.assertTrue("Lukaku" in summary)
		self.assertTrue("Moura" in summary)
