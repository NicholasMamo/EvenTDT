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

from eventdt.objects import Exportable
from eventdt.summarization.timeline import Timeline
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

    def test_write_timeline_single(self):
        """
        Test that when making a single timeline shareable, the output also contains just one timeline, not a list.
        """

        file = 'eventdt/tests/corpora/timelines/TOTLEI.json'
        output = 'tools/tests/.out/shareable.json'

        with open(file, 'r') as infile:
            timeline = Exportable.decode(json.loads(infile.readline()))['timeline']
            self.assertEqual(Timeline.__name__, type(timeline).__name__)

        tools.save(output, {})
        tool.write_timeline(file, output)
        with open(output, 'r') as outfile:
            timeline = Exportable.decode(json.loads(outfile.readline()))['timeline']
            self.assertEqual(Timeline.__name__, type(timeline).__name__)
            
    def test_write_timeline_single_same_tweets(self):
        """
        Test that when making a timeline shareable, the same tweets are kept.
        """

        file = 'eventdt/tests/corpora/timelines/TOTLEI.json'
        output = 'tools/tests/.out/shareable.json'

        with open(file, 'r') as infile:
            timeline = Exportable.decode(json.loads(infile.readline()))['timeline']
            ids = [ document.id for node in timeline.nodes for document in node.get_all_documents() ]

        tools.save(output, {})
        tool.write_timeline(file, output)
        with open(output, 'r') as outfile:
            timeline = Exportable.decode(json.loads(outfile.readline()))['timeline']
            _ids = [ document.id for node in timeline.nodes for document in node.get_all_documents() ]

        self.assertEqual(ids, _ids)

    def test_write_timeline_multiple(self):
        """
        Test that when making multiple timelines shareable, the output also contains just multiple timelines as a list.
        """

        file = 'eventdt/tests/corpora/timelines/#ParmaMilan-streams.json'
        output = 'tools/tests/.out/shareable.json'

        with open(file, 'r') as infile:
            timeline = Exportable.decode(json.loads(infile.readline()))['timeline']
            self.assertEqual(list, type(timeline))
            self.assertTrue(all( Timeline.__name__ == type(_timeline).__name__ for _timeline in timeline ))

        tools.save(output, {})
        tool.write_timeline(file, output)
        with open(output, 'r') as outfile:
            timeline = Exportable.decode(json.loads(outfile.readline()))['timeline']
            self.assertEqual(list, type(timeline))
            self.assertTrue(all( Timeline.__name__ == type(_timeline).__name__ for _timeline in timeline ))

    def test_write_timeline_multiple_same_tweets(self):
        """
        Test that when making multiple timelines shareable, the same tweets are kept and in the same order.
        """

        file = 'eventdt/tests/corpora/timelines/#ParmaMilan-streams.json'
        output = 'tools/tests/.out/shareable.json'

        with open(file, 'r') as infile:
            timelines = Exportable.decode(json.loads(infile.readline()))['timeline']
            ids = [ document.id for timeline in timelines for node in timeline.nodes for document in node.get_all_documents() ]

        tools.save(output, {})
        tool.write_timeline(file, output)
        with open(output, 'r') as outfile:
            timelines = Exportable.decode(json.loads(outfile.readline()))['timeline']
            _ids = [ document.id for timeline in timelines for node in timeline.nodes for document in node.get_all_documents() ]

        self.assertEqual(ids, _ids)

    def test_write_timeline_no_tweets(self):
        """
        Test that when making a timeline shareable, the tweets themselves aren't kept—only the IDs.
        """

        file = 'eventdt/tests/corpora/timelines/TOTLEI.json'
        output = 'tools/tests/.out/shareable.json'

        tools.save(output, {})
        tool.write_timeline(file, output)
        with open(output, 'r') as outfile:
            timeline = Exportable.decode(json.loads(outfile.readline()))['timeline']
            self.assertTrue(all( document.tweet == { 'id': str(document.id) }
                                 for node in timeline.nodes
                                 for document in node.get_all_documents() ))

    def test_write_corpus_same_lines(self):
        """
        Test that when making a corpus shareable, the same number of lines are outputted.
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
        Test that when making a corpus shareable, the tweets are saved in the correct order.
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
