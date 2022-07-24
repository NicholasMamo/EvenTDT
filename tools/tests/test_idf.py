"""
Test the functionality of the IDF tool.
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

import idf

class TestIDF(unittest.TestCase):
    """
    Test the functionality of the IDF tool.
    """

    def test_is_own_idf(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertTrue(idf.is_own(output))

    def test_is_own_other(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertFalse(idf.is_own(output))

    def test_is_own_txt(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "gold.txt")
        self.assertFalse(idf.is_own(file))

    def test_is_own_idf_path(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        self.assertTrue(idf.is_own(file))

    def test_is_own_other_path(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        self.assertFalse(idf.is_own(file))

    def test_load_from_output(self):
        """
        Test that when loading the IDF from the output of the tool, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            _idf = idf.load(output)
            original = output['tfidf']
        self.assertEqual(original, _idf)

    def test_load_from_path(self):
        """
        Test that when loading the IDF from a filepath, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            original = output['tfidf']
        _idf = idf.load(file)
        self.assertEqual(original, _idf)

    def test_construct_all_lines(self):
        """
        Test that when creating an IDF table, the number of documents is equal to the number of lines.
        """

        file = 'eventdt/tests/corpora/CRYCHE-500.json'

        """
        Create an IDF and assert that it has all lines.
        """
        tfidf = idf.construct(file, remove_retweets=False, stem=True)
        self.assertEqual(500, tfidf.global_scheme.documents)

    def test_construct_no_retweets_fewer_documents(self):
        """
        Test that when creating an IDF table without retweets, the number of documents is fewer.
        """

        file = 'eventdt/tests/corpora/CRYCHE-500.json'

        """
        Create an IDF with retweets and another without retweets.
        """
        tfidf = idf.construct(file, remove_retweets=False, stem=True)
        tfidf_wo_rt = idf.construct(file, remove_retweets=True, stem=True)

        """
        Assert that the IDF with retweets has more documents than the one without retweets.
        """
        self.assertGreater(tfidf.global_scheme.documents, tfidf_wo_rt.global_scheme.documents)

    def test_construct_no_retweets_subset(self):
        """
        Test that when creating an IDF table without retweets, its terms are a subset of the IDF with retweets.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'

        """
        Create an IDF with retweets and another without retweets.
        """
        tfidf = idf.construct(file, remove_retweets=False, stem=True)
        tfidf_wo_rt = idf.construct(file, remove_retweets=True, stem=True)

        """
        Assert that all of the terms in the IDF without retweets are in the IDF with retweets.
        """
        self.assertTrue(all( term in tfidf.global_scheme.idf for term in tfidf_wo_rt.global_scheme.idf ))

        """
        Assert that the DF of all terms in the IDF without retweets are less than or equal to the DF of the IDF with retweets.
        """
        self.assertTrue(all( tfidf_wo_rt.global_scheme.idf[term] <= tfidf.global_scheme.idf[term] for term in tfidf_wo_rt.global_scheme.idf ))

    def test_construct_skip_unverified_fewer_documents(self):
        """
        Test that when creating an IDF table without retweets, the number of documents is fewer.
        """

        file = 'eventdt/tests/corpora/CRYCHE-500.json'

        """
        Create an IDF with all authors and another with just verified authors.
        """
        tfidf = idf.construct(file, skip_unverified=False, stem=True)
        tfidf_wo_unverified = idf.construct(file, skip_unverified=True, stem=True)

        """
        Assert that the IDF with all authors has more tweets than the one without unverified authors.
        """
        self.assertGreater(tfidf.global_scheme.documents, tfidf_wo_unverified.global_scheme.documents)

    def test_construct_skip_unverified_subset(self):
        """
        Test that when creating an IDF table without retweets, its terms are a subset of the IDF with retweets.
        """

        file = 'eventdt/tests/corpora/CRYCHE-500.json'

        """
        Create an IDF with retweets and another without retweets.
        """
        tfidf = idf.construct(file, skip_unverified=False, stem=True)
        tfidf_wo_unverified = idf.construct(file, skip_unverified=True, stem=True)

        """
        Assert that all of the terms in the IDF with verified authors are in the IDF with all authors.
        """
        self.assertTrue(all( term in tfidf.global_scheme.idf for term in tfidf_wo_unverified.global_scheme.idf ))

        """
        Assert that the DF of all terms in the IDF with verified authors are less than or equal to the DF of the IDF with all authors.
        """
        self.assertTrue(all( tfidf_wo_unverified.global_scheme.idf[term] <= tfidf.global_scheme.idf[term] for term in tfidf_wo_unverified.global_scheme.idf ))
