"""
Test the functionality of the terms tool.
"""

import json
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
from ate.application import EF, EFIDF, Variability, Entropy

class TestTerms(unittest.TestCase):
    """
    Test the functionality of the terms tool.
    """

    def test_create_extractor_ef(self):
        """
        Test that the EF extractor results.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, files)
        term = [ term for term in extracted if term['term'] == 'kepa' ][0]
        self.assertEqual(1, term['score'])

    def test_create_extractor_ef_less_than_equal_events(self):
        """
        Test that when creating an EF extractor, the maximum score cannot be larger than the number of events.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, files)
        self.assertTrue(all( term['score'] <= len(events) for term in extracted ))
        self.assertTrue(any( term['score'] == len(events) for term in extracted ))

    def test_create_extractor_ef_positive_scores(self):
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

    def test_extract_efidf_with_corpora(self):
        """
        Test that when the EF-IDF receives corpora, it raises a ValueError.
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

    def test_rerank_ranks_ascending(self):
        """
        Test that when re-ranking terms, the ranks are in ascending order.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        reranker_files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, files)
        reranker = terms.create_reranker(Variability, base=2)
        reranked = terms.rerank(reranker, reranker_files, extracted)
        for i in range(0, len(reranked) - 1):
            self.assertLess(reranked[i]['rank'], reranked[i + 1]['rank'])

    def test_rerank_scores_descending(self):
        """
        Test that when reranking terms, the scores are in descending order.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        reranker_files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, files)
        reranker = terms.create_reranker(Variability, base=2)
        reranked = terms.rerank(reranker, reranker_files, extracted)
        for i in range(0, len(reranked) - 1):
            self.assertGreaterEqual(reranked[i]['score'], reranked[i + 1]['score'])

    def test_rerank_same_terms(self):
        """
        Test that when reranking terms, all original terms are retained.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        reranker_files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, files)
        reranker = terms.create_reranker(Variability, base=2)
        reranked = terms.rerank(reranker, reranker_files, extracted)

        extracted = sorted([ term['term'] for term in extracted ])
        reranked = sorted([ term['term'] for term in reranked ])
        self.assertEqual(extracted, reranked)

    def test_rerank_variability_results(self):
        """
        Test that when reranking terms using variability, the correct results are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        reranker_files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, files)
        self.assertEqual([ 'offsid', 'alisson', 'foul', 'tackl', 'goalkeep' ],
                         list( term['term'] for term in extracted[:5] ))
        reranker = terms.create_reranker(Variability, base=10)
        reranked = terms.rerank(reranker, reranker_files, extracted)
        self.assertEqual([ 'ye', 'ff', 'underway', 'foul', 'book' ],
                         list( term['term'] for term in reranked[:5] ))
        self.assertEqual(4.005837, round(reranked[0]['score'], 6))
        self.assertEqual(3.935372, round(reranked[1]['score'], 6))
        self.assertEqual(3.198017, round(reranked[2]['score'], 6))
        self.assertEqual(2.881923, round(reranked[3]['score'], 6))
        self.assertEqual(2.868199, round(reranked[4]['score'], 6))

    def test_rerank_entropy_results(self):
        """
        Test that when reranking terms using entropy, the correct results are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        reranker_files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(EFIDF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, files)
        self.assertEqual([ 'offsid', 'alisson', 'foul', 'tackl', 'goalkeep' ],
                         list( term['term'] for term in extracted[:5] ))
        reranker = terms.create_reranker(Entropy, base=10)
        reranked = terms.rerank(reranker, reranker_files, extracted)
        self.assertEqual([ 'offsid', 'foul', 'underway', 'tackl', 'david' ],
                         list( term['term'] for term in reranked[:5] ))
        self.assertEqual(4.635161, round(reranked[0]['score'], 6))
        self.assertEqual(4.005748, round(reranked[1]['score'], 6))
        self.assertEqual(3.930411, round(reranked[2]['score'], 6))
        self.assertEqual(3.726672, round(reranked[3]['score'], 6))
        self.assertEqual(3.530708, round(reranked[4]['score'], 6))

    def test_rerank_entropy_results_without_base(self):
        """
        Test that when reranking terms using entropy without a base, the correct results are returned.
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
