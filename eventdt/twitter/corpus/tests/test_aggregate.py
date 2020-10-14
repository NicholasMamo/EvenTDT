"""
Test the functionality of the aggregation functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from nlp.tokenizer import Tokenizer
from twitter.corpus.aggregate import *
from vsm import vector_math
import twitter

class TestAggregate(unittest.TestCase):
    """
    Test the functionality of the aggregation functions.
    """

    def volume(self, bin, track=None, *args, **kwargs):
        """
        Count the number of tweets in the given bin.
        If a tracking keyword is given, the function returns the number of tweets in which the keyword appears.
        The function looks for the keyword in the dimensions.

        :param bin: A bin containing a list of tweets to count.
        :type bin: list of dict
        :param track: The keyword to track.
        :type track: None or str

        :return: The number of tweets in the bin.
                 If a tracking keyword is given, the function counts the number of tweets in the bin that contain the keyword.
        :rtype: int
        """

        if track:
            return len([ tweet for tweet in bin if track.lower() in tweet['text'] ])
        else:
            return len(bin)

    def test_volume_empty_bin(self):
        """
        Test that the volume of an empty bin is 0.
        """

        self.assertEqual(0, self.volume([ ]))

    def test_volume_all(self):
        """
        Test that the overall volume is the length of the bin.
        """

        self.assertEqual(10, self.volume(range(0, 10)))

    def test_volume_track(self):
        """
        Test that the volume of a tracked keyword looks in the document's dimensions.
        """

        self.assertEqual(1, self.volume([ { 'text': 'b' } ], track='b'))

    def test_volume_track_no_matches(self):
        """
        Test that the volume of a tracked keyword returns 0 if there are no matches.
        """

        self.assertEqual(0, self.volume([ { 'text': 'b' } ], track='a'))

    def test_volume_track_matches(self):
        """
        Test that the volume of a tracked keyword returns the number of matches.
        """

        self.assertEqual(1, self.volume([ { 'text': 'a' },
                                          { 'text': 'b' } ], track='b'))

    def test_aggregate_timestamps(self):
        """
        Test that when aggregating the corpus, the correct timestamps are processed.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            volume = aggregate(f, agg=self.volume, bin_size=1)

            f.seek(0)
            lines = f.readlines()
            tweets = [ json.loads(line) for line in lines ]
            timestamps = set([ twitter.extract_timestamp(tweet) for tweet in tweets ])
            self.assertEqual(timestamps, set(volume))

    def test_aggregate_count(self):
        """
        Test that the total count of the aggregation is equivalent to the corpus length.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            volume = aggregate(f, agg=self.volume, bin_size=1)

            f.seek(0)
            lines = f.readlines()
            self.assertEqual(len(lines), sum([ volume[bin]['*'] for bin in volume ]))

    def test_aggregate_reverse_count(self):
        """
        Test that when aggregating a reversed corpus, the correct count is still used.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = reversed(f.readlines())
            volume = aggregate(lines, agg=self.volume,bin_size=1)

            f.seek(0)
            lines = f.readlines()
            self.assertEqual(len(lines), sum([ volume[bin]['*'] for bin in volume ]))

            tweets = [ json.loads(line) for line in lines ]
            timestamps = set([ twitter.extract_timestamp(tweet) for tweet in tweets ])
            self.assertEqual(timestamps, set(volume))

    def test_aggregate_track_keyword(self):
        """
        Test that when tracking keywords, there is an entry for it at each timestamp.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            volume = aggregate(f, agg=self.volume, bin_size=1, track='coronaviru')

            self.assertTrue(all([ 'coronaviru' in volume[bin] for bin in volume ]))

    def test_aggregate_track_nonexistent_keyword(self):
        """
        Test that when tracking keywords that do not exist in the corpus, they still have a volume of zero.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            volume = aggregate(f, agg=self.volume, bin_size=1, track='terrier')

            self.assertTrue(all([ 'terrier' in volume[bin] for bin in volume ]))
            self.assertEqual(0, sum([ volume[bin]['terrier'] for bin in volume ]))

    def test_bin_size(self):
        """
        Test that when setting the bin size, the tweets are segmented correctly.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            volume = aggregate(f, agg=self.volume, bin_size=5, track=[ 'coronaviru', 'coronavirus' ])
            self.assertEqual(3, len(volume))
            self.assertTrue(all(timestamp % 5 == 0 for timestamp in volume))

            for timestamp in volume:
                count = 0
                f.seek(0)
                for line in f.readlines():
                    tweet = json.loads(line)
                    time = twitter.extract_timestamp(tweet)
                    if 0 <= time - timestamp < 5:
                        count += 1
                self.assertEqual(count, volume[timestamp]['*'])
