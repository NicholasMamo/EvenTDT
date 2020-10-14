"""
Test the functionality of the APD tool.
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

from tools import participants as apd
from eventdt.apd import ELDParticipantDetector, ParticipantDetector
from eventdt.apd.extractors.local import EntityExtractor
from eventdt.apd.scorers.local import LogTFScorer, TFScorer
from eventdt.apd.filters import Filter
from eventdt.apd.filters.local import RankFilter, ThresholdFilter

from logger import logger
logger.set_logging_level(logger.LogLevel.WARNING)

class TestAPD(unittest.TestCase):
    """
    Test the functionality of the APD tool.
    """

    def test_rank_filter_subset(self):
        """
        Test that when using the rank filter, a subset of all participants are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, Filter)
        all_participants, _ = apd.detect(detector, corpus)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, k=10)
        top_participants, _ = apd.detect(detector, corpus)
        self.assertTrue(all( participant in all_participants for participant in top_participants ))

    def test_rank_filter_subset_k(self):
        """
        Test that when using the rank filter with different _k_ values, a subset is returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, k=20)
        lenient, _ = apd.detect(detector, corpus)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, k=10)
        strict, _ = apd.detect(detector, corpus)
        self.assertEqual(20, len(lenient))
        self.assertEqual(10, len(strict))
        self.assertTrue(all( participant in lenient for participant in strict ))

    def test_rank_filter_missing_k(self):
        """
        Test that when using the rank filter without a _k_, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        self.assertRaises(ValueError, apd.create_detector, ParticipantDetector, EntityExtractor, TFScorer, RankFilter)

    def test_rank_filter_length(self):
        """
        Test that when using the rank filter, the correct number of participants are retained.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, RankFilter, k=10)
        participants, _ = apd.detect(detector, corpus)
        self.assertEqual(10, len(participants))

    def test_threshold_filter_subset(self):
        """
        Test that when using the threshold filter, a subset of all participants are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, Filter)
        all_participants, _ = apd.detect(detector, corpus)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter, threshold=0.5)
        top_participants, _ = apd.detect(detector, corpus)
        self.assertTrue(all( participant in all_participants for participant in top_participants ))

    def test_threshold_filter_all(self):
        """
        Test that when using the minimum threshold filter, all participants are returned.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, Filter)
        all_participants, _ = apd.detect(detector, corpus)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter, threshold=0)
        top_participants, _ = apd.detect(detector, corpus)
        self.assertEqual(all_participants, top_participants)

    def test_rank_filter_float_threshold(self):
        """
        Test that when using the threshold filter, the threshold is used as a float.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, LogTFScorer, ThresholdFilter, threshold=0.2)
        lenient, _ = apd.detect(detector, corpus)
        detector = apd.create_detector(ParticipantDetector, EntityExtractor, LogTFScorer, ThresholdFilter, threshold=0.8)
        strict, _ = apd.detect(detector, corpus)
        self.assertTrue(all( participant in lenient for participant in strict ))
        self.assertLess(len(strict), len(lenient))

    def test_threshold_filter_missing_threshold(self):
        """
        Test that when using the threshold filter without a threshold, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        self.assertRaises(ValueError, apd.create_detector, ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter)

    def test_eld_participant_detector_missing_tfidf(self):
        """
        Test that when using the ELDParticipantDetector without a TF-IDF scheme, a ValueError is raised.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE-100.json')
        corpus = apd.load_corpus(file, True)
        self.assertRaises(ValueError, apd.create_detector, ParticipantDetector, EntityExtractor, TFScorer, ThresholdFilter)

    def test_load_corpus_all_lines(self):
        """
        Test that when loading the corpus, all tweets are loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE.json')
        with open(file) as f:
            tweets = len(f.readlines())

        corpus = apd.load_corpus(file, True)
        self.assertTrue(len(corpus))
        self.assertEqual(tweets, len(corpus))

    def test_load_corpus_complete_tweets(self):
        """
        Test that when loading the corpus, there are generally no ellipses (the tweets are complete).
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE.json')
        corpus = apd.load_corpus(file, True)
        self.assertTrue(len(corpus))

        """
        This check does not have access to tweet IDs.
        These tweets are not incomplete, but are published with the ellipses in them.
        """
        incomplete = 0
        for tweet in corpus:
            if '…' in tweet.text:
                incomplete += 1
        self.assertGreater(50, incomplete)

    def test_load_corpus_no_clean(self):
        """
        Test that when tweets are not cleaned, some mentions remain.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE.json')
        corpus = apd.load_corpus(file, False)
        self.assertTrue(len(corpus))
        self.assertTrue(any( '@' in tweet.text for tweet in corpus ))

    def test_load_corpus_clean(self):
        """
        Test that when loading and cleaning tweets, there are no mentions.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE.json')
        corpus = apd.load_corpus(file, True)
        self.assertTrue(len(corpus))

        """
        Make some exceptions for mentions that aren't really mentions.
        Some of them may look like mentions but refer to accounts that don't exist.
        """
        wrong_pattern = re.compile("@[0-9,\\s…]")
        no_space_pattern = re.compile("[^\\s]@")
        end_pattern = re.compile('@$')
        not_accounts = [ 'EPL', 'real_realestsounds', 'nevilleiesta', 'naija927', 'naijafm92.7', 'manchesterunited', 'ManchesterUnited',
                         'clintasena', 'Maksakal88', 'Aubamayeng7', 'JustWenginIt', 'marcosrojo5', 'btsportsfootball',
                         'Nsibirwahall', 'YouTubeより', 'juniorpepaseed', 'Mezieblog', 'UtdAlamin', 'spurs_vincente' ]
        for tweet in corpus:
            if '@' in tweet.text:
                if '@@' in tweet.text or ' @ ' in tweet.text or '@&gt;' in tweet.text or any(account in tweet.text for account in not_accounts):
                    continue
                if end_pattern.findall(tweet.text):
                    continue
                if no_space_pattern.findall(tweet.text):
                    continue
                if wrong_pattern.findall(tweet.text):
                    continue

                self.fail()

    def test_quoted_and_retweeted(self):
        """
        Test that in the case of a retweeted quoted tweet, the quoted tweet's text is loaded.
        """

        file = os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt', 'tests', 'corpora', 'understanding', 'CRYCHE.json')
        corpus = apd.load_corpus(file, clean=False)
        with open(file) as f:
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            self.assertTrue(any( 'retweeted_status' in tweet for tweet in tweets ))
            self.assertTrue(any( 'quoted_status' in tweet for tweet in tweets ))
            for document, tweet in zip(corpus, tweets):
                if tweet['id'] == 1079327490907271168:
                    self.assertFalse(document.text.lower().startswith('rt'))
                    self.assertTrue(document.text.startswith('This is a great article for those wishing to read a bit more of an insight into Christian Pulisic.'))

                if tweet['id'] == 1079342260788056064:
                    self.assertFalse(document.text.lower().startswith('rt'))
                    self.assertTrue(document.text.startswith('1). Reports are saying RLC is still not 100% fit'))
                    self.assertTrue('…' in tweet['text'])
                    self.assertFalse('…' in document.text)
