"""
Test the functionality of the tweet package-level functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

import twitter
from logger import logger

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the tweet package-level functions.
    """

    def test_timestamp_ms_date(self):
        """
        Test that the timestamp date is the same and correct for all tweets in the corpus.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                date = datetime.fromtimestamp(twitter.extract_timestamp(tweet))
                self.assertEqual(2018, date.year)
                self.assertEqual(12, date.month)
                self.assertEqual(30, date.day)
                self.assertEqual(12, date.hour)
                self.assertTrue(date.minute in range(45, 50))

    def test_timestamp_created_at_date(self):
        """
        Test that the timestamp date is the same and correct for all tweets in the corpus.
        In this test, the millisecond timestamp is removed so the created-at date is used instead.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertTrue('created_at' in tweet)
                self.assertTrue('timestamp_ms' in tweet)
                del tweet['timestamp_ms']
                self.assertTrue('created_at' in tweet)
                self.assertFalse('timestamp_ms' in tweet)
                date = datetime.fromtimestamp(twitter.extract_timestamp(tweet))
                self.assertEqual(2018, date.year)
                self.assertEqual(12, date.month)
                self.assertEqual(30, date.day)
                self.assertEqual(12, date.hour)
                self.assertTrue(date.minute in range(45, 50))

    def test_timestamp_ms_equal_created_at(self):
        """
        Test that the timestamp extracted from the milli-seconds is equal to the timestamp from the created-at field.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                del tweet['timestamp_ms']
                self.assertTrue('created_at' in tweet)
                self.assertFalse('timestamp_ms' in tweet)
                created_at = twitter.extract_timestamp(tweet)

                tweet = json.loads(line)
                del tweet['created_at']
                self.assertFalse('created_at' in tweet)
                self.assertTrue('timestamp_ms' in tweet)
                timestamp_ms = twitter.extract_timestamp(tweet)
                self.assertEqual(created_at, timestamp_ms)

    def test_timestamp_no_fields(self):
        """
        Test that when there are no valid fields, a KeyError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            line = f.readline()
            tweet = json.loads(line)
            del tweet['timestamp_ms']
            del tweet['created_at']
            self.assertFalse('timestamp_ms' in tweet)
            self.assertFalse('created_at' in tweet)
            self.assertRaises(KeyError, twitter.extract_timestamp, tweet)

    def test_full_text_ellipsis(self):
        """
        Test that when the text has an ellipsis, the full text is retrieved.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if '…' in tweet['text']:
                    found = True
                    text = twitter.full_text(tweet)

                    """
                    Make an exception for a special case.
                    """
                    if not ('retweeted_status' in tweet):
                        self.assertFalse(text.endswith('…'))

        if not found:
            logger.warning('Trivial test')

    def test_full_text_quoted(self):
        """
        Test that when the tweet is a quote, the text is used, not the quoted tweet's text.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if 'retweeted_status' in tweet:
                    timestamp = tweet['timestamp_ms']
                    tweet = tweet['retweeted_status']
                    tweet['timestamp_ms'] = timestamp

                if 'quoted_status' in tweet:
                    found = True
                    text = twitter.full_text(tweet)

                    if 'extended_tweet' in tweet:
                        self.assertEqual(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), text)
                    else:
                        self.assertEqual(tweet.get('text'), text)

        if not found:
            logger.warning('Trivial test')

    def test_full_text_retweeted(self):
        """
        Test that when the tweet is a quote, the retweet's text is used.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if 'retweeted_status' in tweet:
                    found = True
                    text = twitter.full_text(tweet)

                    retweet = tweet['retweeted_status']
                    if 'extended_tweet' in retweet:
                        self.assertEqual(retweet["extended_tweet"].get("full_text", retweet.get("text", "")), text)
                    else:
                        self.assertEqual(retweet.get('text'), text)

                    """
                    Tweets shouldn't start with 'RT'.
                    """
                    self.assertFalse(text.startswith('RT'))

        if not found:
            logger.warning('Trivial test')

    def test_full_text_normal(self):
        """
        Test that when the tweet is not a quote or retweet, the full text is used.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not 'retweeted_status' in tweet and not 'quoted_status' in tweet:
                    found = True
                    text = twitter.full_text(tweet)

                    if 'extended_tweet' in tweet:
                        self.assertEqual(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), text)
                    else:
                        self.assertEqual(tweet.get('text'), text)

                    """
                    There should be no ellipsis in the text now.
                    """
                    self.assertFalse(text.endswith('…'))

        if not found:
            logger.warning('Trivial test')

    def test_is_retweet(self):
        """
        Test that when checking for retweets, the function returns ``True`` only if the ``retweeted_status`` key is set.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if 'retweeted_status' in tweet:
                    found = True
                    self.assertTrue(twitter.is_retweet(tweet))
                else:
                    self.assertFalse(twitter.is_retweet(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_is_reply_all_not_replies(self):
        """
        Test that when checking for replies, the function returns ``True`` only if the ``in_reply_to_status_id_str`` key is not None.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if tweet['in_reply_to_status_id_str'] is not None:
                    found = True
                    self.assertTrue(twitter.is_reply(tweet))
                else:
                    self.assertFalse(twitter.is_reply(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_is_reply_allows_mentions(self):
        """
        Test that when checking for replies, just because the tweet includes a mention does not make it a reply.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if tweet['entities']['user_mentions'] and tweet['in_reply_to_status_id_str'] is None:
                    found = True
                    self.assertFalse(twitter.is_reply(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_is_verified(self):
        """
        Test that when checking whether the tweet is from a verified author, the function returns ``True`` only if the author is verified.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if tweet['user']['verified']:
                    found = True
                    self.assertTrue(twitter.is_verified(tweet))
                else:
                    self.assertFalse(twitter.is_verified(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_not_verified_retweet(self):
        """
        Test that when checking whether a retweet is from a verified author, the retweeting author is checked
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    continue

                if tweet['user']['verified'] and not tweet['retweeted_status']['user']['verified']:
                    found = True
                    self.assertTrue(twitter.is_verified(tweet))

        if not found:
            logger.warning('Trivial test')

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    continue

                if not tweet['user']['verified'] and tweet['retweeted_status']['user']['verified']:
                    found = True
                    self.assertFalse(twitter.is_verified(tweet))

        if not found:
            logger.warning('Trivial test')
