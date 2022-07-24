"""
Test the functionality of the correlation tool.
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

import correlation
from eventdt.ate.bootstrapping.probability import ChiBootstrapper, PMIBootstrapper
from logger import logger

logger.set_logging_level(logger.LogLevel.ERROR)

class TestCorrelation(unittest.TestCase):
    """
    Test the functionality of the correlation tool.
    """

    def test_is_own_correlations(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "correlations.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertTrue(correlation.is_own(output))

    def test_is_own_other(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertFalse(correlation.is_own(output))

    def test_is_own_correlations_path(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "correlations.json")
        self.assertTrue(correlation.is_own(file))

    def test_is_own_other_path(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        self.assertFalse(correlation.is_own(file))

    def test_load_from_output(self):
        """
        Test that when loading terms from the output of the tool, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'correlations.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            _correlations = correlation.load(output)
            original = output['correlations']
        self.assertEqual(original, _correlations)

    def test_load_from_path(self):
        """
        Test that when loading correlations from a filepath, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'correlations.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            original = output['correlations']
        _correlations = correlation.load(file)
        self.assertEqual(original, _correlations)

    def test_load_terms_all_terms(self):
        """
        Test that when loading terms and they are given explicitly, they are used.
        """

        terms = [ 'first', 'second', 'half', 'underway' ]
        self.assertTrue(all( term in correlation.load_terms(terms) for term in terms ))

    def test_load_terms_order(self):
        """
        Test that when loading terms, they are kept in the same order as given.
        """

        terms = [ 'first', 'second', 'half', 'underway' ]
        self.assertEqual(terms, correlation.load_terms(terms))

    def test_load_terms_extracted(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, the terms themselves are loaded.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json') ]
        terms = correlation.load_terms(files)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(files[0]) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(len(original), len(terms))

    def test_load_terms_extracted_cmd(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, the terms themselves are loaded.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'sample.json') ]
        terms = correlation.load_terms(files)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(files[0]) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(len(original), len(terms))

    def test_load_terms_extracted_order(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, they are loaded in order of rank.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json') ]
        terms = correlation.load_terms(files)
        with open(files[0]) as f:
            original = json.loads(''.join(f.readlines()))['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(original, terms)

    def test_load_terms_bootstrapped(self):
        """
        Test that when loading terms from the output of the ``bootstrap`` tool, the terms themselves are loaded.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped.json') ]
        terms = correlation.load_terms(files)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(files[0]) as f:
            data = json.loads(''.join(f.readlines()))
            original = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(len(original), len(terms))

    def test_load_terms_bootstrapped_order(self):
        """
        Test that when loading terms from the output of the ``bootstrap`` tool, the seed terms are first, followed by the bootstrapped terms.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped.json') ]
        terms = correlation.load_terms(files)
        with open(files[0]) as f:
            data = json.loads(''.join(f.readlines()))
            original = data['meta']['seed'] + data['bootstrapped']
        self.assertEqual(original, terms)

    def test_load_terms_bootstrapped_new(self):
        """
        Test that when loading terms from the output of the ``bootstrap`` tool, the terms themselves are loaded.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped-new.json') ]
        terms = correlation.load_terms(files)
        self.assertTrue(all( type(term) is str for term in terms ))
        with open(files[0]) as f:
            data = json.loads(''.join(f.readlines()))
            original = data['pcmd']['seed'] + [ term['term'] for term in data['bootstrapped'] ]
        self.assertEqual(len(original), len(terms))

    def test_load_terms_bootstrapped_new_order(self):
        """
        Test that when loading terms from the output of the ``bootstrap`` tool, the seed terms are first, followed by the bootstrapped terms.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped-new.json') ]
        terms = correlation.load_terms(files)
        with open(files[0]) as f:
            data = json.loads(''.join(f.readlines()))
            original = data['pcmd']['seed'] + [ term['term'] for term in data['bootstrapped'] ]
        self.assertEqual(original, terms)

    def test_load_terms_mix(self):
        """
        Test that when loading terms from a mix of words and files, they are all loaded in the same order.
        """

        files = [ 'yellow', 'card',
                  os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'bootstrapped.json') ]
        terms = correlation.load_terms(files)
        original = files[:2]
        with open(files[2]) as f:
            data = json.loads(''.join(f.readlines()))
            original.extend([ term['term'] for term in data['terms'] ])
        with open(files[3]) as f:
            data = json.loads(''.join(f.readlines()))
            original.extend(data['meta']['seed'] + data['bootstrapped'])
        self.assertEqual(original, terms)

    def test_load_terms_max_terms_less_than_two(self):
        """
        Test that when the number of maximum terms is less than 2, a ValueError is raised.
        """

        terms = [ 'card', 'yellow', 'foul', 'tackl', 'red', 'var', 'refere', 'ref' ]
        self.assertRaises(ValueError, correlation.load_terms, terms, max_terms=1)

    def test_load_terms_max_terms_two(self):
        """
        Test that when the maximum number of terms is 2, the first 2 terms are returned.
        """

        terms = [ 'card', 'yellow', 'foul', 'tackl', 'red', 'var', 'refere', 'ref' ]
        self.assertEqual(terms[:2], correlation.load_terms(terms, max_terms=2))

    def test_load_terms_no_max_terms(self):
        """
        Test that when no maximum number of terms is given, all terms are retained.
        """

        terms = [ 'card', 'yellow', 'foul', 'tackl', 'red', 'var', 'refere', 'ref' ]
        self.assertEqual(terms, correlation.load_terms(terms, max_terms=None))

    def test_load_terms_max_terms(self):
        """
        Test that when the maximum number of terms is given, the first few terms are returned.
        """

        terms = [ 'card', 'yellow', 'foul', 'tackl', 'red', 'var', 'refere', 'ref' ]
        self.assertEqual(terms[:3], correlation.load_terms(terms, max_terms=3))

    def test_extract_dict(self):
        """
        Test that the correlation returns a dictionary of keywords.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        terms = [ 'first', 'second', 'half', 'underway' ]

        extractor = correlation.create_extractor(PMIBootstrapper)
        c = correlation.extract(extractor, files, terms)
        self.assertEqual(dict, type(c))
        self.assertTrue(all( type(c.get(v)) is dict for v in c ))

    def test_extract_all_keywords(self):
        """
        Test that the correlation returns all initial terms.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        terms = [ 'first', 'second', 'half', 'underway' ]

        extractor = correlation.create_extractor(PMIBootstrapper)
        c = correlation.extract(extractor, files, terms)
        self.assertEqual(set(terms), set(c))

    def test_extract_nested_all_keywords(self):
        """
        Test that the correlation returns all initial terms in the nested dictionaries.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        terms = [ 'first', 'second', 'half', 'underway' ]

        extractor = correlation.create_extractor(PMIBootstrapper)
        c = correlation.extract(extractor, files, terms)
        self.assertTrue(all( set(terms) == set(v) for v in c.values() ))

    def test_extract_nested_all_keywords(self):
        """
        Test that the correlation returns all initial terms in the nested dictionaries.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        terms = [ 'first', 'second', 'half', 'underway' ]

        extractor = correlation.create_extractor(PMIBootstrapper)
        c = correlation.extract(extractor, files, terms)
        self.assertTrue(all( set(terms) == set(v) for v in c.values() ))

    def test_extract_pmi_symmetric(self):
        """
        Test that the correlation with PMI is symmetric.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        terms = [ 'first', 'second', 'half', 'underway' ]

        extractor = correlation.create_extractor(PMIBootstrapper)
        c = correlation.extract(extractor, files, terms)
        for t1 in terms:
            for t2 in terms:
                self.assertEqual(c[t1][t2], c[t2][t1])

    def test_extract_chi_symmetric(self):
        """
        Test that the correlation with CHI is symmetric.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        terms = [ 'first', 'second', 'half', 'underway' ]

        extractor = correlation.create_extractor(ChiBootstrapper)
        c = correlation.extract(extractor, files, terms)
        for t1 in terms:
            for t2 in terms:
                self.assertEqual(c[t1][t2], c[t2][t1])

    def test_extract_unknown_words(self):
        """
        Test that the correlation of unknown words is 0.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        terms = [ 'first', 'second', 'half', 'underway', 'superlongword' ]

        extractor = correlation.create_extractor(ChiBootstrapper)
        c = correlation.extract(extractor, files, terms)
        self.assertTrue(all( c['superlongword'][term] == 0 for term in terms ))

    def test_extract(self):
        """
        Test that the extraction makes sense.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        terms = [ 'first', 'second', 'half', 'underway', 'yellow', 'card' ]

        extractor = correlation.create_extractor(PMIBootstrapper)
        c = correlation.extract(extractor, files, terms)
        self.assertGreater(c['first']['half'], c['yellow']['half'])
        self.assertGreater(c['yellow']['card'], c['first']['card'])
