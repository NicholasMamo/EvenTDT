"""
Test the functionality of the tokenizer tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
 		  os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
	if path not in sys.path:
	    sys.path.append(path)

import tokenizer as tool
from eventdt.nlp.tokenizer import Tokenizer

class TestTokenizer(unittest.TestCase):
	"""
	Test the functionality of the Tokenizer tool.
	"""

	def test_prepare_output_dir(self):
		"""
		Test that if the output directory does not exist, the tool creates it.
		"""

		path = 'tools/tests/.out/tokenized.json'
		dir = os.path.dirname(path)

		"""
		Remove the directory.
		Also remove any files in the directory.
		"""
		if os.path.exists(dir):
			with os.scandir(dir) as files:
				for file in files:
					os.remove(file)
			os.rmdir(dir)

		tool.prepare_output(path)
		self.assertTrue(os.path.exists(dir))
		os.rmdir(dir)

	def test_get_text_full(self):
		"""
		Test that when getting the text from tweets, the full text is returned.
		"""

		with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
			for line in f:
				tweet = json.loads(line)
				if '…' in tweet['text']:
					text = tool.get_text(tweet)

					"""
					Make an exception for a special case.
					"""
					if not ('retweeted_status' in tweet and tweet['retweeted_status']['id_str'] == '1238513167573147648'):
						self.assertFalse(text.endswith('…'))

	def test_tokenize_corpus_same_lines(self):
		"""
		Test that when tokenizing a corpus, the same number of lines are outputted.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Count the number of lines in the corpus.
		"""
		inlines = 0
		with open(file, 'r') as infile:
			for line in infile:
				inlines += 1

		"""
		Tokenize the corpus and again count the number of lines in the tokenized corpus.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer())
		outlines = 0
		with open(output, 'r') as outfile:
			for line in outfile:
				outlines += 1

		self.assertEqual(inlines, outlines)

	def test_tokenize_corpus_same_order(self):
		"""
		Test that when tokenizing a corpus, the tweets are saved in the correct order.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Collect the IDs in the input file.
		"""
		inids = [ ]
		with open(file, 'r') as infile:
			for line in infile:
				inids.append(json.loads(line)['id'])

		"""
		Tokenize the corpus and again collect the lines in the tokenized corpus.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer())
		outids = [ ]
		with open(output, 'r') as outfile:
			for line in outfile:
				outids.append(json.loads(line)['id'])

		self.assertEqual(inids, outids)

	def test_tokenize_corpus_id(self):
		"""
		Test that when tokenizing a corpus, the ID is saved alongside each tweet.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and ensure that the ID is present in all tweets.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer())
		with open(output, 'r') as outfile:
			for line in outfile:
				self.assertTrue('id' in json.loads(line))

	def test_tokenize_corpus_text(self):
		"""
		Test that when tokenizing a corpus, the text is saved alongside each tweet.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and ensure that the ID is present in all tweets.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer())
		with open(output, 'r') as outfile:
			for line in outfile:
				self.assertTrue('text' in json.loads(line))
