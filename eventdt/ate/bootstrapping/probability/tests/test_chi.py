"""
Test the functionality of the chi-square bootstrapper.
"""

import json
import os
import string
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate
from ate.bootstrapping.probability import ChiBootstrapper
from ate.stat import probability
from objects.exportable import Exportable

class TestChiBootstrapper(unittest.TestCase):
    """
    Test the functionality of the chi-square bootstrapper.
    """

    def test_bootstrap_empty_corpus(self):
        """
        Test that when calculating the chi-square statistic on an empty corpus, all statistics are zero.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'empty.json')
        seed, candidates = [ 'yellow' ], [ 'foul', 'tackl' ]
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(path, seed, candidates)
        self.assertTrue(all( 0 == value for value in chi.values() ))

    def test_bootstrap_str_seed(self):
        """
        Test that when `seed` is a string, it is treated as such.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        seed, candidates = 'yellow', [ 'foul', 'tackl' ]
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(paths, seed, candidates)
        self.assertTrue(('yellow', 'foul') in chi)
        self.assertTrue(('yellow', 'tackl') in chi)

    def test_bootstrap_str_candidates(self):
        """
        Test that when `candidates` is a string, it is treated as such.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        seed, candidates = [ 'foul', 'tackl' ], 'yellow'
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(paths, seed, candidates)
        self.assertTrue(('foul', 'yellow') in chi)
        self.assertTrue(('tackl', 'yellow') in chi)

    def test_bootstrap_list_seed(self):
        """
        Test that when `seed` is a list, it is treated as such.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        seed, candidates = [ 'foul', 'tackl' ], 'yellow'
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(paths, seed, candidates)
        self.assertTrue(('foul', 'yellow') in chi)
        self.assertTrue(('tackl', 'yellow') in chi)

    def test_bootstrap_list_candidates(self):
        """
        Test that when `candidates` is a list, it is treated as such.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        seed, candidates = 'yellow', [ 'foul', 'tackl' ]
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(paths, seed, candidates)
        self.assertTrue(('yellow', 'foul') in chi)
        self.assertTrue(('yellow', 'tackl') in chi)

    def test_bootstrap_str_seed_candidates(self):
        """
        Test that when `seed` and `candidates` are strings, only one pair is returned.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        seed, candidates = 'yellow', 'foul'
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(paths, seed, candidates)
        self.assertEqual({ ('yellow', 'foul') }, set(chi.keys()))

    def test_bootstrap_list_x_y(self):
        """
        Test that when `seed` and `candidates` are lists, their cross-product is returned.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        seed, candidates = [ 'yellow', 'red' ], [ 'foul', 'tackl' ]
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(paths, seed, candidates)
        self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl'),
                            ('red', 'foul'), ('red', 'tackl') },
                         set(chi.keys()))

    def test_bootstrap_nonexisting_word(self):
        """
        Test that non-existing words are also included in the chi-statistic.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        seed, candidates = 'yellow', 'superlongword'
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(paths, seed, candidates)
        self.assertTrue(('yellow', 'superlongword') in chi)
        self.assertEqual(0, chi[('yellow', 'superlongword')])

    def test_bootstrap_example(self):
        """
        Test with an example chi-square value.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')
        seed, candidates = [ 'yellow', 'shoot' ], [ 'foul', 'tackl', 'save' ]
        bootstrapper = ChiBootstrapper()
        chi = bootstrapper.bootstrap(path, seed, candidates)
        self.assertGreater(chi[('yellow', 'tackl')], chi['shoot', 'tackl'])
        self.assertGreater(chi[('yellow', 'foul')], chi['shoot', 'foul'])
        self.assertGreater(chi[('shoot', 'save')], chi['yellow', 'save'])

    def test_contingency_table_empty_corpus(self):
        """
        Test that when creating the contingency table of an empty corpus results in all zeroes.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'empty.json')
        bootstrapper = ChiBootstrapper()
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, 'a', 'b')
        self.assertEqual(0, sum(tables[('a', 'b')]))

    def test_contingency_table_single_corpus(self):
        """
        Test that when creating the contingency table from a single corpus, the total of each contingency table adds up to the total number of documents in that corpus.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, 'a', 'b')
        self.assertEqual(ate.total_documents(path), sum(tables[('a', 'b')]))

    def test_contingency_table_multiple_corpora(self):
        """
        Test that when creating the contingency table from multiple corpora, the total of each contingency table adds up to the total number of documents in all corpora.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        total = ate.total_documents(paths)
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, 'a', 'b')
        self.assertEqual(total, sum(tables[('a', 'b')]))

    def test_contingency_table_str_seed(self):
        """
        Test that when creating the contingency table with one `seed`, the contingency table treats it correctly as a string.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, 'yellow', [ 'foul', 'tackl' ])
        self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl') }, tables.keys())

    def test_contingency_table_str_candidates(self):
        """
        Test that when creating the contingency table with one `candidates`, the contingency table treats it correctly as a string.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], 'yellow')
        self.assertEqual({ ('foul', 'yellow'), ('tackl', 'yellow') }, tables.keys())

    def test_contingency_table_list_seed(self):
        """
        Test that when creating the contingency table with multiple `seed`, the contingency table treats it correctly as a list.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, [ 'yellow', 'red' ], [ 'foul', 'tackl' ])
        self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl'),
                           ('red', 'foul'), ('red', 'tackl') },
                         tables.keys())

    def test_contingency_table_list_candidates(self):
        """
        Test that when creating the contingency table with multiple `candidates`, the contingency table treats it correctly as a list.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
        self.assertEqual({ ('foul', 'yellow'), ('foul', 'red'),
                           ('tackl', 'yellow'), ('tackl', 'red') },
                         tables.keys())

    def test_contingency_table_token_not_found(self):
        """
        Test that even if a token is not found, a contingency table is created for it.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')
        total = ate.total_documents(path)
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], [ 'superlongword' ])
        self.assertEqual({ ('foul', 'superlongword'), ('tackl', 'superlongword') },
                         tables.keys())
        self.assertTrue(all( total == sum(table) for table in tables.values() ))

    def test_contingency_table_row_total(self):
        """
        Test that the row totals are correct.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], 'yellow')
        counts = { token: len(probability.cached(paths, token)) for token in [ 'foul', 'tackl' ] }
        for pair, table in tables.items():
            expected = counts['foul'] if 'foul' in pair else counts['tackl']
            self.assertEqual(expected, table[0] + table[1])

    def test_contingency_table_column_total(self):
        """
        Test that the column totals are correct.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
        counts = { token: len(probability.cached(paths, token)) for token in [ 'yellow', 'red' ] }
        for pair, table in tables.items():
            expected = counts['yellow'] if 'yellow' in pair else counts['red']
            self.assertEqual(expected, table[0] + table[2])

    def test_contingency_table_totals(self):
        """
        Test that the contingency table totals add up to the number of documents in the corpora.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
        total = ate.total_documents(paths)
        self.assertTrue(all( total == sum(table) for table in tables.values() ))

    def test_contingency_table_joint_count(self):
        """
        Test that the joint counts are correct.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

        seed, candidates = [ 'foul', 'tackl' ], 'yellow'
        freq = dict.fromkeys(probability.joint_vocabulary(seed, candidates), 0)
        for corpus in paths:
            with open(corpus, 'r') as f:
                for line in f:
                    document = json.loads(line)
                    for pair in freq:
                        if pair[0] in document['tokens'] and pair[1] in document['tokens']:
                            freq[pair] += 1

        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, seed, candidates)
        for pair in tables:
            self.assertEqual(freq[pair], tables[pair][0])

    def test_contingency_table_symmetric(self):
        """
        Test that the contingency table is symmetric, but otherwise all counts are the same.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

        seed, candidates = [ 'foul', 'tackl' ], 'yellow'
        bootstrapper = ChiBootstrapper()
        t1, t2 = bootstrapper._contingency_table(paths, seed, candidates), bootstrapper._contingency_table(paths, candidates, seed)
        for t1, t2 in zip(t1.values(), t2.values()):
            self.assertEqual(t1[0], t2[0])
            self.assertEqual(t1[1], t2[2])
            self.assertEqual(t1[2], t2[1])
            self.assertEqual(t1[3], t2[3])

    def test_contingency_table_cache(self):
        """
        Test that the contingency table's cache results in the same table as without cache.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'BVBFCB-100.json') ]

        seed, candidates = [ 'yellow', 'red' ], [ 'foul', 'tackl' ]
        bootstrapper = ChiBootstrapper()
        cached = bootstrapper._contingency_table(paths, seed, candidates, cache=seed)
        not_cached = bootstrapper._contingency_table(paths, seed, candidates)
        self.assertEqual(cached, not_cached)

    def test_contingency_table_seed_candidates_cached(self):
        """
        Test that when both `seed` and `candidates` are cached, their document frequencies are created immediately.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'CRYCHE-100.json')

        seed, candidates = 'x', 'y'
        bootstrapper = ChiBootstrapper()
        table = bootstrapper._contingency_table(path, seed, candidates, cache=[ seed, candidates ])
        self.assertTrue(table)

    def test_contingency_table_empty_timeline(self):
        """
        Test that when creating the contingency table of an empty timeline results in all zeroes.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'empty.json')
        bootstrapper = ChiBootstrapper()
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, 'a', 'b')
        self.assertEqual(0, sum(tables[('a', 'b')]))

    def test_contingency_table_single_timeline(self):
        """
        Test that when creating the contingency table from a single timeline, the total of each contingency table adds up to the total number of documents in that timeline.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, 'a', 'b')
        self.assertEqual(ate.total_documents(path), sum(tables[('a', 'b')]))

    def test_contingency_table_multiple_timelines(self):
        """
        Test that when creating the contingency table from multiple timelines, the total of each contingency table adds up to the total number of documents in all timelines.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
                  os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json') ]
        total = ate.total_documents(paths)
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, 'a', 'b')
        self.assertEqual(total, sum(tables[('a', 'b')]))

    def test_contingency_table_timeline_str_seed(self):
        """
        Test that when creating the contingency table from a timeline with one `seed`, the contingency table treats it correctly as a string.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, 'yellow', [ 'foul', 'tackl' ])
        self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl') }, tables.keys())

    def test_contingency_table_timeline_str_candidates(self):
        """
        Test that when creating the contingency table from a timeline with one `candidates`, the contingency table treats it correctly as a string.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], 'yellow')
        self.assertEqual({ ('foul', 'yellow'), ('tackl', 'yellow') }, tables.keys())

    def test_contingency_table_timeline_list_seed(self):
        """
        Test that when creating the contingency table from a timeline with multiple `seed`, the contingency table treats it correctly as a list.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, [ 'yellow', 'red' ], [ 'foul', 'tackl' ])
        self.assertEqual({ ('yellow', 'foul'), ('yellow', 'tackl'),
                           ('red', 'foul'), ('red', 'tackl') },
                         tables.keys())

    def test_contingency_table_timeline_list_candidates(self):
        """
        Test that when creating the contingency table from a timeline with multiple `candidates`, the contingency table treats it correctly as a list.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
        self.assertEqual({ ('foul', 'yellow'), ('foul', 'red'),
                           ('tackl', 'yellow'), ('tackl', 'red') },
                         tables.keys())

    def test_contingency_table_timeline_token_not_found(self):
        """
        Test that even if a token is not found in a timeline, a contingency table is created for it.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')
        total = ate.total_documents(path)
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(path, [ 'foul', 'tackl' ], [ 'superlongword' ])
        self.assertEqual({ ('foul', 'superlongword'), ('tackl', 'superlongword') },
                         tables.keys())
        self.assertTrue(all( total == sum(table) for table in tables.values() ))

    def test_contingency_table_timeline_row_total(self):
        """
        Test that the row totals are correct when using timelines.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json') ]
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], 'yellow')
        counts = { token: len(probability.cached(paths, token)) for token in [ 'foul', 'tackl' ] }
        for pair, table in tables.items():
            expected = counts['foul'] if 'foul' in pair else counts['tackl']
            self.assertEqual(expected, table[0] + table[1])

    def test_contingency_table_timeline_column_total(self):
        """
        Test that the column totals are correct when using timelines.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json') ]
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
        counts = { token: len(probability.cached(paths, token)) for token in [ 'yellow', 'red' ] }
        for pair, table in tables.items():
            expected = counts['yellow'] if 'yellow' in pair else counts['red']
            self.assertEqual(expected, table[0] + table[2])

    def test_contingency_table_timeline_totals(self):
        """
        Test that the contingency table totals add up to the number of documents in the timelines.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json') ]
        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, [ 'foul', 'tackl' ], [ 'yellow', 'red' ])
        total = ate.total_documents(paths)
        self.assertTrue(all( total == sum(table) for table in tables.values() ))

    def test_contingency_table_timeline_joint_count(self):
        """
        Test that the joint counts are correct when using timelines.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json') ]

        seed, candidates = [ 'foul', 'tackl' ], 'yellow'
        freq = dict.fromkeys(probability.joint_vocabulary(seed, candidates), 0)
        for corpus in paths:
            with open(corpus, 'r') as f:
                timeline = Exportable.decode(json.loads(f.readline()))['timeline']
                documents = [ document for node in timeline.nodes for document in node.get_all_documents() ]
                for document in documents:
                    for pair in freq:
                        if pair[0] in document.dimensions and pair[1] in document.dimensions:
                            freq[pair] += 1

        bootstrapper = ChiBootstrapper()
        tables = bootstrapper._contingency_table(paths, seed, candidates)
        for pair in tables:
            self.assertEqual(freq[pair], tables[pair][0])

    def test_contingency_table_timeline_symmetric(self):
        """
        Test that the contingency table is symmetric, but otherwise all counts are the same when using timelines.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json') ]

        seed, candidates = [ 'foul', 'tackl' ], 'yellow'
        bootstrapper = ChiBootstrapper()
        t1, t2 = bootstrapper._contingency_table(paths, seed, candidates), bootstrapper._contingency_table(paths, candidates, seed)
        for t1, t2 in zip(t1.values(), t2.values()):
            self.assertEqual(t1[0], t2[0])
            self.assertEqual(t1[1], t2[2])
            self.assertEqual(t1[2], t2[1])
            self.assertEqual(t1[3], t2[3])

    def test_contingency_table_timeline_cache(self):
        """
        Test that the contingency table's cache results in the same table as without cache when using timelines.
        """

        paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json'),
                   os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'LIVMUN.json') ]

        seed, candidates = [ 'yellow', 'red' ], [ 'foul', 'tackl' ]
        bootstrapper = ChiBootstrapper()
        cached = bootstrapper._contingency_table(paths, seed, candidates, cache=seed)
        not_cached = bootstrapper._contingency_table(paths, seed, candidates)
        self.assertEqual(cached, not_cached)

    def test_contingency_table_timeline_seed_candidates_cached(self):
        """
        Test that when both `seed` and `candidates` are cached, their document frequencies are created immediately when using timelines.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'timelines', 'CRYCHE.json')

        seed, candidates = 'x', 'y'
        bootstrapper = ChiBootstrapper()
        table = bootstrapper._contingency_table(path, seed, candidates, cache=[ seed, candidates ])
        self.assertTrue(table)

    def test_contingency_table_example(self):
        """
        Test the creation of a contingency table from an example corpus.
        """

        path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tests', 'corpora', 'tokenized', 'example-1.json')

        seed, candidates = 'x', '!y'
        bootstrapper = ChiBootstrapper()
        table = list(bootstrapper._contingency_table(path, seed, candidates).values())[0]
        self.assertEqual(3, table[0])
        self.assertEqual(1, table[1])
        self.assertEqual(2, table[2])
        self.assertEqual(14, table[3])

    def test_chi(self):
        """
        Test the chi-square calculation.
        """

        bootstrapper = ChiBootstrapper()

        table = (600, 200, 300, 1000)
        self.assertEqual(545.1923, round(bootstrapper._chi(table), 4))

        table = (30, 20, 331, 3218)
        self.assertEqual(140.2925, round(bootstrapper._chi(table), 4))

    def test_chi_empty(self):
        """
        Test that the chi-square statistic of an empty table is 0.
        """

        bootstrapper = ChiBootstrapper()

        table = (0, 0, 0, 0)
        self.assertEqual(0, bootstrapper._chi(table))

    def test_chi_empty_combinations(self):
        """
        Test that the chi-square statistic of a table that is not empty, except for a few combinations, is 0.
        """

        bootstrapper = ChiBootstrapper()

        table = (0, 1, 0, 1) # A + C = 0
        self.assertEqual(0, bootstrapper._chi(table))

        table = (1, 0, 1, 0) # B + D = 0
        self.assertEqual(0, bootstrapper._chi(table))

        table = (0, 0, 1, 1) # A + B = 0
        self.assertEqual(0, bootstrapper._chi(table))

        table = (1, 1, 0, 0) # C + D = 0
        self.assertEqual(0, bootstrapper._chi(table))

        table = (1, 0, 0, 1) # B + C = 0
        self.assertLess(0, bootstrapper._chi(table))

        table = (0, 1, 1, 0) # A + D = 0
        self.assertLess(0, bootstrapper._chi(table))
