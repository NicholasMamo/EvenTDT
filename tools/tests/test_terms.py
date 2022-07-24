"""
Test the functionality of the terms tool.
"""

import copy
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
from ate.application import *
from ate.stat import TFExtractor, TFIDFExtractor

class TestTerms(unittest.TestCase):
    """
    Test the functionality of the terms tool.
    """

    def test_is_own_terms(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "sample.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertTrue(terms.isOwn(output))

    def test_is_own_bootstrap(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            self.assertFalse(terms.isOwn(output))

    def test_is_own_terms_path(self):
        """
        Test that checking whether an output was produced by this tool returns true when given its own output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', "sample.json")
        self.assertTrue(terms.isOwn(file))

    def test_is_own_bootstrap_path(self):
        """
        Test that checking whether an output was produced by this tool returns false when given another tool's output.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', "bootstrapped.json")
        self.assertFalse(terms.isOwn(file))

    def test_load_extracted(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, the terms themselves are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'bootstrapping', 'seed.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            _terms = terms.load(output)
            original = output['terms']
            original = [ term['term'] for term in original ]

        self.assertTrue(all( type(term) is str for term in _terms ))
        self.assertEqual(len(original), len(_terms))

    def test_load_extracted_cmd(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, the terms themselves are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'sample.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            _terms = terms.load(output)
            original = output['terms']
            original = [ term['term'] for term in original ]

        self.assertTrue(all( type(term) is str for term in _terms ))
        self.assertEqual(len(original), len(_terms))

    def test_load_extracted_order(self):
        """
        Test that when loading terms from the output of the ``terms`` tool, they are loaded in order of rank.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'sample.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            _terms = terms.load(output)
            original = output['terms']
            original = [ term['term'] for term in original ]
        self.assertEqual(original, _terms)

    def test_load_from_path(self):
        """
        Test that when loading terms from a filepath, they are loaded correctly.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'ate', 'sample.json')
        with open(file) as f:
            output = json.loads(''.join(f.readlines()))
            original = output['terms']
            original = [ term['term'] for term in original ]
        _terms = terms.load(file)
        self.assertEqual(original, _terms)

    def test_extract_no_files(self):
        """
        Test that when no files are given when extracting, a SystemExit is raised.
        """

        self.assertRaises(SystemExit, terms.extract, EF(), None)
        self.assertRaises(SystemExit, terms.extract, EF(), [ ])

    def test_extract_no_candidates(self):
        """
        Test that when extracting terms without candidates, all candidates are returned.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(LogEF)
        extracted = terms.extract(extractor, files)
        extracted_list = terms.extract(extractor, files, candidates=[])
        extracted_none = terms.extract(extractor, files, candidates=None)
        self.assertGreater(len(extracted), 10)
        self.assertEqual(len(extracted), len(extracted_list))
        self.assertEqual(len(extracted), len(extracted_none))

    def test_extract_only_candidates(self):
        """
        Test that when extracting candidates, only those candidates are returned.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(LogEF)
        candidates = [ 'kepa' ]
        extracted = terms.extract(extractor, files, candidates=candidates)
        self.assertEqual(1, len(extracted))
        self.assertEqual(candidates, [ term['term'] for term in extracted ])

    def test_extract_unknown_candidates(self):
        """
        Test that when extracting unknown candidates, only those candidates are returned.
        This can happen when, for example, following up TF-IDF with EF-IDF (and the term is never breaking).
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        extractor = terms.create_extractor(LogEF)
        candidates = [ 'superlongword' ]
        extracted = terms.extract(extractor, files, candidates=candidates)
        self.assertEqual(1, len(extracted))
        self.assertEqual(candidates, [ term['term'] for term in extracted ])

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

    def test_create_extractor_eficf_missing_idf(self):
        """
        Test that when the TF-IDF scheme is not given for the EF-ICF, a SystemExit is raised.
        """

        self.assertRaises(SystemExit, terms.create_extractor, EFICF)

    def test_extract_efidf_with_incorrect_corpora(self):
        """
        Test that when the EF-IDF receives incorrect corpus types, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', 'LIVMUN.json')
        extractor = terms.create_extractor(EFIDF, tfidf=idf)
        self.assertRaises(ValueError, extractor.extract, path)

    def test_extract_eficf_with_incorrect_corpora(self):
        """
        Test that when the EF-ICF receives incorrect corpus types, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', 'LIVMUN.json')
        extractor = terms.create_extractor(EFICF, tfidf=idf)
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

    def test_create_extractor_eficfentropy_missing_idf(self):
        """
        Test that when the TF-IDF scheme is not given to the EF-ICF-Entropy extractor, a SystemExit is raised.
        """

        self.assertRaises(SystemExit, terms.create_extractor, EFICFEntropy)

    def test_create_extractor_evate_missing_idf(self):
        """
        Test that when the TF-IDF scheme is not given to the EVATEextractor, a SystemExit is raised.
        """

        self.assertRaises(SystemExit, terms.create_extractor, EVATE)

    def test_extract_efidfentropy_with_incorrect_corpora(self):
        """
        Test that when the EF-IDF-Entropy extractor receives incorrect corpus types, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', 'LIVMUN.json')
        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf)
        self.assertRaises(ValueError, extractor.extract, path, path)

    def test_extract_eficfentropy_with_incorrect_corpora(self):
        """
        Test that when the EF-ICF-Entropy extractor receives incorrect corpus types, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', 'LIVMUN.json')
        extractor = terms.create_extractor(EFICFEntropy, tfidf=idf)
        self.assertRaises(ValueError, extractor.extract, path, path)

    def test_extract_evate_with_incorrect_corpora(self):
        """
        Test that when the EVATE extractor receives incorrect corpus types, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        path = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf', 'LIVMUN.json')
        extractor = terms.create_extractor(EVATE, tfidf=idf)
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

    def test_extract_eficfentropy_with_unequal_corpora(self):
        """
        Test that when the EF-ICF-Entropy extractor receives a different number of timelines and IDFs, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events[:len(events) - 1] ]
        extractor = terms.create_extractor(EFICFEntropy, tfidf=idf)
        self.assertRaises(ValueError, extractor.extract, timelines, idfs=idfs)

    def test_extract_evate_with_unequal_corpora(self):
        """
        Test that when the EVATE extractor receives a different number of timelines and IDFs, it raises a ValueError.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events[:len(events) - 1] ]
        extractor = terms.create_extractor(EVATE, tfidf=idf)
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

    def test_extract_keep_large(self):
        """
        Test that when providing a large value of terms to keep, all terms are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs)
        keep = len(extracted) + 1
        self.assertEqual(len(extracted), len(terms.extract(extractor, timelines, idfs=idfs, keep=keep)))

    def test_extract_keep_all(self):
        """
        Test that when the number of terms to keep is the same as the number of actual terms, all terms are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs)
        keep = len(extracted)
        self.assertEqual(len(extracted), len(terms.extract(extractor, timelines, idfs=idfs, keep=keep)))

    def test_extract_keep_none(self):
        """
        Test that when no number of terms is specified, all terms are returned,
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted_ef = terms.extract(extractor, timelines)

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs)
        self.assertEqual(len(extracted_ef), len(extracted))

    def test_extract_keep_top_ranks(self):
        """
        Test that when extracting only a few terms, the top-ranked terms are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted_all = terms.extract(extractor, timelines, idfs=idfs)

        keep = 10
        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs, keep=keep)
        self.assertEqual(1, extracted[0]['rank'])
        self.assertEqual(keep, extracted[-1]['rank'])
        self.assertEqual(extracted_all[:keep], extracted)

    def test_extract_keep_top_scoring(self):
        """
        Test that when extracting only a few terms, the top-scoring terms are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        keep = 10
        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs, keep=keep)
        self.assertTrue(all( extracted[i]['score'] >= extracted[i + 1]['score'] for i in range(len(extracted) - 1) ))

    def test_extract_no_normalize(self):
        """
        Test that when extracting terms without the normalization flag, the scores are not normalized.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs, normalized=False)
        self.assertTrue(any( term['score'] > 1 for term in extracted ))

    def test_extract_normalize(self):
        """
        Test that when extracting terms with the normalization flag, the scores are all normalized.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs, normalized=True)
        self.assertTrue(all( 0 <= term['score'] <= 1 for term in extracted ))
        self.assertEqual(1, extracted[0]['score'])
        self.assertEqual(0, extracted[-1]['score'])

    def test_extract_normalize_same_order(self):
        """
        Test that normalizing scores does not affect the order of the terms.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EFIDFEntropy, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs, normalized=False)
        normalized = terms.extract(extractor, timelines, idfs=idfs, normalized=True)
        self.assertEqual([ term['term'] for term in extracted ],
                         [ term['term'] for term in normalized ])

    def test_rank_copy(self):
        """
        Test that when ranking terms, the original term dictionary is not changed.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = extractor.extract(timelines)
        original = copy.deepcopy(extracted)
        ranked = terms.rank(extracted)
        self.assertEqual(original, extracted)

    def test_rank_all_terms(self):
        """
        Test that when ranking terms, all terms are returned.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = extractor.extract(timelines)
        ranked = terms.rank(extracted)
        ranked_terms = [ term['term'] for term in ranked ]
        self.assertEqual(set(extracted), set(ranked_terms))

    def test_rank_no_duplicates(self):
        """
        Test that when ranking terms, there are no duplicates.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = extractor.extract(timelines)
        ranked = terms.rank(extracted)
        ranked_terms = [ term['term'] for term in ranked ]
        self.assertEqual(len(ranked_terms), len(set(ranked_terms)))

    def test_rank_aligned_scores(self):
        """
        Test that when ranking terms, the scores are correct.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = extractor.extract(timelines)
        ranked = terms.rank(extracted)
        self.assertTrue(all( term['score'] == extracted[term['term']] for term in ranked ))

    def test_rank_descending_scores(self):
        """
        Test that when ranking terms, the terms are returned in descending order of their score.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = extractor.extract(timelines)
        ranked = terms.rank(extracted)
        self.assertTrue(all([ ranked[i]['score'] >= ranked[i + 1]['score'] for i in range(len(ranked) - 1) ]))

    def test_rank_start_from_one(self):
        """
        Test that when ranking terms, the ranks start from 1.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = extractor.extract(timelines)
        ranked = terms.rank(extracted)
        self.assertEqual(1, ranked[0]['rank'])

    def test_rank_ascending_rank(self):
        """
        Test that when ranking terms, the ranks are in ascending order.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = extractor.extract(timelines)
        ranked = terms.rank(extracted)
        self.assertTrue(all([ ranked[i]['rank'] < ranked[i + 1]['rank'] for i in range(len(ranked) - 1) ]))

    def test_rerank_same_terms_as_base(self):
        """
        Test that when re-ranking, the same terms extracted by the base method are returned.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF, base=2)
        extracted = terms.extract(extractor, timelines)
        extracted_terms = [ term['term'] for term in extracted ]

        reranked = terms.rerank(extracted, reranker=TFIDFExtractor, tfidf=idf, files=files, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        reranked_terms = [ term['term'] for term in reranked ]
        self.assertEqual(set(extracted_terms), set(reranked_terms))

    def test_rerank_scores_as_extracted(self):
        """
        Test that when re-ranking, the scores are the same as when extracting the terms using the same method, but as a base method.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(TFIDFExtractor, tfidf=idf)
        extracted = terms.extract(extractor, files)
        extracted_terms = [ term['term'] for term in extracted ]

        reranked = terms.rerank(extracted, reranker=TFIDFExtractor, tfidf=idf, files=files, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        reranked_terms = [ term['term'] for term in reranked ]
        self.assertEqual(extracted, reranked)

    def test_rerank_no_normalize(self):
        """
        Test that when reranking terms without the normalization flag, the scores are not normalized.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs, normalized=False)
        reranked = terms.rerank(extracted, reranker=TFIDFExtractor, tfidf=idf, files=files,
                                general=None, cutoff=None, base=None, keep=None,
                                normalized=False, idfs=None)
        self.assertTrue(any( term['score'] > 1 for term in reranked ))

    def test_rerank_normalize(self):
        """
        Test that when reranking terms with the normalization flag, the scores are all normalized.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs, normalized=True)
        reranked = terms.rerank(extracted, reranker=TFIDFExtractor, tfidf=idf, files=files,
                                general=None, cutoff=None, base=None, keep=None,
                                normalized=True, idfs=None)
        self.assertTrue(all( 0 <= term['score'] <= 1 for term in reranked ))
        self.assertEqual(1, reranked[0]['score'])
        self.assertEqual(0, reranked[-1]['score'])

    def test_rerank_normalize_same_order(self):
        """
        Test that normalizing the reranker's scores, it does not affect the order of the terms.
        """

        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        events = [ 'CRYCHE', 'LIVMUN' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]
        idfs = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf_wo_rt', f"{ event }.json") for event in events ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF, tfidf=idf, base=2)
        extracted = terms.extract(extractor, timelines, idfs=idfs, normalized=False)
        reranked = terms.rerank(extracted, reranker=TFIDFExtractor, tfidf=idf, files=files,
                                general=None, cutoff=None, base=None, keep=None,
                                normalized=False, idfs=None)
        normalized = terms.rerank(extracted, reranker=TFIDFExtractor, tfidf=idf, files=files,
                                  general=None, cutoff=None, base=None, keep=None,
                                  normalized=True, idfs=None)
        self.assertEqual([ term['term'] for term in reranked ],
                         [ term['term'] for term in normalized ])

    def test_reranker_params_only_reranker(self):
        """
        Test that when extracting the re-ranker parameters, only the re-ranker parameters are retained.
        """

        params = {
            'method': 'TFIDF',
            'files': [ 'data/tokenized1.json', 'data/tokenized2.json' ],
            'reranker': 'EF',
            'reranker_files': [ 'data/timeline1.json', 'data/timeline2.json' ]
        }
        reranker_params = terms.reranker_params(params)
        self.assertEqual(2, len(reranker_params))
        self.assertFalse('method' in reranker_params)
        self.assertEqual(reranker_params['files'], params['reranker_files'])

    def test_reranker_params_all_reranker(self):
        """
        Test that when extracting the re-ranker parameters, all the re-ranker parameters are retained.
        """

        params = {
            'method': 'TFIDF',
            'files': [ 'data/tokenized1.json', 'data/tokenized2.json' ],
            'reranker': 'EF',
            'reranker_files': [ 'data/timeline1.json', 'data/timeline2.json' ],
            'reranker_keep': 50,
            'reranker_normalize': False,
            'reranker_tfidf': 'path/to/idf.json',
            'reranker_general': 'path/to/general.json',
            'reranker_cutoff': 100,
            'reranker_base': 2,
            'reranker_idfs': [ 'data/idf1.json', 'data/idf2.json' ]
        }
        reranker_params = terms.reranker_params(params)
        self.assertEqual({ 'reranker', 'files', 'keep', 'normalize',
                           'tfidf', 'general', 'cutoff', 'base', 'idfs' }, set(reranker_params))

    def test_reranker_params_reranker(self):
        """
        Test that when extracting the re-ranker parameters, the re-ranker parameter is retained normally.
        """

        params = {
            'method': 'TFIDF',
            'files': [ 'data/tokenized1.json', 'data/tokenized2.json' ],
            'reranker': 'EF',
            'reranker_files': [ 'data/timeline1.json', 'data/timeline2.json' ],
        }
        reranker_params = terms.reranker_params(params)
        self.assertTrue('reranker' in reranker_params)
        self.assertEqual(params['reranker'], reranker_params['reranker'])

    def test_reranker_params_no_prefix(self):
        """
        Test that when extracting the re-ranker parameters, the prefix is not retained.
        """

        params = {
            'method': 'TFIDF',
            'files': [ 'data/tokenized1.json', 'data/tokenized2.json' ],
            'reranker': 'EF',
            'reranker_files': [ 'data/timeline1.json', 'data/timeline2.json' ],
            'reranker_keep': 50,
            'reranker_tfidf': 'path/to/idf.json',
            'reranker_general': 'path/to/general.json',
            'reranker_cutoff': 100,
            'reranker_base': 2,
            'reranker_idfs': [ 'data/idf1.json', 'data/idf2.json' ]
        }
        reranker_params = terms.reranker_params(params)
        self.assertTrue(all( not param.startswith('reranker_') for param in reranker_params ))

    def test_reranker_params_unchanged(self):
        """
        Test that the original parameters are unchanged when extracting the re-ranker parameters.
        """

        params = {
            'method': 'TFIDF',
            'files': [ 'data/tokenized1.json', 'data/tokenized2.json' ],
            'reranker': 'EF',
            'reranker_files': [ 'data/timeline1.json', 'data/timeline2.json' ],
            'reranker_keep': 50,
            'reranker_tfidf': 'path/to/idf.json',
            'reranker_general': 'path/to/general.json',
            'reranker_cutoff': 100,
            'reranker_base': 2,
            'reranker_idfs': [ 'data/idf1.json', 'data/idf2.json' ]
        }
        params_copy = dict(params)
        self.assertEqual(params_copy, params)
        reranker_params = terms.reranker_params(params)
        self.assertEqual(params_copy, params)

    def test_normalize_empty(self):
        """
        Test that normalizing an empty set of terms returns another empty set of terms.
        """

        self.assertEqual({ }, terms.normalize({ }))

    def test_normalize_copy(self):
        """
        Test that score normalization creates a copy and does not affect the original list of terms.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        _extracted = copy.deepcopy(extracted)
        self.assertEqual(extracted, _extracted)
        normalized = terms.normalize(extracted)
        self.assertEqual(extracted, _extracted)
        self.assertFalse(normalized == extracted)

    def test_normalize_zero_inclusive(self):
        """
        Test that when normalizing, the lowest score is 0.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        normalized = terms.normalize(extracted)
        self.assertEqual(0, min( term['score'] for term in normalized ))

    def test_normalize_one_inclusive(self):
        """
        Test that when normalizing, the highest score is 1.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        normalized = terms.normalize(extracted)
        self.assertEqual(1, max( term['score'] for term in normalized ))

    def test_normalize_bounds(self):
        """
        Test that when normalizing, the new term scores are bound between 0 and 1.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        normalized = terms.normalize(extracted)
        self.assertTrue(all( 0 <= term['score'] <= 1 for term in normalized ))

    def test_normalize_same_order(self):
        """
        Test that when normalizing, the same order is kept for all terms.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        normalized = terms.normalize(extracted)
        self.assertEqual([ term['term'] for term in extracted ],
                         [ term['term'] for term in normalized ])

    def test_normalize_same_terms(self):
        """
        Test that normalizing returns all terms from the original list.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        normalized = terms.normalize(extracted)
        self.assertEqual(list(set([ term['term'] for term in extracted ])),
                         list(set([ term['term'] for term in normalized ])))

    def test_normalize_same_ranks(self):
        """
        Test that the terms' ranks are correct after normalizing.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        ranks = { term['rank']: term['term'] for term in extracted }
        normalized = terms.normalize(extracted)
        self.assertTrue(all( ranks[term['rank']] == term['term'] for term in normalized ))

    def test_normalize_descending_order_of_score(self):
        """
        Test that when normalizing scores, the returned list is in descending order of scores.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        normalized = terms.normalize(extracted)
        self.assertTrue([ normalized[i]['rank'] < normalized[i + 1]['rank'] for i in range(len(normalized) - 1) ])
        self.assertTrue([ normalized[i]['score'] >= normalized[i + 1]['score'] for i in range(len(normalized) - 1) ])

    def test_combine_normal_unchanged(self):
        """
        Test that when combining two lists of terms using the 'normal' mode, the returned list is the same.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        combined = terms.combine('normal', extracted, reranked)
        self.assertEqual(extracted, reranked)
        self.assertEqual(combined, extracted)

    def test_combine_normal_copy(self):
        """
        Test that when combining two lists of terms using the 'normal' mode, the original lists are not changed.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        extracted_copy = copy.deepcopy(extracted)

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        reranked_copy = copy.deepcopy(reranked)
        combined = terms.combine('normal', extracted, reranked)
        self.assertEqual(extracted_copy, extracted)
        self.assertEqual(reranked_copy, reranked)

    def test_combine_multiply_unchanged(self):
        """
        Test that when combining two lists of terms using the 'multiply' mode, the returned list is the same.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        combined = terms.combine('multiply', extracted, reranked)
        self.assertEqual(extracted, reranked)

    def test_combine_multiply_copy(self):
        """
        Test that when combining two lists of terms using the 'multiply' mode, the original lists are not changed.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        extracted_copy = copy.deepcopy(extracted)

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        reranked_copy = copy.deepcopy(reranked)
        combined = terms.combine('multiply', extracted, reranked)
        self.assertEqual(extracted_copy, extracted)
        self.assertEqual(reranked_copy, reranked)

    def test_combine_multiply_correct(self):
        """
        Test that when combining two lists of terms, the results are correct.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        extracted_scores = { term['term']: term['score'] for term in extracted }

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        reranked_scores = { term['term']: term['score'] for term in reranked }

        combined = terms.combine('multiply', extracted, reranked)
        self.assertTrue(all( term['score'] == extracted_scores[term['term']] * reranked_scores[term['term']]
                             for term in combined ))

    def test_combine_harmonic_copy(self):
        """
        Test that when combining two lists of terms using the 'harmonic' mode, the original lists are not changed.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        extracted_copy = copy.deepcopy(extracted)

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        reranked_copy = copy.deepcopy(reranked)
        combined = terms.combine('harmonic', extracted, reranked)
        self.assertEqual(extracted_copy, extracted)
        self.assertEqual(reranked_copy, reranked)

    def test_combine_harmonic_correct(self):
        """
        Test that when combining two lists of terms, the results are correct.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        extracted_scores = { term['term']: term['score'] for term in extracted }

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        reranked_scores = { term['term']: term['score'] for term in reranked }

        combined = terms.combine('harmonic', extracted, reranked)
        self.assertTrue(all( term['score'] == 2 * extracted_scores[term['term']] * reranked_scores[term['term']] / (extracted_scores[term['term']] + reranked_scores[term['term']])
                             for term in combined ))

    def test_combine_harmonic_zero_reranker(self):
        """
        Test that when combining two lists of terms, terms whose reranked score is zero also get a zero score.
        """

        events = [ 'CRYCHE', 'LIVMUN' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', f"{ event }.json") for event in events ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(TFExtractor)
        extracted = terms.extract(extractor, files, keep=200)
        extracted_scores = { term['term']: term['score'] for term in extracted }

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)
        reranked_scores = { term['term']: term['score'] for term in reranked }

        combined = terms.combine('harmonic', extracted, reranked)
        zero_scores = { term: score for term, score in reranked_scores.items()
                                    if score == 0 }
        self.assertTrue(zero_scores)
        combined_scores = { term['term']: term['score'] for term in combined }
        self.assertTrue(all( combined_scores[term] == 0 for term in zero_scores ))

    def test_combine_harmonic_zero_denominator(self):
        """
        Test that when combining two lists of terms, the harmonic mean of a term whose scores are both 0 is also 0.
        """

        extracted, reranked = [ { 'term': 'term', 'score': 0 } ], [ { 'term': 'term', 'score': 0 } ]
        combined = terms.combine('harmonic', extracted, reranked)
        self.assertEqual(0, combined[0]['score'])

    def test_combine_harmonic_same_score(self):
        """
        Test that when combining two lists of terms, the harmonic mean of a term whose scores are the same do not chage.
        """

        extracted, reranked = [ { 'term': f"t{ i }", 'score': i/10 } for i in range(0, 11) ], [ { 'term': f"t{ i }", 'score': i/10 } for i in range(0, 11) ]
        extracted_scores = { term['term']: term['score'] for term in extracted }
        reranked_scores = { term['term']: term['score'] for term in reranked }
        combined = terms.combine('harmonic', extracted, reranked)
        combined_scores = { term['term']: term['score'] for term in combined }
        self.assertTrue(all( round(score, 10) == extracted_scores[term] for term, score in combined_scores.items() ))
        self.assertTrue(all( round(score, 10) == reranked_scores[term] for term, score in combined_scores.items() ))

    def test_combine_base_order_zero_score(self):
        """
        Test that when combining two lists of terms, all terms with a zero score have the same order as in the baseline.
        """

        events = [ 'CRYCHE', 'LIVMUN' ]
        files = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'tokenized', f"{ event }.json") for event in events ]
        idf = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'idf.json')
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        # extract the terms using TF-IDF
        extractor = terms.create_extractor(TFIDFExtractor, tfidf=idf)
        extracted = terms.extract(extractor, files, keep=200)
        extracted_scores = { term['term']: term['score'] for term in extracted }
        base_terms = sorted(extracted_scores.keys(), key=extracted_scores.get, reverse=True)

        # rerank the terms without Laplace smoothing
        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines,
                                general=None, cutoff=None, base=None, keep=None,
                                normalized=True, idfs=None, laplace=False)
        reranked_scores = { term['term']: term['score'] for term in reranked }
        combined = terms.combine('multiply', extracted, reranked)

        # test that the terms with a combined score of zero are ordered in the same way as in the original list
        zero_terms = [ term['term'] for term in combined if term['score'] == 0 ]
        self.assertTrue(zero_terms)
        for i in range(len(zero_terms) - 1):
            self.assertLess(base_terms.index(zero_terms[i]), base_terms.index(zero_terms[i + 1]))

    def test_combine_multiply_correct_order(self):
        """
        Test that when combining two lists of terms, the results are sorted in descending order of score.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)

        combined = terms.combine('multiply', extracted, reranked)
        self.assertTrue(all( combined[i]['score'] >= combined[i + 1]['score'] for i in range(len(combined) - 1) ))

    def test_combine_multiply_correct_rank(self):
        """
        Test that when combining two lists of terms, the results are sorted in ascending order of rank.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)
        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=None, idfs=None)

        combined = terms.combine('multiply', extracted, reranked)
        self.assertEqual(1, combined[0]['rank'])
        self.assertTrue(all( combined[i]['rank'] < combined[i + 1]['rank'] for i in range(len(combined) - 1) ))

    def test_combine_normal_normalized(self):
        """
        Test that when combining two lists of terms using the 'normal' mode, and the re-ranker uses normalization, the combined scores are also normalized.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines)

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=True, idfs=None)
        combined = terms.combine('normal', extracted, reranked)
        self.assertTrue(all( 0 <= term['score'] <= 1 for term in combined ))

    def test_combine_multiply_normalized(self):
        """
        Test that when combining two lists of terms using the 'multiply' mode,the combined scores are normalized if both extractor and re-ranker use normalization.
        """

        events = [ 'CRYCHE', 'LIVMUN', 'LIVNAP', 'MUNARS' ]
        timelines = [ os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'timelines', f"{ event }.json") for event in events ]

        extractor = terms.create_extractor(EF)
        extracted = terms.extract(extractor, timelines, normalized=True)

        reranked = terms.rerank(extracted, reranker=EF, tfidf=None, files=timelines, general=None, cutoff=None, base=None, keep=None, normalized=True, idfs=None)
        combined = terms.combine('multiply', extracted, reranked)
        self.assertTrue(all( 0 <= term['score'] <= 1 for term in combined ))
