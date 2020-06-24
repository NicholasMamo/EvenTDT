"""
Test the functionality of the tokenizer tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime
from nltk.corpus import stopwords

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

	def test_tokenize_corpus_no_keep(self):
		"""
		Test that when specifying no attribute to keep, the only attributes kept are the tweet ID, text and tokens.
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
				self.assertEqual({ 'id', 'text', 'tokens' }, set(json.loads(line)))

	def test_tokenize_corpus_keep(self):
		"""
		Test that when specifying attributes to keep, they are always stored.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and ensure that the ID is present in all tweets.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer(), keep=[ 'timestamp_ms' ])
		with open(output, 'r') as outfile:
			for line in outfile:
				self.assertEqual({ 'id', 'text', 'tokens', 'timestamp_ms' }, set(json.loads(line)))

	def test_tokenize_corpus_keep_occasional(self):
		"""
		Test that when specifying attributes to keep, an attribute that appears occasionally is still stored, but as `None`, when not found.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and ensure that the ID is present in all tweets.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer(), keep=[ 'retweeted_status' ])
		with open(output, 'r') as outfile:
			for line in outfile:
				self.assertEqual({ 'id', 'text', 'tokens', 'retweeted_status' }, set(json.loads(line)))

	def test_tokenize_corpus_keep_multiple(self):
		"""
		Test that when specifying multiple attributes to keep, they are always stored.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and ensure that the ID is present in all tweets.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer(), keep=[ 'timestamp_ms', 'id_str' ])
		with open(output, 'r') as outfile:
			for line in outfile:
				self.assertEqual({ 'id', 'text', 'tokens', 'timestamp_ms', 'id_str' }, set(json.loads(line)))

	def test_tokenize_corpus_keep_retweets(self):
		"""
		Test that when keeping retweets, the number of lines remains the same.
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
		tool.tokenize_corpus(file, output, Tokenizer(), remove_retweets=False)
		outlines = 0
		with open(output, 'r') as outfile:
			for line in outfile:
				outlines += 1

		self.assertEqual(inlines, outlines)

	def test_tokenize_corpus_remove_retweets(self):
		"""
		Test that when removing retweets, the number of lines should decrease.
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
		tool.tokenize_corpus(file, output, Tokenizer(), remove_retweets=True)
		outlines = 0
		with open(output, 'r') as outfile:
			for line in outfile:
				outlines += 1

		self.assertGreater(inlines, outlines)

	def test_tokenize_corpus_remove_retweets_retweeted_status(self):
		"""
		Test that when removing retweets, the `retweeted_status` attribute is never present.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and ensure that the ID is present in all tweets.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer(), keep=[ 'retweeted_status' ], remove_retweets=True)
		with open(output, 'r') as outfile:
			self.assertTrue(not any( json.loads(line)['retweeted_status'] in json.loads(line) for line in outfile ))

	def test_tokenize_corpus_remove_retweets_keep_quoted(self):
		"""
		Test that when removing retweets, quoted statuses are retained.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and ensure that the ID is present in all tweets.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer(), keep=[ 'quoted_status' ], remove_retweets=True)
		with open(output, 'r') as outfile:
			self.assertTrue(any( json.loads(line)['quoted_status'] for line in outfile ))

	def test_tokenize_corpus_keep_stopwords(self):
		"""
		Test that when tokenizing a corpus without removing stopwords, they are retained.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and again collect the lines in the tokenized corpus.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer(stem=False, stopwords={ }))
		with open(output, 'r') as outfile:
			self.assertTrue(any( 'while' in json.loads(line)['tokens'] for line in outfile.readlines() ))
			outfile.seek(0)
			self.assertTrue(any( 'the' in json.loads(line)['tokens'] for line in outfile.readlines() ))
			outfile.seek(0)
			self.assertTrue(any( 'this' in json.loads(line)['tokens'] for line in outfile.readlines() ))

	def test_tokenize_corpus_remove_stopwords(self):
		"""
		Test that when tokenizing a corpus and removing stopwords, no stopwords remain.
		"""

		file = 'tools/tests/corpus.json'
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and again collect the lines in the tokenized corpus.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer(stem=False, stopwords=stopwords.words('english')))
		with open(output, 'r') as outfile:
			self.assertTrue(not any( 'while' in json.loads(line)['tokens'] for line in outfile.readlines() ))
			outfile.seek(0)
			self.assertTrue(not any( 'the' in json.loads(line)['tokens'] for line in outfile.readlines() ))
			outfile.seek(0)
			self.assertTrue(not any( 'this' in json.loads(line)['tokens'] for line in outfile.readlines() ))

	def test_tokenize_corpus_nouns(self):
		"""
		Test that when tokenizing a corpus and retaining only nouns, other words do not remain.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'CRYCHE-100.json')
		output = 'tools/tests/.out/tokenized.json'

		"""
		Tokenize the corpus and again collect the lines in the tokenized corpus.
		"""
		tool.prepare_output(output)
		tool.tokenize_corpus(file, output, Tokenizer(nouns_only=True))
		with open(output, 'r') as outfile:
			self.assertTrue(not any( 'while' in json.loads(line)['tokens'] for line in outfile.readlines() ))
			outfile.seek(0)
			self.assertTrue(not any( 'feel' in json.loads(line)['tokens'] for line in outfile.readlines() ))
			outfile.seek(0)
			self.assertTrue(any( 'chelsea' in json.loads(line)['tokens'] for line in outfile.readlines() ))

	def test_tokenize_corpus_nouns_subset(self):
		"""
		Test that when tokenizing a corpus and retaining only nouns, the tokens are a subset of the original tokenized corpus.
		"""

		file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'CRYCHE-100.json')
		output = [ 'tools/tests/.out/nouns.json',
				   'tools/tests/.out/tokenized.json' ]

		"""
		Tokenize the corpus and again collect the lines in the tokenized corpus.
		"""
		tool.prepare_output(output[0])
		tool.prepare_output(output[1])
		tool.tokenize_corpus(file, output[0], Tokenizer(nouns_only=True, remove_punctuation=True))
		tool.tokenize_corpus(file, output[1], Tokenizer(nouns_only=False, remove_punctuation=True))

		with open(output[0], 'r') as nounfile, \
			 open(output[1], 'r') as tokenfile:
			for line in nounfile:
				nouns = json.loads(line)['tokens']
				tokens = json.loads(tokenfile.readline())['tokens']
				self.assertTrue(all( noun in tokens for noun in nouns ))
