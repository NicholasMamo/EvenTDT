"""
Test the functionality of the terms tool.
"""

import json
import math
import os
import re
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from tools import terms
from ate.application import LogEF, EF, EFIDF, EFIDFEntropy, Entropy

class TestTerms(unittest.TestCase):
    """
    Test the functionality of the terms tool.
    """

    def test_extract_logef(self):
        """
        Test the LogEF extractor results.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(LogEF)
        extracted = terms.extract(extractor, files)
        term = [ term for term in extracted if term['term'] == 'kepa' ][0]
        self.assertEqual(0, term['score'])

    def test_extract_logef_less_than_equal_events(self):
        """
        Test that when creating a LogEF extractor, the maximum score cannot be larger than the log of the number of events.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(LogEF)
        extracted = terms.extract(extractor, files)
        self.assertTrue(all( term['score'] <= math.log(len(events), 2) for term in extracted ))
        self.assertTrue(any( term['score'] == math.log(len(events), 2) for term in extracted ))

    def test_extract_logef_zero_scores(self):
        """
        Test that when creating a LogEF extractor, terms that appear only once have a score of 0.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted_ef = terms.extract(extractor, files)
        once = [ term['term'] for term in extracted_ef if term['score'] == 1 ]

        extractor = terms.create_extractor(LogEF)
        extracted_logef = terms.extract(extractor, files)
        zero = [ term['term'] for term in extracted_logef if term['score'] == 0 ]
        self.assertEqual(set(once), set(zero))

    def test_extract_logef_same_ranking_as_ef(self):
        """
        Test that the ranking of the LogEF is the same as the EF's.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted_ef = terms.extract(extractor, files)
        terms_ef = [ term['term'] for term in extracted_ef ]

        extractor = terms.create_extractor(LogEF)
        extracted_logef = terms.extract(extractor, files)
        terms_logef = [ term['term'] for term in extracted_logef ]
        self.assertEqual(terms_ef, terms_logef)

    def test_extract_logef_uses_log(self):
        """
        Test that the scores of the LogEF are the same as the EF's, but with a logarithm.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted_ef = terms.extract(extractor, files)
        terms_ef = [ term['score'] for term in extracted_ef ]

        extractor = terms.create_extractor(LogEF)
        extracted_logef = terms.extract(extractor, files)
        terms_logef = [ term['score'] for term in extracted_logef ]
        self.assertTrue(all( logef == math.log(ef, 2) for (ef, logef) in zip(terms_ef, terms_logef) ))

    def test_extract_logef_base(self):
        """
        Test that the LogEF extractor uses the base when given.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted_ef = terms.extract(extractor, files)
        terms_ef = [ term['score'] for term in extracted_ef ]

        extractor = terms.create_extractor(LogEF, base=2)
        extracted_logef = terms.extract(extractor, files)
        terms_2 = [ term['score'] for term in extracted_logef ]
        self.assertTrue(all( logef == math.log(ef, 2) for (ef, logef) in zip(terms_ef, terms_2) ))

        # pass on a different base
        extractor = terms.create_extractor(LogEF, base=10)
        extracted_logef = terms.extract(extractor, files)
        terms_10 = [ term['score'] for term in extracted_logef ]
        self.assertTrue(all( logef == math.log(ef, 10) for (ef, logef) in zip(terms_ef, terms_10) ))

        # check that the term scores go down when the logarithmic base goes up
        self.assertTrue(all( score_10 < score_2 or (score_10 == 0 and score_2 == 0) for (score_10, score_2) in zip(terms_10, terms_2) ))

    def test_extract_logef_base_does_not_affect_ranking(self):
        """
        Test that changing the base of the LogEF extractor does not change the ranking.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(LogEF, base=2)
        extracted_logef = terms.extract(extractor, files)
        terms_2 = [ term['term'] for term in extracted_logef ]

        extractor = terms.create_extractor(LogEF, base=10)
        extracted_logef = terms.extract(extractor, files)
        terms_10 = [ term['term'] for term in extracted_logef ]
        self.assertEqual(terms_2, terms_10)

    def test_extract_ef(self):
        """
        Test the EF extractor results.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, files)
        term = [ term for term in extracted if term['term'] == 'kepa' ][0]
        self.assertEqual(1, term['score'])

    def test_extract_ef_less_than_equal_events(self):
        """
        Test that when creating an EF extractor, the maximum score cannot be larger than the number of events.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, files)
        self.assertTrue(all( term['score'] <= len(events) for term in extracted ))
        self.assertTrue(any( term['score'] == len(events) for term in extracted ))

    def test_extract_ef_positive_scores(self):
        """
        Test that when creating an EF extractor, the scores are all positive.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, files)
        self.assertTrue(any( term['score'] > 0 for term in extracted ))

    def test_create_extractor_efidf_missing_idf(self):
        """
        Test that when the TF-IDF scheme is not given for the EF-IDF, a SystemExit is raised.
        """

        self.assertRaises(SystemExit, terms.create_extractor, EFIDF)

    def test_extract_efidf_with_incorrect_corpora(self):
        """
        Test that when the EF-IDF receives incorrect corpus types, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', 'LIVMUN.json')
        extractor = terms.create_extractor(EFIDF, tfidf=idf)
        self.assertRaises(ValueError, extractor.extract, path)

    def test_extract_efidf_results(self):
        """
        Test that when extracting terms using EF-IDF, the correct results are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, files)
        self.assertEqual([ 'offsid', 'alisson', 'foul', 'tackl', 'goalkeep' ],
                         list( term['term'] for term in extracted[:5] ))
        self.assertEqual(9.764345, round(extracted[0]['score'], 6))
        self.assertEqual(8.971401, round(extracted[1]['score'], 6))
        self.assertEqual(7.749988, round(extracted[2]['score'], 6))
        self.assertEqual(7.461810, round(extracted[3]['score'], 6))
        self.assertEqual(7.205842, round(extracted[4]['score'], 6))

    def test_extract_efidf_results_without_base(self):
        """
        Test that when extracting terms using EF-IDF without a base, the correct results are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf)
        extracted = terms.extract(extractor, files)
        self.assertEqual([ 'offsid', 'alisson', 'foul', 'tackl', 'goalkeep' ],
                         list( term['term'] for term in extracted[:5] ))
        self.assertEqual(19.528690, round(extracted[0]['score'], 6))
        self.assertEqual(16.980971, round(extracted[1]['score'], 6))
        self.assertEqual(15.499975, round(extracted[2]['score'], 6))
        self.assertEqual(14.923619, round(extracted[3]['score'], 6))
        self.assertEqual(13.639141, round(extracted[4]['score'], 6))

    def test_create_extractor_efidfentropy_missing_idf(self):
        """
        Test that when the TF-IDF scheme is not given to the EF-IDF-Entropy extractor, a SystemExit is raised.
        """

        self.assertRaises(SystemExit, terms.create_extractor, EFIDFEntropy)

    def test_extract_efidfentropy_with_incorrect_corpora(self):
        """
        Test that when the EF-IDF-Entropy extractor receives incorrect corpus types, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', 'LIVMUN.json')
        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf)
        self.assertRaises(ValueError, extractor.extract, path, path)

    def test_extract_efidfentropy_with_unequal_corpora(self):
        """
        Test that when the EF-IDF-Entropy extractor receives a different number of timelines and IDFs, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events[:len(events) - 1] ]
        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf)
        self.assertRaises(ValueError, extractor.extract, timelines, idfs=idfs)

    def test_extract_efidfentropy_results(self):
        """
        Test the results of EF-IDF-Entropy 'manually' by computing EF-IDF and Entropy separately.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EFIDF, tfidf=idf, base=2)
        terms_efidf = terms.extract(extractor, timelines)
        terms_efidf = { term['term']: term['score'] for term in terms_efidf }

        extractor = Entropy(base=2)
        terms_entropy = extractor.extract(idfs)

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        terms_efidf_entropy = terms.extract(extractor, timelines, idfs=idfs)
        self.assertTrue(all( term['score'] == terms_efidf[term['term']] * terms_entropy.get(term['term'], 0) for term in terms_efidf_entropy ))

    def test_extract_efidfentropy_results_base_same_order(self):
        """
        Test that when extracting terms using EF-IDF-Entropy with different bases, the same ranking is returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=10)
        terms_nolog = terms.extract(extractor, timelines, idfs=idfs)
        terms_nolog = [ term['term'] for term in terms_nolog ]

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        terms_log = terms.extract(extractor, timelines, idfs=idfs)
        terms_log = [ term['term'] for term in terms_log ]
        self.assertEqual(terms_log, terms_nolog)

    def test_extract_ranks_ascending(self):
        """
        Test that when extracting terms, the ranks are in ascending order.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf)
        extracted = terms.extract(extractor, files)
        for i in range(0, len(extracted) - 1):
            self.assertLess(extracted[i]['rank'], extracted[i + 1]['rank'])

    def test_extract_scores_descending(self):
        """
        Test that when extracting terms, the scores are in descending order.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf)
        extracted = terms.extract(extractor, files)
        for i in range(0, len(extracted) - 1):
            self.assertGreaterEqual(extracted[i]['score'], extracted[i + 1]['score'])
