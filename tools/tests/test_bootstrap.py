"""
Test the functionality of the bootstrap tool.
"""

import json
import math
import os
import statistics
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import bootstrap
from eventdt.ate.bootstrapping.probability import PMIBootstrapper
from logger import logger

logger.set_logging_level(logger.LogLevel.ERROR)

class TestBootstrap(unittest.TestCase):
    """
    Test the functionality of the bootstrap tool.
    """

    def test_bootstrap_list(self):
        """
        Test that bootstrapping returns a list of keywords.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        candidates = bootstrap.generate_candidates(files, generate=200)

        bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 1, 5, max, candidates)
        self.assertEqual(list, type(bootstrapped))

    def test_bootstrap_iterations(self):
        """
        Test that bootstrapping repeats for a number of iterations.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        candidates = bootstrap.generate_candidates(files, generate=200)

        bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 1, 1, max, candidates)
        self.assertEqual(1, len(bootstrapped))
        bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 2, 1, max, candidates)
        self.assertEqual(2, len(bootstrapped))

    def test_bootstrap_keep(self):
        """
        Test that bootstrapping keeps only a number of terms at each iteration
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        candidates = bootstrap.generate_candidates(files, generate=200)

        bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 1, 2, max, candidates)
        self.assertEqual(2, len(bootstrapped))
        bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 2, 2, max, candidates)
        self.assertEqual(4, len(bootstrapped))

    def test_bootstrap_unique(self):
        """
        Test that bootstrapping returns a unique list of terms.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        candidates = bootstrap.generate_candidates(files, generate=200)

        bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 2, 5, max, candidates)
        self.assertEqual(sorted(list(set(bootstrapped))), sorted(bootstrapped))

    def test_bootstrap(self):
        """
        Test that bootstrapping results make sense.
        """

        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json') ]
        candidates = bootstrap.generate_candidates(files, generate=200)

        bootstrapped = bootstrap.bootstrap(files, [ 'half' ], PMIBootstrapper, 1, 5, max, candidates)
        self.assertTrue('second' in bootstrapped)
        self.assertTrue('first' in bootstrapped)

    def test_load_seed_all_words(self):
        """
        Test that when loading the seed words, all words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)

        """
        Assert that the correct number of seed words are loaded.
        """
        self.assertEqual(30, len(seed))

        """
        Load each seed set separately and ensure it has been loaded.
        """
        with open(file, 'r') as f:
            for word in f:
                self.assertTrue(word.strip() in seed)

    def test_load_seed_list(self):
        """
        Test that when loading the seed words, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)

        """
        Assert that the seed list is returned as a list.
        """
        self.assertEqual(list, type(seed))

    def test_load_seed_from_terms(self):
        """
        Test that when loading the seed words from the terms tool's output, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        seed = bootstrap.load_seed(file)

        """
        Assert that the seed list is returned as a list.
        """
        self.assertEqual(list, type(seed))
        self.assertTrue(len(seed))

    def test_load_seed_no_newlines(self):
        """
        Test that when loading the seed words, the newline symbol is removed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)

        """
        Assert that the seed list is returned as a list.
        """
        self.assertTrue(all( '\n' not in word for word in seed ))

    def test_load_seed_max_seed_zero(self):
        """
        Test that when loading the seed words and keeping zero words, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        self.assertRaises(ValueError, bootstrap.load_seed, file, 0)

    def test_load_seed_max_seed_negative(self):
        """
        Test that when loading the seed words and keeping negative words, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        self.assertRaises(ValueError, bootstrap.load_seed, file, -1)

    def test_load_seed_max_seed_respected(self):
        """
        Test that when loading the seed words, the specified number of words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file, 10)
        self.assertEqual(10, len(seed))

    def test_load_seed_max_seed_top_words(self):
        """
        Test that when loading the seed words with a cutoff, the top words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        all = bootstrap.load_seed(file)
        seed = bootstrap.load_seed(file, 10)
        self.assertEqual(all[:10], seed)

    def test_load_seed_max_seed_very_large(self):
        """
        Test that when loading the seed words with a large cutoff, all words are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file, 50)
        self.assertEqual(30, len(seed))

    def test_load_seed_max_seed_none(self):
        """
        Test that when loading the seed words with no specified cutoff, all words are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file, None)
        self.assertEqual(30, len(seed))

    def test_load_seed_empty(self):
        """
        Test that when the seed file is empty, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'empty.txt')
        self.assertRaises(ValueError, bootstrap.load_seed, file)

    def test_load_candidates_all_words(self):
        """
        Test that when loading the candidates words, all words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        candidates = bootstrap.load_candidates(file)

        """
        Assert that the correct number of candidates words are loaded.
        """
        self.assertEqual(500, len(candidates))

        """
        Load each candidates set separately and ensure it has been loaded.
        """
        with open(file, 'r') as f:
            for word in f:
                self.assertTrue(word.strip() in candidates)

    def test_load_candidates_list(self):
        """
        Test that when loading the candidates words, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        candidates = bootstrap.load_candidates(file)

        """
        Assert that the candidates list is returned as a list.
        """
        self.assertEqual(list, type(candidates))

    def test_load_candidates_from_terms(self):
        """
        Test that when loading the candidate words from the terms tool's output, they are returned as a list.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.json')
        candidates = bootstrap.load_candidates(file)

        """
        Assert that the candidates list is returned as a list.
        """
        self.assertEqual(list, type(candidates))
        self.assertTrue(len(candidates))

    def test_load_candidates_no_newlines(self):
        """
        Test that when loading the candidates words, the newline symbol is removed.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        candidates = bootstrap.load_candidates(file)

        """
        Assert that the candidates list is returned as a list.
        """
        self.assertTrue(all( '\n' not in word for word in candidates ))

    def test_load_candidates_max_candidates_zero(self):
        """
        Test that when loading the candidates words and keeping zero words, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        self.assertRaises(ValueError, bootstrap.load_candidates, file, 0)

    def test_load_candidates_max_candidates_negative(self):
        """
        Test that when loading the candidates words and keeping negative words, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        self.assertRaises(ValueError, bootstrap.load_candidates, file, -1)

    def test_load_candidates_max_candidates_respected(self):
        """
        Test that when loading the candidates words, the specified number of words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        candidates = bootstrap.load_candidates(file, 10)
        self.assertEqual(10, len(candidates))

    def test_load_candidates_max_candidates_top_words(self):
        """
        Test that when loading the candidates words with a cutoff, the top words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        all = bootstrap.load_candidates(file)
        candidates = bootstrap.load_candidates(file, 10)
        self.assertEqual(all[:10], candidates)

    def test_load_candidates_max_candidates_very_large(self):
        """
        Test that when loading the candidates words with a large cutoff, all words are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        candidates = bootstrap.load_candidates(file, 600)
        self.assertEqual(500, len(candidates))

    def test_load_candidates_max_candidates_none(self):
        """
        Test that when loading the seed words with no specified cutoff, all words are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'candidates.txt')
        candidates = bootstrap.load_candidates(file, None)
        self.assertEqual(500, len(candidates))

    def test_load_candidates_empty(self):
        """
        Test that when the candidates file is empty, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'empty.txt')
        self.assertRaises(ValueError, bootstrap.load_candidates, file)

    def test_generate_candidates_cutoff(self):
        """
        Test that when generating candidates, the cutoff is respected.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

        """
        Assert that the number of candidates is correct.
        """
        candidates = bootstrap.generate_candidates(file, generate=100)
        self.assertEqual(100, len(candidates))

        candidates = bootstrap.generate_candidates(file, generate=250)
        self.assertEqual(250, len(candidates))

    def test_generate_candidates_words_only(self):
        """
        Test that when generating candidates, only words are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

        """
        Assert that all items in the list are words.
        """
        candidates = bootstrap.generate_candidates(file, generate=100)
        self.assertEqual(list, type(candidates))
        self.assertTrue(all(str == type(word) for word in candidates))

    def test_generate_candidates(self):
        """
        Test that when generating candidates, the returned candidates make sense
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', 'CRYCHE.json')

        """
        Assert that all items in the list are words.
        """
        candidates = bootstrap.generate_candidates(file, generate=500)
        self.assertTrue('goal' in candidates)

    def test_filter_candidates_empty_seed_bootstrapped(self):
        """
        Test that when empty seed set and bootstrapped keywords are given, the original dictionary is returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)
        candidates = { word: i for i, word in enumerate(seed) }

        self.assertEqual(candidates, bootstrap.filter_candidates(candidates, [ ], [ ]))

    def test_filter_candidates_copy(self):
        """
        Test that the filtered candidate dictionary is a copy.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)
        candidates = { word: i for i, word in enumerate(seed) }

        filtered = bootstrap.filter_candidates(candidates, seed, [ ])
        self.assertEqual(30, len(candidates))
        self.assertEqual(0, len(filtered))

    def test_filter_candidates_all(self):
        """
        Test that when all candidates are filtered, an empty dictionary is returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)
        candidates = { word: i for i, word in enumerate(seed) }

        filtered = bootstrap.filter_candidates(candidates, seed, [ ])
        self.assertEqual({ }, filtered)

    def test_filter_candidates_seed(self):
        """
        Test filtering by the seed set.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)
        candidates = { word: i for i, word in enumerate(seed) }

        filtered = bootstrap.filter_candidates(candidates, seed[:10], [ ])
        self.assertTrue(all( word not in filtered for word in seed[:10] ))

    def test_filter_candidates_bootstrapped(self):
        """
        Test filtering by the bootstrapped keywords.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)
        candidates = { word: i for i, word in enumerate(seed) }

        filtered = bootstrap.filter_candidates(candidates, [ ], seed[:10])
        self.assertTrue(all( word not in filtered for word in seed[:10] ))

    def test_filter_candidates_combination(self):
        """
        Test filtering by the seed set and bootstrapped keywords.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)
        candidates = { word: i for i, word in enumerate(seed) }

        filtered = bootstrap.filter_candidates(candidates, seed[:10], seed[10:20])
        self.assertTrue(all( word not in filtered for word in seed[:20] ))

    def test_filter_candidates_scores_retained(self):
        """
        Test that when filtering candidates, the scores are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.txt')
        seed = bootstrap.load_seed(file)
        candidates = { word: i for i, word in enumerate(seed) }

        filtered = bootstrap.filter_candidates(candidates, seed[:10], [ ])
        for i, word in enumerate(seed[10:]):
            self.assertEqual(i + 10, filtered[word])

    def test_choose_next_empty(self):
        """
        Test that when choosing the next seed terms and there are no scores, an empty list is returned.
        """

        scores = { }
        self.assertEqual([ ], bootstrap.choose_next(scores, 10))

    def test_choose_next_list(self):
        """
        Test that when choosing the next seed terms, a list of tuples is returned, and that each first element is a string and each second element is a floating number.
        """

        scores = { 'second': { 'half': 10 }, 'first': { 'half': 2 } }
        next_seed = bootstrap.choose_next(scores, 10)
        self.assertEqual(list, type(next_seed))
        self.assertTrue(all( type(seed) is tuple for seed in next_seed ))
        self.assertTrue(all( type(seed[0]) is str for seed in next_seed ))
        self.assertTrue(all( type(seed[1]) is float or type(seed[1]) is int for seed in next_seed ))

    def test_choose_next_copy(self):
        """
        Test that when choosing the next seed terms, the original scores dictionary does not change.
        """

        scores = { 'second': { 'half': 10 }, 'first': { 'half': 2 } }
        next_seed = bootstrap.choose_next(scores, 10)
        self.assertEqual(set([ 'second', 'first' ]), set(scores.keys()))

    def test_choose_next_all(self):
        """
        Test that when choosing the next seed terms and there are few terms relative to how many should be kept, all are returned.
        """

        scores = { 'second': { 'half': 10 }, 'first': { 'half': 2 } }
        next_seed = bootstrap.choose_next(scores, 10)
        terms = [ term for term, _ in next_seed ]
        self.assertEqual(set(scores.keys()), set(terms))

    def test_choose_next_keep_inclusive(self):
        """
        Test that when choosing the next seed terms, the ``keep`` parameter is inclusive.
        """

        scores = { 'second': { 'half': 10 }, 'first': { 'half': 2 }, 'third': { 'half': 4 } }
        next_seed = bootstrap.choose_next(scores, 3)
        terms = [ term for term, _ in next_seed ]
        self.assertEqual(set(scores.keys()), set(terms))

    def test_choose_next_highest(self):
        """
        Test that when choosing the next seed terms, the ones with the highest scores are retained.
        """

        keep = 2
        scores = { 'second': { 'half': 10 }, 'first': { 'half': 2 }, 'third': { 'half': 4 } }
        next_seed = bootstrap.choose_next(scores, keep)
        terms = [ term for term, _ in next_seed ]
        self.assertEqual([ 'second', 'third' ], terms)

    def test_choose_next_sorted_scores(self):
        """
        Test that when choosing the next seed terms, the terms are sorted in descending order of score.
        """

        keep = 2
        scores = { 'second': { 'half': 10 }, 'first': { 'half': 2 }, 'third': { 'half': 4 } }
        next_seed = bootstrap.choose_next(scores, keep)
        self.assertTrue(all( next_seed[i][1] >= next_seed[i + 1][1] for i in range(len(next_seed) - 1) ))

    def test_choose_next_highest_mean(self):
        """
        Test that when choosing the next seed terms with the highest mean, the maximum score is not used.
        """

        scores = { 'yellow': { 'card': 10, 'tackl': 8 }, 'red': { 'card': 11, 'tackl': 5 } }
        next_seed = bootstrap.choose_next(scores, 1, choose=max) # using the maximum score
        terms = [ term for term, _ in next_seed ]
        self.assertEqual([ 'red' ], terms)

        next_seed = bootstrap.choose_next(scores, 1, choose=statistics.mean) # using the mean score
        terms = [ term for term, _ in next_seed ]
        self.assertEqual([ 'yellow' ], terms)

    def test_choose_next_wmean_order_matters(self):
        """
        Test that when choosing the next seed terms with the highest mean, the order of the previously-bootstrapped (or seed) terms matters.
        """

        scores = { 'yellow': { 'card': 10, 'tackl': 8 }, 'red': { 'card': 8, 'tackl': 10 } }
        next_seed = bootstrap.choose_next(scores, 1, choose=bootstrap.wmean, bootstrapped=[ 'card', 'tackl' ]) # using the maximum score
        terms = [ term for term, _ in next_seed ]
        self.assertEqual([ 'yellow' ], terms)

        next_seed = bootstrap.choose_next(scores, 1, choose=bootstrap.wmean, bootstrapped=[ 'tackl', 'card' ]) # using the maximum score
        terms = [ term for term, _ in next_seed ]
        self.assertEqual([ 'red' ], terms)

    def test_wmean_correct_score(self):
        """
        Test that the weighted mean assigns the correct score.
        """

        scores = { 'card': 10, 'tackl': 8 }
        bootstrapped = [ 'card', 'tackl' ]
        self.assertEqual(sum(scores[term] * math.exp(-( bootstrapped.index(term) + 1 )) for term in scores), bootstrap.wmean(scores, bootstrapped))

        scores = { 'card': 10, 'tackl': 8 }
        bootstrapped = [ 'tackl', 'card' ]
        self.assertEqual(sum(scores[term] * math.exp(-( bootstrapped.index(term) + 1 )) for term in scores), bootstrap.wmean(scores, bootstrapped))

    def test_wmean_lambda(self):
        """
        Test that the weighted mean uses the lambda parameter to assign the correct score.
        """

        scores = { 'card': 10, 'tackl': 8 }
        bootstrapped = [ 'card', 'tackl' ]
        l = 0.5
        self.assertEqual(sum(scores[term] * l * math.exp(-l * ( bootstrapped.index(term) + 1 )) for term in scores), bootstrap.wmean(scores, bootstrapped, l=l))

    def test_wmean_drift(self):
        """
        Test that the the smaller the lambda value, the more semantic drift is allowed.
        """

        scores = { 'yellow': { 'card': 10, 'tackl': 8 }, 'red': { 'card': 8, 'tackl': 10 } }
        bootstrapped = [ 'card', 'tackl' ]

        l = 0.1
        low_l = bootstrap.wmean(scores['yellow'], bootstrapped, l=l)/bootstrap.wmean(scores['red'], bootstrapped, l=l)

        l = 10
        high_l = bootstrap.wmean(scores['yellow'], bootstrapped, l=l)/bootstrap.wmean(scores['red'], bootstrapped, l=l)

        self.assertGreater(high_l, low_l) # there is a bigger ratio between the two terms when lambda is bigger

    def test_wmean_lambda_order(self):
        """
        Test that the lambda value affects the order of the terms.
        """

        scores = { 'yellow': { 'card': 10, 'tackl': 8, 'foul': 2 }, 'red': { 'card': 8, 'tackl': 10, 'foul': 10 } }
        bootstrapped = [ 'card', 'tackl', 'foul' ]

        l = 0.1
        self.assertLess(bootstrap.wmean(scores['yellow'], bootstrapped, l=l), bootstrap.wmean(scores['red'], bootstrapped, l=l))

        l = 10
        self.assertGreater(bootstrap.wmean(scores['yellow'], bootstrapped, l=l), bootstrap.wmean(scores['red'], bootstrapped, l=l))

    def test_update_scores_lower(self):
        """
        Test that when updating the scores, lower scores are kept, but new keys are added.
        """

        candidates = { 'ff': { 'fuck': 2 } }
        scores = { ('goal', 'ff'): 1 }
        self.assertEqual({ 'ff': { 'fuck': 2, 'goal': 1 } }, bootstrap.update_scores(candidates, scores))

    def test_update_scores_higher(self):
        """
        Test that when updating the scores, higher scores are kept, but as new keys.
        """

        candidates = { 'ff': { 'fuck': 2 } }
        scores = { ('goal', 'ff'): 3 }
        self.assertEqual({ 'ff': { 'fuck': 2, 'goal': 3 } }, bootstrap.update_scores(candidates, scores))

    def test_update_scores_same(self):
        """
        Test that when updating the scores, scores where the seed and candidate words are the same are ignored.
        """

        candidates = { 'ff': { 'ff': 2 } }
        scores = { ('ff', 'ff'): 3 }
        self.assertEqual(candidates, bootstrap.update_scores(candidates, scores))

    def test_update_scores_missing_candidate(self):
        """
        Test that when updating the scores, new terms are added to the candidate list.
        """

        candidates = { 'ff': { 'fuck': 2 } }
        scores = { ('goal', 'wtf'): 3 }
        self.assertEqual({ 'ff': { 'fuck': 2 }, 'wtf': { 'goal': 3 } }, bootstrap.update_scores(candidates, scores))

    def test_update_scores_missing_score(self):
        """
        Test that when updating the scores, existing terms without a new score are not touched.
        """

        candidates = { 'ff': { 'fuck': 2 } }
        scores = { ('goal', 'wtf'): 3 }
        self.assertEqual({ 'ff': { 'fuck': 2 }, 'wtf': { 'goal': 3 } }, bootstrap.update_scores(candidates, scores))

    def test_update_scores_seed_inner(self):
        """
        Test that when updating the scores, the seed term, which gives a score for the candidates, is the inner key of the candidate's score.
        """

        candidates = {  }
        seed, candidate, score = 'goal', 'wtf', 3
        scores = { (seed, candidate): score }
        updated = bootstrap.update_scores(candidates, scores)
        self.assertEqual({ candidate }, set(updated.keys()))
        self.assertEqual({ seed }, set(updated[candidate].keys()))
        self.assertEqual(score, updated[candidate][seed])

    def test_update_scores_empty_candidates(self):
        """
        Test that when updating the scores of no candidates, the new scores are returned.
        """

        candidates = { }
        scores = { ('goal', 'wtf'): 3 }
        self.assertEqual({ 'wtf': { 'goal': 3 } }, bootstrap.update_scores(candidates, scores))

    def test_update_scores_empty_scores(self):
        """
        Test that when updating the scores with no scores, the candidates are returned.
        """

        candidates = { 'ff': 2 }
        scores = { }
        self.assertEqual(candidates, bootstrap.update_scores(candidates, scores))

    def test_update_scores_copy(self):
        """
        Test that when updating the scores, the original candidates are not changed.
        """

        candidates = { 'ff': { 'fuck': 2} }
        scores = { ('goal', 'ff'): 3 }
        updated = bootstrap.update_scores(candidates, scores)
        self.assertEqual({ 'ff': { 'fuck': 2 } }, candidates)
        self.assertEqual({ 'ff': { 'fuck': 2, 'goal': 3 } }, updated)

    def test_update_scores_same_score_keys(self):
        """
        Test that when updating the scores, all candidates should have the same keys.
        """

        candidates = { 'yellow': { 'card': 10 }, 'red': { 'card': 3 } }
        scores = { ('tackl', 'yellow'): 5, ('tackl', 'red'): 3 }
        updated = bootstrap.update_scores(candidates, scores)
        self.assertEqual({ 'card', 'tackl' }, set(updated['yellow'].keys()))
        self.assertEqual(set(updated['red'].keys()), set(updated['yellow'].keys()))
