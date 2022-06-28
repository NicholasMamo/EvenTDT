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

import shareable as tool
import tools

class TestShareable(unittest.TestCase):
    """
    Test the functionality of the shareabl tool.
    """

    def test_is_timeline_false(self):
        """
        Test that when providing a path to a tweet corpus, the function detects it as one.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        self.assertFalse(tool.is_timeline(file))

    def test_is_timeline_true(self):
        """
        Test that when providing a path to a timeline, the function detects it as one.
        """

        file = 'eventdt/tests/corpora/timelines/CRYCHE.json'
        self.assertTrue(tool.is_timeline(file))

    def test_is_timeline_streamed(self):
        """
        Test that when providing a path to a streamed timeline, the function detects it as one.
        """

        file = 'eventdt/tests/corpora/timelines/#ParmaMilan-streams.json'
        self.assertTrue(tool.is_timeline(file))

    def test_write_corpus_same_lines(self):
        """
        Test that when tokenizing a corpus, the same number of lines are outputted.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        output = 'tools/tests/.out/shareable.json'

        """
        Count the number of lines in the corpus.
        """
        inlines = 0
        with open(file, 'r') as infile:
            for line in infile:
                inlines += 1

        """
        Tokenize the corpus and again count the number of lines in the shareable corpus.
        """
        tools.save(output, {})
        tool.write(file, output)
        outlines = 0
        with open(output, 'r') as outfile:
            for line in outfile:
                outlines += 1

        self.assertEqual(inlines, outlines)

    def test_write_corpus_same_order(self):
        """
        Test that when tokenizing a corpus, the tweets are saved in the correct order.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        output = 'tools/tests/.out/shareable.json'

        """
        Collect the IDs in the input file.
        """
        inids = [ ]
        with open(file, 'r') as infile:
            for line in infile:
                inids.append(json.loads(line)['id_str'])

        """
        Tokenize the corpus and again collect the lines in the shareable corpus.
        """
        tools.save(output, {})
        tool.write(file, output)
        outids = [ ]
        with open(output, 'r') as outfile:
            for line in outfile:
                outids.append(line.strip())

        self.assertEqual(inids, outids)
