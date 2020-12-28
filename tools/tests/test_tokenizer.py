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

    def test_get_tags_none(self):
        """
        Test that when getting no tags, `None is returned`
        """

        self.assertEqual(None,
                         tool.get_tags(nouns=False, proper_nouns=False, verbs=False, adjectives=False))

    def test_get_tags_nouns(self):
        """
        Test getting the noun tags.
        """

        self.assertEqual([ 'NN', 'NNS' ],
                         tool.get_tags(nouns=True, proper_nouns=False, verbs=False, adjectives=False))

    def test_get_tags_proper_nouns(self):
        """
        Test getting the proper noun tags.
        """

        self.assertEqual([ 'NNP', 'NNPS' ],
                         tool.get_tags(nouns=False, proper_nouns=True, verbs=False, adjectives=False))

    def test_get_tags_verbs(self):
        """
        Test getting the verb tags.
        """

        self.assertEqual([ 'VB', 'VBG', 'VBD', 'VBN', 'VBP', 'VBZ' ],
                         tool.get_tags(nouns=False, proper_nouns=False, verbs=True, adjectives=False))

    def test_get_tags_adjectives(self):
        """
        Test getting the adjective tags.
        """

        self.assertEqual([ 'JJ', 'JJR', 'JJS' ],
                         tool.get_tags(nouns=False, proper_nouns=False, verbs=False, adjectives=True))

    def test_get_tags_all_nouns(self):
        """
        Test getting all noun tags.
        """

        self.assertEqual([ 'NN', 'NNS', 'NNP', 'NNPS' ],
                         tool.get_tags(nouns=True, proper_nouns=True, verbs=False, adjectives=False))

    def test_get_tags_mix(self):
        """
        Test getting mixed tags.
        """

        self.assertEqual([ 'NN', 'NNS', 'JJ', 'JJR', 'JJS' ],
                         tool.get_tags(nouns=True, proper_nouns=False, verbs=False, adjectives=True))

    def test_get_tags_all(self):
        """
        Test getting all tags.
        """

        self.assertEqual([ 'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBG', 'VBD', 'VBN', 'VBP', 'VBZ', 'JJ', 'JJR', 'JJS' ],
                         tool.get_tags(nouns=True, proper_nouns=True, verbs=True, adjectives=True))

    def test_tokenize_corpus_same_lines(self):
        """
        Test that when tokenizing a corpus, the same number of lines are outputted.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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
        Test that when specifying attributes to keep, an attribute that appears occasionally is still stored, but as ``None``, when not found.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-500.json'
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

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
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
        tags = tool.get_tags(nouns=True, proper_nouns=False, verbs=False, adjectives=False)
        tool.tokenize_corpus(file, output, Tokenizer(pos=tags))
        with open(output, 'r') as outfile:
            self.assertTrue(not any( 'while' in json.loads(line)['tokens'] for line in outfile.readlines() ))
            outfile.seek(0)
            self.assertTrue(not any( 'feel' in json.loads(line)['tokens'] for line in outfile.readlines() ))
            outfile.seek(0)
            self.assertTrue(any( 'chelsea' in json.loads(line)['tokens'] for line in outfile.readlines() ))
