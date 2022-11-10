"""
Test the functionality of the tokenizer tool.
"""

import json
import os
import sys
import tarfile
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
from eventdt import twitter
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

    def test_write_archive_correct_folder_structure(self):
        """
        Test that writing an archive re-creates the folder structure.
        """

        file = 'eventdt/tests/corpora/#AjaxRoma.tar.gz'
        output = 'tools/tests/.out/'

        tool.write_archive(file, output)
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma'))
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma/.cache'))

    def test_write_archive_ignores_filename(self):
        """
        Test that writing an archive re-creates the folder structure by ignoring any filename in the output path.
        """

        file = 'eventdt/tests/corpora/#AjaxRoma.tar.gz'
        output = 'tools/tests/.out/#AjaxRoma.json'

        tool.write_archive(file, output)
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma'))
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma/.cache'))

    def test_write_archive_all_files(self):
        """
        Test that writing an archive re-creates the folder structure with all files.
        """

        file = 'eventdt/tests/corpora/#AjaxRoma.tar.gz'
        output = 'tools/tests/.out/'

        tool.write_archive(file, output)
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma'))
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma/event.json'))
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma/understanding.json'))
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma/meta.json'))
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma/.cache'))
        self.assertTrue(os.path.exists('tools/tests/.out/#AjaxRoma/.cache/understanding.json'))

    def test_write_archive_event_IDs(self):
        """
        Test that writing an archive saves the tweet IDs correctly.
        """

        file = 'eventdt/tests/corpora/#AjaxRoma.tar.gz'
        output = 'tools/tests/.out/'

        tool.write_archive(file, output)

        with tarfile.open(file) as archive:
            for member in archive:
                path, filename = os.path.split(member.name)
                if filename == 'event.json':
                    with archive.extractfile(member) as _file:
                        inids = [ twitter.id(json.loads(line)) for line in _file ]

        with open('tools/tests/.out/#AjaxRoma/event.json', 'r') as _file:
            outids = [ line.strip() for line in _file ]

        self.assertEqual(inids, outids)

    def test_write_archive_understanding_IDs(self):
        """
        Test that writing an archive saves the tweet IDs correctly.
        """

        file = 'eventdt/tests/corpora/#AjaxRoma.tar.gz'
        output = 'tools/tests/.out/'

        tool.write_archive(file, output)

        with tarfile.open(file) as archive:
            for member in archive:
                path, filename = os.path.split(member.name)
                if filename == 'understanding.json' and '.cache' not in path:
                    with archive.extractfile(member) as _file:
                        inids = [ twitter.id(json.loads(line)) for line in _file ]

        with open('tools/tests/.out/#AjaxRoma/understanding.json', 'r') as _file:
            outids = [ line.strip() for line in _file ]

        self.assertEqual(inids, outids)

    def test_write_archive_meta_file(self):
        """
        Test that writing an archive reproduces the meta file identically.
        """

        file = 'eventdt/tests/corpora/#AjaxRoma.tar.gz'
        output = 'tools/tests/.out/'

        tool.write_archive(file, output)

        with tarfile.open(file) as archive:
            for member in archive:
                path, filename = os.path.split(member.name)
                if filename == 'meta.json':
                    with archive.extractfile(member) as _file:
                        meta = json.loads(_file.readline())

        with open('tools/tests/.out/#AjaxRoma/meta.json', 'r') as _file:
            self.assertEqual(meta, json.loads(_file.readline()))

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

    def test_write_timeline_removes_attribues(self):
        """
        Test that when making multiple timelines shareable, all attributes are removed except for the tweet IDs.
        """

        file = 'eventdt/tests/corpora/timelines/#ParmaMilan-streams.json'
        output = 'tools/tests/.out/shareable.json'

        with open(file, 'r') as infile:
            timelines = Exportable.decode(json.loads(infile.readline()))['timeline']
            ids = [ document.id for timeline in timelines for node in timeline.nodes for document in node.get_all_documents() ]
            for timeline in timelines:
                for node in timeline.nodes:
                    for document in node.get_all_documents():
                        document.attributes['test'] = True

        self.assertTrue(all( document.test for timeline in timelines for node in timeline.nodes for document in node.get_all_documents() ))

        tools.save(output, {})
        tool.write_timeline(file, output)
        with open(output, 'r') as outfile:
            timelines = Exportable.decode(json.loads(outfile.readline()))['timeline']
            _ids = [ document.id for timeline in timelines for node in timeline.nodes for document in node.get_all_documents() ]
            self.assertTrue(all( set(document.attributes.keys()) ==  { 'id', 'tweet' }
                                 for timeline in timelines for node in timeline.nodes for document in node.get_all_documents() ))

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

    def test_write_corpus_v2_same_order(self):
        """
        Test that when making a Twitter APIv2 corpus shareable, the tweets are saved in the correct order.
        """

        file = 'eventdt/tests/corpora/LEIMUNv2.json'
        output = 'tools/tests/.out/shareable.json'

        """
        Collect the IDs in the input file.
        """
        inids = [ ]
        with open(file, 'r') as infile:
            for line in infile:
                inids.append(twitter.id(json.loads(line)))

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
