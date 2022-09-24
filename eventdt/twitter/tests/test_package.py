"""
Test the functionality of the tweet package-level functions.
"""

from dateutil.parser import parse
import json
import os
import random
import re
import string
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

    def test_version_v1(self):
        """
        Test that the version of all tweets collected using version 1.1 of the Twitter API is 1.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            self.assertTrue(all( 1 == twitter.version(json.loads(line)) for line in f ))

    def test_version_v2(self):
        """
        Test that the version of all tweets collected using version 2 of the Twitter API is 2.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            self.assertTrue(all( 2 == twitter.version(json.loads(line)) for line in f ))

    def test_id_returns_string(self):
        """
        Test that getting the ID from a tweet returns a string.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(str, type(twitter.id(tweet)))

    def test_id_v2_returns_string(self):
        """
        Test that getting the ID from a tweet returns a string.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(str, type(twitter.id(tweet)))

    def test_id_normal_tweet(self):
        """
        Test that getting the ID from a normal tweet returns the top-level ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(tweet['id_str'], twitter.id(tweet))

    def test_id_v2_normal_tweet(self):
        """
        Test that getting the ID from a normal tweet returns the top-level ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(str(tweet['data']['id']), twitter.id(tweet))

    def test_id_retweet(self):
        """
        Test that getting the ID from a retweet returns the top-level ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(tweet['id_str'], twitter.id(tweet))

    def test_id_v2_retweet(self):
        """
        Test that getting the ID from a retweet returns the top-level ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(str(tweet['data']['id']), twitter.id(tweet))

    def test_id_quote(self):
        """
        Test that getting the ID from a quoted tweet returns the top-level ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(tweet['id_str'], twitter.id(tweet))

    def test_id_v2_quote(self):
        """
        Test that getting the ID from a quoted tweet returns the top-level ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(str(tweet['data']['id']), twitter.id(tweet))

    def test_id_from_retweet(self):
        """
        Test that getting the ID from the retweet object returns the retweet's ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.original(tweet)['id_str'], twitter.id(twitter.original(tweet)))

    def test_id_v2_from_retweet(self):
        """
        Test that getting the ID from the retweet object returns the retweet's ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(str(twitter.original(tweet)['id']), twitter.id(twitter.original(tweet)))

    def test_id_from_quote(self):
        """
        Test that getting the ID from the quoted status object returns the quoted status' ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(twitter.quoted(tweet)['id_str'], twitter.id(twitter.quoted(tweet)))

    def test_id_v2_from_quote(self):
        """
        Test that getting the ID from the quoted status object returns the quoted status' ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    self.assertEqual(str(twitter.quoted(tweet)['id']), twitter.id(twitter.quoted(tweet)))

    def test_lang(self):
        """
        Test getting the language matches with the tweets' language.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual('en', twitter.lang(tweet))

    def test_lang_v2(self):
        """
        Test getting the language matches with the tweets' language.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(tweet['data']['lang'], twitter.lang(tweet))

    def test_lang_returns_str(self):
        """
        Test getting the language returns a string.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(str, type(twitter.lang(tweet)))

    def test_extract_timestamp_timestamp_ms_date(self):
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

    def test_extract_timestamp_timestamp_created_at_date(self):
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

    def test_extract_timestamp_v2_timestamp_created_at_date(self):
        """
        Test that the timestamp date is the same and correct for all tweets in the corpus.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                date = datetime.fromtimestamp(twitter.extract_timestamp(tweet))
                self.assertEqual(2022, date.year)
                self.assertEqual(3, date.month)
                self.assertEqual(23, date.day)
                self.assertTrue(date.hour in { 15, 16 })
                self.assertTrue(date.minute in { 58, 59, 0 })

    def test_extract_timestamp_timestamp_ms_equal_created_at(self):
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

    def test_extract_timestamp_timestamp_no_fields(self):
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

    def test_extract_timestamp_v2_normal_tweet(self):
        """
        Test extracting the timestamp from a normal tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.timestamp(tweet), parse(tweet['data']['created_at']).timestamp())

    def test_extract_timestamp_v2_retweet(self):
        """
        Test extracting the timestamp from a retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.timestamp(twitter.original(tweet)), parse(twitter.original(tweet)['created_at']).timestamp())

    def test_extract_timestamp_v2_quote(self):
        """
        Test extracting the timestamp from a quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    self.assertEqual(twitter.timestamp(twitter.quoted(tweet)), parse(twitter.quoted(tweet)['created_at']).timestamp())

    def test_text_alias_full_text(self):
        """
        Test that the ``text`` function acts as an alias to the ``full_text`` function.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(twitter.full_text(tweet), twitter.text(tweet))

    def test_text_v2_alias_full_text(self):
        """
        Test that the ``text`` function acts as an alias to the ``full_text`` function.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(twitter.full_text(tweet), twitter.text(tweet))

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
                    if not twitter.is_retweet(tweet):
                        self.assertFalse(text.endswith('…'))

        if not found:
            logger.warning('Trivial test')

    def test_full_text_v2_ellipsis(self):
        """
        Test that when the text has an ellipsis, the full text is retrieved.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if '…' in tweet['data']['text']:
                    found = True
                    text = twitter.full_text(tweet)

                    allowed = ( '1506646719215575045', '1506646731815288832', '1506646736013602818',
                                '1506646756955934726', '1506646761154441221', '1506646773741195272' ) # these tweets have an ellipsis written by the author
                    self.assertTrue(not text.endswith('…') or tweet['data']['id'] in allowed)

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
                if twitter.is_retweet(tweet):
                    tweet = twitter.original(tweet)

                if twitter.is_quote(tweet):
                    found = True
                    text = twitter.full_text(tweet)

                    if 'extended_tweet' in tweet:
                        self.assertEqual(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), text)
                    else:
                        self.assertEqual(tweet.get('text'), text)

        if not found:
            logger.warning('Trivial test')

    def test_full_text_v2_quoted(self):
        """
        Test that when the tweet is a quote, the text is used, not the quoted tweet's text.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    tweet = twitter.original(tweet)

                if twitter.is_quote(tweet):
                    found = True
                    text = twitter.full_text(tweet)

                    self.assertEqual(tweet.get('data', tweet).get('text'), text)

        if not found:
            logger.warning('Trivial test')

    def test_full_text_retweeted(self):
        """
        Test that when the tweet is a retweet, the retweet's text is used.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    found = True
                    text = twitter.full_text(tweet)

                    tweet = twitter.original(tweet)
                    if 'extended_tweet' in tweet:
                        self.assertEqual(tweet["extended_tweet"].get("full_text", tweet.get("text", "")), text)
                    else:
                        self.assertEqual(tweet.get('text'), text)

                    """
                    Tweets shouldn't start with 'RT @'.
                    """
                    self.assertFalse(text.startswith('RT @'))

        if not found:
            logger.warning('Trivial test')

    def test_full_text_v2_retweeted(self):
        """
        Test that when the tweet is a retweet, the retweet's text is used.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    found = True
                    text = twitter.full_text(tweet)

                    tweet = twitter.original(tweet)
                    self.assertEqual(tweet.get('data', tweet).get('text'), text)

                    """
                    Tweets shouldn't start with 'RT @'.
                    """
                    self.assertFalse(text.startswith('RT @'))

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
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
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

    def test_full_text_v2_normal(self):
        """
        Test that when the tweet is not a quote or retweet, the full text is used.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    found = True
                    text = twitter.full_text(tweet)

                    self.assertEqual(tweet.get('data', tweet).get('text'), text)

                    """
                    There should be no ellipsis in the text now.
                    """
                    allowed = ( '1506646719215575045', '1506646731815288832', '1506646736013602818',
                                '1506646756955934726', '1506646761154441221', '1506646773741195272' ) # these tweets have an ellipsis written by the author
                    self.assertTrue(not text.endswith('…') or tweet['data']['id'] in allowed)

        if not found:
            logger.warning('Trivial test')

    def test_urls_returns_list(self):
        """
        Test that extracting URLs from a tweet returns a list.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(list, type(twitter.urls(tweet)))
                self.assertTrue(all( str == type(url) for url in twitter.urls(tweet) ))

    def test_urls_v2_returns_list(self):
        """
        Test that extracting URLs from a tweet returns a list.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(list, type(twitter.urls(tweet)))
                self.assertTrue(all( str == type(url) for url in twitter.urls(tweet) ))

    def test_urls_no_duplicates(self):
        """
        Test that extracting URLs from a tweet returns no duplicates.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                urls = twitter.urls(tweet)
                self.assertEqual(sorted(list(set(urls))), sorted(urls))

    def test_urls_v2_no_duplicates(self):
        """
        Test that extracting URLs from a tweet returns no duplicates.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                urls = twitter.urls(tweet)
                self.assertEqual(sorted(list(set(urls))), sorted(urls))

    def test_urls_from_normal_tweet(self):
        """
        Test that extracting URLs from a normal tweet returns the URLs from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    urls = (tweet.get('extended_tweet', tweet).get('entities', { }).get('urls', [ ]) +
                            tweet.get('entities', { }).get('urls', [ ]))
                    urls = [ url['expanded_url'] for url in urls ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_v2_from_normal_tweet(self):
        """
        Test that extracting URLs from a normal tweet returns the URLs from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    urls = tweet.get('data', tweet).get('entities', { }).get('urls', [ ])
                    urls = [ url['expanded_url'] for url in urls ]
                    urls = [ url for url in urls if not url.endswith('/photo/1') and not url.endswith('/video/1') ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_from_extended(self):
        """
        Test that extracting URLs looks for URLs in the extended version of a tweet if one exists.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                original = twitter.original(tweet) if twitter.is_retweet(tweet) else tweet
                if 'extended_tweet' in original:
                    urls = (original.get('extended_tweet', original).get('entities', { }).get('urls', [ ]) +
                            original.get('entities', { }).get('urls', [ ]))
                    urls = [ url['expanded_url'] for url in urls ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_from_quoted_tweet(self):
        """
        Test that extracting URLs from a quoted tweet returns the URLs from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    urls = (tweet.get('extended_tweet', tweet).get('entities', { }).get('urls', [ ]) +
                            tweet.get('entities', { }).get('urls', [ ]))
                    urls = [ url['expanded_url'] for url in urls ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_v2_from_quoted_tweet(self):
        """
        Test that extracting URLs from a quoted tweet returns the URLs from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    urls = tweet.get('data', tweet).get('entities', { }).get('urls', [ ])
                    urls = [ url['expanded_url'] for url in urls ]
                    urls = [ url for url in urls if not url.endswith('/photo/1') and not url.endswith('/video/1') ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_from_retweets(self):
        """
        Test that extracting URLs from a retweet returns the URLs from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    urls = (original.get('extended_tweet', original).get('entities', { }).get('urls', [ ]) +
                            original.get('entities', { }).get('urls', [ ]))
                    urls = [ url['expanded_url'] for url in urls ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_v2_from_retweets(self):
        """
        Test that extracting URLs from a retweet returns the URLs from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    urls = original.get('entities', { }).get('urls', [ ])
                    urls = [ url['expanded_url'] for url in urls ]
                    urls = [ url for url in urls if not url.endswith('/photo/1') and not url.endswith('/video/1') ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_no_media(self):
        """
        Test that extracting URLs does not return media URLs.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertFalse(any( re.search("\/photo\/\\d$", url) for url in twitter.urls(tweet) ))

    def test_urls_v2_no_media(self):
        """
        Test that extracting URLs does not return media URLs.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertFalse(any( url.endswith('/photo/1') or url.endswith('/video/1') for url in twitter.urls(tweet) ))

    def test_urls_v2_normal_tweets_no_media(self):
        """
        Test that extracting URLs from tweets that are not retweeted should have all URLs but not media.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    urls = tweet.get('data', tweet).get('entities', { }).get('urls', [ ])
                    media = tweet.get('includes', tweet).get('media', [ ])
                    self.assertEqual(len(urls) - len(media), len(twitter.urls(tweet)))

    def test_urls_from_quoted_retweet(self):
        """
        Test that extracting URLs from a quoted retweet returns the URLs from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    urls = (original.get('extended_tweet', original).get('entities', { }).get('urls', [ ]) +
                            original.get('entities', { }).get('urls', [ ]))
                    urls = [ url['expanded_url'] for url in urls ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_v2_from_quoted_retweet(self):
        """
        Test that extracting URLs from a quoted retweet returns the URLs from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    urls = original.get('entities', { }).get('urls', [ ])
                    urls = [ url['expanded_url'] for url in urls ]
                    urls = [ url for url in urls if not url.endswith('/photo/1') and not url.endswith('/video/1') ]
                    self.assertEqual(list(set(urls)), twitter.urls(tweet))

    def test_urls_quoted_at_least_one(self):
        """
        Test that quoted tweets always have at least one URL (the original tweet).
        This is required by the ELD consumer.
        """

        # NOTE: Not tested due to inconsistencies in the APIv1.1 tweets.

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    tweet = twitter.original(tweet) if twitter.is_retweet(tweet) else tweet
                    # self.assertGreaterEqual(len(twitter.urls(tweet)), 1)

    def test_urls_v2_quoted_at_least_one(self):
        """
        Test that quoted tweets always have at least one URL (the original tweet).
        This is required by the ELD consumer.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertGreaterEqual(len(twitter.urls(tweet)), 1)
                    self.assertTrue(any( re.search('/status/', url) for url in twitter.urls(tweet) ))

    def test_hashtags_returns_list(self):
        """
        Test that extracting hashtags from a tweet returns a list.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(list, type(twitter.hashtags(tweet)))
                self.assertTrue(all( str == type(hashtag) for hashtag in twitter.hashtags(tweet) ))

    def test_hashtags_from_normal_tweet(self):
        """
        Test that extracting hashtags from a normal tweet returns the URLs from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    hashtags = tweet.get('extended_tweet', tweet).get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['text'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_hashtags_v2_from_normal_tweet(self):
        """
        Test that extracting hashtags from a normal tweet returns the URLs from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    hashtags = tweet.get('data', tweet).get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['tag'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_hashtags_from_extended(self):
        """
        Test that extracting hashtags looks for URLs in the extended version of a tweet if one exists.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                original = twitter.original(tweet) if twitter.is_retweet(tweet) else tweet
                if 'extended_tweet' in original:
                    hashtags = original.get('extended_tweet', original).get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['text'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_hashtags_from_quoted_tweet(self):
        """
        Test that extracting hashtags from a quoted tweet returns the URLs from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    hashtags = tweet.get('extended_tweet', tweet).get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['text'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_hashtags_v2_from_quoted_tweet(self):
        """
        Test that extracting hashtags from a quoted tweet returns the URLs from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    hashtags = tweet.get('data', tweet).get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['tag'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_hashtags_from_retweets(self):
        """
        Test that extracting hashtags from a retweet returns the URLs from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    hashtags = original.get('extended_tweet', original).get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['text'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_hashtags_v2_from_retweets(self):
        """
        Test that extracting hashtags from a retweet returns the URLs from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    hashtags = original.get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['tag'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_hashtags_from_quoted_retweet(self):
        """
        Test that extracting hashtags from a quoted retweet returns the URLs from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    hashtags = original.get('extended_tweet', original).get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['text'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_hashtags_v2_from_quoted_retweet(self):
        """
        Test thathashtags URLs from a quoted retweet returns the URLs from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    hashtags = original.get('entities', { }).get('hashtags', [ ])
                    hashtags = [ hashtag['tag'] for hashtag in hashtags ]
                    self.assertEqual(hashtags, twitter.hashtags(tweet))

    def test_annotations_raises_NotImplementedError(self):
        """
        Test that extracting hashtags from an APIv1.1 tweet raises a ``NotImplementedError``.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertRaises(NotImplementedError, twitter.annotations, tweet)

    def test_annotations_v2_returns_list(self):
        """
        Test that extracting hashtags from a tweet returns a list.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(list, type(twitter.annotations(tweet)))
                self.assertTrue(all( str == type(annotation) for annotation in twitter.annotations(tweet) ))

    def test_annotations_v2_from_normal_tweet(self):
        """
        Test that extracting annotations from a normal tweet returns the annotations from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    annotations = tweet.get('data', tweet).get('entities', { }).get('annotations', [ ])
                    annotations = [ annotation['normalized_text'] for annotation in annotations ]
                    self.assertEqual(annotations, twitter.annotations(tweet))

    def test_annotations_v2_from_quoted_tweet(self):
        """
        Test that extracting annotations from a quoted tweet returns the annotations from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    annotations = tweet.get('data', tweet).get('entities', { }).get('annotations', [ ])
                    annotations = [ annotation['normalized_text'] for annotation in annotations ]
                    self.assertEqual(annotations, twitter.annotations(tweet))

    def test_annotations_v2_from_retweets(self):
        """
        Test that extracting annotations from a retweet returns the annotations from the original tweet, not the retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    annotations = original.get('entities', { }).get('annotations', [ ])
                    annotations = [ annotation['normalized_text'] for annotation in annotations ]
                    self.assertEqual(annotations, twitter.annotations(tweet))

    def test_annotations_v2_from_quoted_retweet(self):
        """
        Test thatannotations URLs from a quoted retweet returns the annotations from the new tweet, not the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    annotations = original.get('entities', { }).get('annotations', [ ])
                    annotations = [ annotation['normalized_text'] for annotation in annotations ]
                    self.assertEqual(annotations, twitter.annotations(tweet))

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

    def test_original_not_retweet(self):
        """
        Test that getting the original tweet of a tweet that is not a retweet returns the same object.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    self.assertEqual(tweet, twitter.original(tweet))

    def test_original_retweet(self):
        """
        Test that getting the original tweet of a retweet returns the retweeted object.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(tweet['retweeted_status'], twitter.original(tweet))

    def test_original_v2_not_retweet(self):
        """
        Test that getting the original tweet of a tweet that is not a retweet returns the same object.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    self.assertEqual(tweet['data'], twitter.original(tweet))

    def test_original_v2_retweet(self):
        """
        Test that getting the original tweet of a retweet returns the retweeted object.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    referenced = [ referenced for referenced in tweet['data']['referenced_tweets']
                                              if referenced['type'] == 'retweeted' ][0]
                    original = [ _tweet for _tweet in tweet['includes']['tweets']
                                        if _tweet['id'] == referenced['id'] ][0]

                    self.assertEqual(original, twitter.original(tweet))

    def test_is_retweet_v2(self):
        """
        Test that when checking for retweets of APIv2 tweets, the function returns ``True`` only if the tweet is a retweet.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if any( referenced['type'] == 'retweeted' for referenced in tweet['data'].get('referenced_tweets', { }) ):
                    found = True
                    self.assertTrue(twitter.is_retweet(tweet))
                else:
                    self.assertFalse(twitter.is_retweet(tweet))

        if not found:
            logger.warning("Trivial test (test_is_retweet_v2)")

    def test_is_retweet_v2_only_one(self):
        """
        Test that APIv2 tweets may only include one retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    retweet = [ referenced for referenced in tweet['data']['referenced_tweets']
                                           if referenced['type'] == 'retweeted' ]
                    self.assertEqual(1, len(retweet))

    def test_is_retweet_v2_has_matching_id(self):
        """
        Test that when retweets in APIv2 tweets include a tweet with a matching referenced ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    retweet = [ referenced for referenced in tweet['data']['referenced_tweets']
                                           if referenced['type'] == 'retweeted' ]
                    self.assertTrue(any( referenced['id'] == retweet[0]['id'] for referenced in tweet['includes']['tweets'] ))

    def test_is_quote(self):
        """
        Test that when checking for quotes, the function returns ``True`` only if the ``quoted_status`` key is set.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if 'quoted_status' in tweet:
                    found = True
                    self.assertTrue(twitter.is_quote(tweet))
                else:
                    self.assertFalse(twitter.is_quote(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_is_quote_v2(self):
        """
        Test that when checking for quotes, the function returns ``True`` only if the tweet is a quoted tweet.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if any( referenced['type'] == 'quoted' for referenced in tweet['data'].get('referenced_tweets', { }) ):
                    found = True
                    self.assertTrue(twitter.is_quote(tweet))

                # if the tweet is marked as a quote but a quoted tweet isn't referenced from the top-level tweet, it must be a retweeted quote
                if not any( referenced['type'] == 'quoted' for referenced in tweet['data'].get('referenced_tweets', { }) ) and twitter.is_quote(tweet):
                    self.assertTrue(twitter.is_retweet(tweet))
                    original = twitter.original(tweet)
                    self.assertTrue(any( referenced['type'] == 'quoted' for referenced in original.get('referenced_tweets', { }) ))

        if not found:
            logger.warning('Trivial test')

    def test_is_quote_v2_only_one(self):
        """
        Test that APIv2 tweets may only include one quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)

                if twitter.is_quote(tweet):
                    if twitter.is_retweet(tweet):
                        referenced = [ referenced for referenced in tweet['data']['referenced_tweets']
                                                  if referenced['type'] == 'retweeted' ][0]
                        original = [ _tweet for _tweet in tweet['includes']['tweets']
                                            if _tweet['id'] == referenced['id'] ][0]
                        quoted = [ referenced for referenced in original['referenced_tweets']
                                               if referenced['type'] == 'quoted' ]
                        self.assertEqual(1, len(quoted))
                    else:
                        quoted = [ referenced for referenced in tweet['data']['referenced_tweets']
                                               if referenced['type'] == 'quoted' ]
                        self.assertEqual(1, len(quoted))

    def test_is_quote_v2_has_matching_id(self):
        """
        Test that APIv2 quoted tweets include a tweet with a matching referenced ID.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                # if a tweet is a quote but it has been retweeted, the top-level tweet will only refer to it as a retweet
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    quoted = [ referenced for referenced in tweet['data']['referenced_tweets']
                                           if referenced['type'] == 'quoted' ][0]
                    self.assertTrue(any( referenced['id'] == quoted['id'] for referenced in tweet['includes']['tweets'] ))

    def test_is_quote_retweet(self):
        """
        Test that when checking for quotes, if the quote is retweeted, the function returns ``True``.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if 'quoted_status' in tweet and 'retweeted_status' in tweet:
                    found = True
                    self.assertTrue(twitter.is_retweet(tweet))
                    self.assertTrue(twitter.is_quote(tweet))
                elif not 'quoted_status' in tweet and not 'retweeted_status' in tweet:
                    self.assertFalse(twitter.is_quote(tweet))
                    self.assertFalse(twitter.is_retweet(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_is_quote_v2_retweet(self):
        """
        Test that when checking for quotes, if the quote is retweeted, the function returns ``True`` for both checks.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    id = [ referenced['id'] for referenced in tweet['data']['referenced_tweets']
                                      if referenced['type'] == 'retweeted' ][0]
                    original = [ _tweet for _tweet in tweet['includes']['tweets']
                                        if _tweet['id'] == id ][0]
                    if any( referenced['type'] == 'quoted' for referenced in original.get('referenced_tweets', [ ]) ):
                        found = True
                        self.assertTrue(twitter.is_quote(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_quoted(self):
        """
        Test that when getting quoted tweets, the function returns the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(tweet['quoted_status'], twitter.quoted(tweet))

    def test_quoted_v2_not_retweet(self):
        """
        Test that when getting quoted tweets that are not retweeted, the function returns the quoted tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    references = [ referenced['id'] for referenced in tweet.get('data', tweet)['referenced_tweets']
                                                    if referenced['type'] == 'quoted' ][0]
                    referenced = [ included for included in tweet['includes']['tweets']
                                            if included['id'] == references ][0]
                    self.assertEqual(referenced, twitter.quoted(tweet))

    def test_quoted_v2_retweet(self):
        """
        Test that when getting retweeted quoted tweets, the function raises a ``KeyError``
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and twitter.is_retweet(tweet):
                    self.assertRaises(KeyError, twitter.quoted, tweet)

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

    def test_is_reply_v2_all_not_replies(self):
        """
        Test that when checking for replies, the function returns ``True`` only if the tweet is a reply.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    if any( referenced['type'] == 'replied_to' for referenced in original.get('referenced_tweets', [ ]) ):
                        found = True
                        self.assertTrue(twitter.is_reply(tweet))
                    else:
                        self.assertFalse(twitter.is_reply(tweet))
                else:
                    if any( referenced['type'] == 'replied_to' for referenced in tweet.get('data', tweet)
                               .get('referenced_tweets', [ ]) ):
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

    def test_author_unknown_id(self):
        """
        Test that getting the author with an unknown ID raises a ``KeyError``.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertRaises(KeyError, twitter.author, tweet, ''.join(random.choice(string.digits)))

    def test_author_unknown_no_includes(self):
        """
        Test that getting the author from a tweet without the `includes` key raises a ``KeyError``.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertRaises(KeyError, twitter.author, twitter.original(tweet))

    def test_author_not_retweet(self):
        """
        Test that getting the author of a tweet that is not a retweet simply returns the author of the original tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    self.assertEqual(tweet['user'], twitter.author(tweet))

    def test_author_retweeted(self):
        """
        Test that getting the author of a retweet when specifying the original author's ID returns the original status' author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.original(tweet)['user'], twitter.author(tweet, twitter.user_id(twitter.original(tweet))))

    def test_author_retweeted_without_id(self):
        """
        Test that getting the author of a retweet without providing a user ID returns the retweeting author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(tweet['user'], twitter.author(tweet))

    def test_author_quoted(self):
        """
        Test that getting the author of a quoted tweet when specifying the original author's ID returns the original status' author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(tweet['quoted_status']['user'], twitter.author(tweet, twitter.user_id(twitter.quoted(tweet))))

    def test_author_quoted_without_id(self):
        """
        Test that getting the author of a retweet without providing a user ID returns the retweeting author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(tweet['user'], twitter.author(tweet))

    def test_author_v2_unknown_id(self):
        """
        Test that getting the author with an unknown ID raises a KeyError.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertRaises(KeyError, twitter.author, tweet, ''.join(random.choice(string.digits)))

    def test_author_v2_not_retweet(self):
        """
        Test that getting the author of a tweet that is not a retweet simply returns the author of the original tweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    authors = { user['id']: user for user in tweet['includes']['users'] }
                    self.assertEqual(authors[twitter.user_id(tweet)], twitter.author(tweet))

    def test_author_v2_retweeted(self):
        """
        Test that getting the author of a retweet when specifying the original author's ID returns the original status' author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    authors = { user['id']: user for user in tweet['includes']['users'] }
                    self.assertEqual(authors[twitter.user_id(twitter.original(tweet))], twitter.author(tweet, twitter.user_id(twitter.original(tweet))))

    def test_author_v2_retweeted_without_id(self):
        """
        Test that getting the author of a retweet without providing a user ID returns the retweeting author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    authors = { user['id']: user for user in tweet['includes']['users'] }
                    self.assertEqual(authors[twitter.user_id(tweet)], twitter.author(tweet))

    def test_author_v2_quoted(self):
        """
        Test that getting the author of a quoted tweet when specifying the original author's ID returns the original status' author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    authors = { user['id']: user for user in tweet['includes']['users'] }
                    self.assertEqual(authors[twitter.user_id(twitter.quoted(tweet))],
                                     twitter.author(tweet, twitter.user_id(twitter.quoted(tweet))))

    def test_author_v2_quoted_without_id(self):
        """
        Test that getting the author of a retweet without providing a user ID returns the retweeting author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    authors = { user['id']: user for user in tweet['includes']['users'] }
                    self.assertEqual(authors[twitter.user_id(twitter.original(tweet))], twitter.author(tweet))

    def test_user_id_normal(self):
        """
        Test that getting the user ID from a normal tweet simply returns the author ID.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    found = True
                    self.assertEqual(tweet['user']['id_str'], twitter.user_id(tweet))

        if not found:
            logger.warning('Trivial test: `test_user_id_normal`')

    def test_user_id_reply(self):
        """
        Test that getting the user ID from a reply simply returns the author ID.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_reply(tweet):
                    found = True
                    self.assertEqual(tweet['user']['id_str'], twitter.user_id(tweet))

        if not found:
            logger.warning('Trivial test: `test_user_id_reply`')

    def test_user_id_quoted(self):
        """
        Test that getting the user ID from a quoted tweet returns the original author's ID.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    found = True
                    self.assertEqual(twitter.quoted(tweet)['user']['id_str'], twitter.user_id(twitter.quoted(tweet)))

        if not found:
            logger.warning('Trivial test: `test_user_id_quote`')

    def test_user_id_retweeted(self):
        """
        Test that getting the user ID from a retweeted tweet returns the original author's ID.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    found = True
                    self.assertEqual(twitter.original(tweet)['user']['id_str'], twitter.user_id(twitter.original(tweet)))

        if not found:
            logger.warning('Trivial test: `test_user_id_retweeted`')

    def test_user_id_v2_normal(self):
        """
        Test that getting the user ID from a normal tweet simply returns the author ID.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    found = True
                    self.assertEqual(tweet['data']['author_id'], twitter.user_id(tweet))

        if not found:
            logger.warning('Trivial test: `test_user_id_v2_normal`')

    def test_user_id_v2_reply(self):
        """
        Test that getting the user ID from a reply simply returns the author ID.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_reply(tweet):
                    found = True
                    self.assertEqual(tweet['data']['author_id'], twitter.user_id(tweet))

        if not found:
            logger.warning('Trivial test: `test_user_id_v2_reply`')

    def test_user_id_v2_quoted(self):
        """
        Test that getting the user ID from a quoted tweet returns the original author's ID.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and twitter.is_quote(tweet):
                    found = True
                    self.assertEqual(twitter.quoted(tweet)['author_id'], twitter.user_id(twitter.quoted(tweet)))

        if not found:
            logger.warning('Trivial test: `test_user_id_v2_quote`')

    def test_user_id_v2_retweeted(self):
        """
        Test that getting the user ID from a retweeted tweet returns the original author's ID.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    found = True
                    self.assertEqual(twitter.original(tweet)['author_id'], twitter.user_id(twitter.original(tweet)))

        if not found:
            logger.warning('Trivial test: `test_user_id_v2_retweeted`')

    def test_user_favorites_returns_int(self):
        """
        Test that getting the number of user favorites returns an integer.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(int, type(twitter.user_favorites(tweet)))

    def test_user_favorites_raises_NotImplementedError(self):
        """
        Test that getting the number of user favorites from an APIv2 tweet raises a ``NotImplementedError``.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertRaises(NotImplementedError, twitter.user_favorites, tweet)

    def test_user_favorites_normal_tweet(self):
        """
        Test that getting the number of user favorites returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['favourites_count'], twitter.user_favorites(tweet))

    def test_user_favorites_normal_tweet_with_id(self):
        """
        Test that getting the number of user favorites with the author ID returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['favourites_count'], twitter.user_favorites(tweet, twitter.user_id(tweet)))

    def test_user_favorites_retweet(self):
        """
        Test that getting the number of user favorites from a retweet returns the retweeting author's favourites.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.author(tweet)['favourites_count'], twitter.user_favorites(tweet))
                    self.assertNotEqual(twitter.author(twitter.original(tweet))['favourites_count'], twitter.user_favorites(tweet))

    def test_user_favorites_retweet_with_id(self):
        """
        Test that getting the number of user favorites from a retweet with the original author's ID returns the original author's favourites.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertNotEqual(twitter.author(tweet)['favourites_count'],
                                        twitter.user_favorites(tweet, twitter.user_id(twitter.original(tweet))))
                    self.assertEqual(twitter.author(twitter.original(tweet))['favourites_count'],
                                        twitter.user_favorites(tweet, twitter.user_id(twitter.original(tweet))))

    def test_user_favorites_quoted(self):
        """
        Test that getting the number of user favorites from a quoted tweet returns the quoting author's favourites.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['favourites_count'], twitter.user_favorites(tweet))
                    if twitter.user_id(twitter.quoted(tweet)) != twitter.user_id(tweet):
                        found = True
                        self.assertNotEqual(twitter.quoted(tweet)['user']['favourites_count'], twitter.user_favorites(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_user_favorites_quoted_with_id(self):
        """
        Test that getting the number of user favorites from a quoted tweet with the original author's ID returns the original author's favourites.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    if twitter.user_id(twitter.quoted(tweet)) != twitter.user_id(tweet):
                        self.assertNotEqual(twitter.author(tweet)['favourites_count'],
                                            twitter.user_favorites(tweet, twitter.user_id(twitter.quoted(tweet))))
                        self.assertEqual(twitter.author(twitter.quoted(tweet))['favourites_count'],
                                            twitter.user_favorites(tweet, twitter.user_id(twitter.quoted(tweet))))

    def test_user_statuses_returns_int(self):
        """
        Test that getting the number of user statuses returns an integer.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(int, type(twitter.user_statuses(tweet)))

    def test_user_statuses_v2_returns_int(self):
        """
        Test that getting the number of user statuses returns an integer.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(int, type(twitter.user_statuses(tweet)))

    def test_user_statuses_normal_tweet(self):
        """
        Test that getting the number of user statuses returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['statuses_count'], twitter.user_statuses(tweet))

    def test_user_statuses_normal_tweet_with_id(self):
        """
        Test that getting the number of user statuses with the author ID returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['statuses_count'], twitter.user_statuses(tweet, twitter.user_id(tweet)))

    def test_user_statuses_v2_normal_tweet(self):
        """
        Test that getting the number of user statuses returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['public_metrics']['tweet_count'], twitter.user_statuses(tweet))

    def test_user_statuses_v2_normal_tweet_with_id(self):
        """
        Test that getting the number of user statuses with the author ID returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['public_metrics']['tweet_count'], twitter.user_statuses(tweet, twitter.user_id(tweet)))

    def test_user_statuses_retweet(self):
        """
        Test that getting the number of user statuses from a retweet returns the retweeting author's tweets.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.author(tweet)['statuses_count'], twitter.user_statuses(tweet))
                    self.assertNotEqual(twitter.original(tweet)['user']['statuses_count'], twitter.user_statuses(tweet))

    def test_user_statuses_retweet_with_id(self):
        """
        Test that getting the number of user statuses from a retweet with the original author's ID returns the original author's tweets.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertNotEqual(twitter.author(tweet)['statuses_count'],
                                        twitter.user_statuses(tweet, twitter.user_id(twitter.original(tweet))))
                    self.assertEqual(twitter.author(twitter.original(tweet))['statuses_count'],
                                        twitter.user_statuses(tweet, twitter.user_id(twitter.original(tweet))))

    def test_user_statuses_v2_retweet(self):
        """
        Test that getting the number of user statuses from a retweet returns the retweeting author's tweets.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.author(tweet)['public_metrics']['tweet_count'], twitter.user_statuses(tweet))

    def test_user_statuses_v2_retweet_with_id(self):
        """
        Test that getting the number of user statuses from a retweet with the original author's ID returns the original author's tweets.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    if twitter.author(tweet) == twitter.author(tweet, twitter.original(tweet)['author_id']):
                        continue

                    self.assertNotEqual(twitter.author(tweet)['public_metrics']['tweet_count'],
                                        twitter.user_statuses(tweet, twitter.user_id(twitter.original(tweet))))
                    self.assertEqual(twitter.author(tweet, twitter.user_id(twitter.original(tweet)))['public_metrics']['tweet_count'],
                                        twitter.user_statuses(tweet, twitter.user_id(twitter.original(tweet))))

    def test_user_statuses_quoted(self):
        """
        Test that getting the number of user statuses from a quoted tweet returns the quoting author's tweets.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['statuses_count'], twitter.user_statuses(tweet))
                    if twitter.user_id(twitter.quoted(tweet)) != twitter.user_id(tweet):
                        found = True
                        self.assertNotEqual(twitter.quoted(tweet)['user']['statuses_count'], twitter.user_statuses(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_user_statuses_quoted_with_id(self):
        """
        Test that getting the number of user statuses from a quoted tweet with the original author's ID returns the original author's tweets.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    if twitter.user_id(tweet) == twitter.user_id(twitter.quoted(tweet)):
                        continue

                    found = True
                    self.assertNotEqual(twitter.author(tweet)['statuses_count'],
                                        twitter.user_statuses(tweet, twitter.user_id(twitter.quoted(tweet))))
                    self.assertEqual(twitter.author(twitter.quoted(tweet))['statuses_count'],
                                        twitter.user_statuses(tweet, twitter.user_id(twitter.quoted(tweet))))

        if not found:
            logger.warning('Trivial test')

    def test_user_statuses_v2_quoted(self):
        """
        Test that getting the number of user statuses from a quoted tweet returns the quoting author's tweets.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['public_metrics']['tweet_count'], twitter.user_statuses(tweet))
                    if not twitter.is_retweet(tweet) and twitter.user_id(twitter.quoted(tweet)) != twitter.user_id(tweet):
                        self.assertNotEqual(twitter.author(tweet, twitter.user_id(twitter.quoted(tweet)))['public_metrics']['tweet_count'],
                                            twitter.user_statuses(tweet))

    def test_user_statuses_v2_quoted_with_id(self):
        """
        Test that getting the number of user statuses from a quoted tweet with the original author's ID returns the original author's tweets.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    if twitter.author(tweet) == twitter.author(tweet, twitter.user_id(twitter.quoted(tweet))):
                        continue

                    found = True
                    self.assertNotEqual(twitter.author(tweet)['public_metrics']['tweet_count'],
                                        twitter.user_statuses(tweet, twitter.user_id(twitter.quoted(tweet))))
                    self.assertEqual(twitter.author(tweet, twitter.user_id(twitter.quoted(tweet)))['public_metrics']['tweet_count'],
                                        twitter.user_statuses(tweet, twitter.user_id(twitter.quoted(tweet))))

        if not found:
            logger.warning('Trivial test')

    def test_user_followers_returns_int(self):
        """
        Test that getting the number of user followers returns an integer.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(int, type(twitter.user_followers(tweet)))

    def test_user_followers_v2_returns_int(self):
        """
        Test that getting the number of user followers returns an integer.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertEqual(int, type(twitter.user_followers(tweet)))

    def test_user_followers_normal_tweet(self):
        """
        Test that getting the number of user followers returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['followers_count'], twitter.user_followers(tweet))

    def test_user_followers_normal_tweet_with_id(self):
        """
        Test that getting the number of user followers with the author ID returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['followers_count'], twitter.user_followers(tweet, twitter.user_id(tweet)))

    def test_user_followers_v2_normal_tweet(self):
        """
        Test that getting the number of user followers returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['public_metrics']['followers_count'], twitter.user_followers(tweet))

    def test_user_followers_v2_normal_tweet_with_id(self):
        """
        Test that getting the number of user followers with the author ID returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['public_metrics']['followers_count'], twitter.user_followers(tweet, twitter.user_id(tweet)))

    def test_user_followers_retweet(self):
        """
        Test that getting the number of user followers from a retweet returns the retweeting author's followers.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.author(tweet)['followers_count'], twitter.user_followers(tweet))
                    self.assertNotEqual(twitter.original(tweet)['user']['followers_count'], twitter.user_followers(tweet))

    def test_user_followers_retweet_with_id(self):
        """
        Test that getting the number of user followers from a retweet with the original author's ID returns the original author's followers.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertNotEqual(twitter.author(tweet)['followers_count'],
                                        twitter.user_followers(tweet, twitter.user_id(twitter.original(tweet))))
                    self.assertEqual(twitter.author(twitter.original(tweet))['followers_count'],
                                        twitter.user_followers(tweet, twitter.user_id(twitter.original(tweet))))

    def test_user_followers_v2_retweet(self):
        """
        Test that getting the number of user followers from a retweet returns the retweeting author's followers.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.author(tweet)['public_metrics']['followers_count'], twitter.user_followers(tweet))

    def test_user_followers_v2_retweet_with_id(self):
        """
        Test that getting the number of user followers from a retweet with the original author's ID returns the original author's followers.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    if twitter.author(tweet) == twitter.author(tweet, twitter.user_id(twitter.original(tweet))):
                        continue

                    self.assertNotEqual(twitter.author(tweet)['public_metrics']['followers_count'],
                                        twitter.user_followers(tweet, twitter.user_id(twitter.original(tweet))))
                    self.assertEqual(twitter.author(tweet, twitter.user_id(twitter.original(tweet)))['public_metrics']['followers_count'],
                                        twitter.user_followers(tweet, twitter.user_id(twitter.original(tweet))))

    def test_user_followers_quoted(self):
        """
        Test that getting the number of user followers from a quoted tweet returns the quoting author's followers.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['followers_count'], twitter.user_followers(tweet))
                    if twitter.user_id(twitter.quoted(tweet)) != twitter.user_id(tweet):
                        found = True
                        self.assertNotEqual(twitter.quoted(tweet)['user']['followers_count'], twitter.user_followers(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_user_followers_quoted_with_id(self):
        """
        Test that getting the number of user followers from a quoted tweet with the original author's ID returns the original author's followers.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    if twitter.user_id(tweet) == twitter.user_id(twitter.quoted(tweet)):
                        continue

                    found = True
                    self.assertNotEqual(twitter.author(tweet)['followers_count'],
                                        twitter.user_followers(tweet, twitter.user_id(twitter.quoted(tweet))))
                    self.assertEqual(twitter.author(twitter.quoted(tweet))['followers_count'],
                                        twitter.user_followers(tweet, twitter.user_id(twitter.quoted(tweet))))

        if not found:
            logger.warning('Trivial test')

    def test_user_followers_v2_quoted(self):
        """
        Test that getting the number of user followers from a quoted tweet returns the quoting author's followers.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['public_metrics']['followers_count'], twitter.user_followers(tweet))
                    if not twitter.is_retweet(tweet) and twitter.user_id(twitter.quoted(tweet)) != twitter.user_id(tweet):
                        self.assertNotEqual(twitter.author(tweet, twitter.user_id(twitter.quoted(tweet)))['public_metrics']['followers_count'],
                                            twitter.user_followers(tweet))

    def test_user_followers_v2_quoted_with_id(self):
        """
        Test that getting the number of user followers from a quoted tweet with the original author's ID returns the original author's followers.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    if twitter.author(tweet) == twitter.author(tweet, twitter.user_id(twitter.quoted(tweet))):
                        continue

                    found = True
                    self.assertNotEqual(twitter.author(tweet)['public_metrics']['followers_count'],
                                        twitter.user_followers(tweet, twitter.user_id(twitter.quoted(tweet))))
                    self.assertEqual(twitter.author(tweet, twitter.user_id(twitter.quoted(tweet)))['public_metrics']['followers_count'],
                                        twitter.user_followers(tweet, twitter.user_id(twitter.quoted(tweet))))

        if not found:
            logger.warning('Trivial test')

    def test_user_description_returns_str_or_none(self):
        """
        Test that getting the description returns a string or ``None``.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                description = twitter.user_description(tweet)
                self.assertTrue(description is None or type(description) == str)

    def test_user_description_v2_returns_str_or_none(self):
        """
        Test that getting the description returns a string or ``None`.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                description = twitter.user_description(tweet)
                self.assertTrue(description is None or type(description) == str)

    def test_user_description_normal_tweet(self):
        """
        Test that getting the description returns the correct description.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['description'], twitter.user_description(tweet))

    def test_user_description_normal_tweet_with_id(self):
        """
        Test that getting the user description with the author ID returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['description'], twitter.user_description(tweet, twitter.user_id(tweet)))

    def test_user_description_v2_normal_tweet(self):
        """
        Test that getting the description returns the correct description.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['description'], twitter.user_description(tweet))

    def test_user_description_v2_normal_tweet_with_id(self):
        """
        Test that getting the user description with the author ID returns the correct number.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet) and not twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['description'], twitter.user_description(tweet, twitter.user_id(tweet)))

    def test_user_description_retweet(self):
        """
        Test that getting the description from a retweet returns the retweeting author's description.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.author(tweet)['description'], twitter.user_description(tweet))
                    self.assertNotEqual(twitter.original(tweet)['user']['followers_count'], twitter.user_description(tweet))

    def test_user_description_retweet_with_id(self):
        """
        Test that getting the user description from a retweet with the original author's ID returns the original author's description.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    if tweet['user']['description'] == twitter.original(tweet)['user']['description']:
                        continue

                    self.assertNotEqual(twitter.author(tweet)['description'],
                                        twitter.user_description(tweet, twitter.user_id(twitter.original(tweet))))
                    self.assertEqual(twitter.author(twitter.original(tweet))['description'],
                                        twitter.user_description(tweet, twitter.user_id(twitter.original(tweet))))

    def test_user_description_v2_retweet(self):
        """
        Test that getting the description from a retweet returns the retweeting author's description.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.author(tweet)['description'], twitter.user_description(tweet))

    def test_user_description_v2_retweet_with_id(self):
        """
        Test that getting the user description from a retweet with the original author's ID returns the original author's description.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    if twitter.author(tweet)['description'] == twitter.author(tweet, twitter.user_id(twitter.original(tweet)))['description']:
                        continue

                    self.assertNotEqual(twitter.author(tweet)['description'],
                                        twitter.user_description(tweet, twitter.user_id(twitter.original(tweet))))
                    self.assertEqual(twitter.author(tweet, twitter.user_id(twitter.original(tweet)))['description'],
                                        twitter.user_description(tweet, twitter.user_id(twitter.original(tweet))))

    def test_user_description_quoted(self):
        """
        Test that getting the description from a quoted tweet returns the quoting author's description.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['description'], twitter.user_description(tweet))
                    if twitter.user_id(twitter.quoted(tweet)) != twitter.user_id(tweet):
                        found = True
                        self.assertNotEqual(twitter.quoted(tweet)['user']['followers_count'], twitter.user_description(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_user_description_quoted_with_id(self):
        """
        Test that getting the user description from a quoted tweet with the original author's ID returns the original author's description.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    if twitter.user_id(tweet) == twitter.user_id(twitter.quoted(tweet)):
                        continue

                    found = True
                    self.assertNotEqual(twitter.author(tweet)['description'],
                                        twitter.user_description(tweet, twitter.user_id(twitter.quoted(tweet))))
                    self.assertEqual(twitter.author(twitter.quoted(tweet))['description'],
                                        twitter.user_description(tweet, twitter.user_id(twitter.quoted(tweet))))

        if not found:
            logger.warning('Trivial test')

    def test_user_description_v2_quoted(self):
        """
        Test that getting the description from a quoted tweet returns the quoting author's description.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet):
                    self.assertEqual(twitter.author(tweet)['description'], twitter.user_description(tweet))

    def test_user_description_v2_quoted_with_id(self):
        """
        Test that getting the user description from a quoted tweet with the original author's ID returns the original author's description.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_quote(tweet) and not twitter.is_retweet(tweet):
                    if twitter.author(tweet)['description'] == twitter.author(tweet, twitter.user_id(twitter.quoted(tweet)))['description']:
                        continue

                    found = True
                    self.assertNotEqual(twitter.author(tweet)['description'],
                                        twitter.user_description(tweet, twitter.user_id(twitter.quoted(tweet))))
                    self.assertEqual(twitter.author(tweet, twitter.user_id(twitter.quoted(tweet)))['description'],
                                        twitter.user_description(tweet, twitter.user_id(twitter.quoted(tweet))))

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
                if twitter.author(tweet)['verified']:
                    found = True
                    self.assertTrue(twitter.is_verified(tweet))
                else:
                    self.assertFalse(twitter.is_verified(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_is_verified_not_verified_retweet(self):
        """
        Test that when checking whether a retweet is from a verified author, the retweeting author is checked.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    continue

                if twitter.author(tweet)['verified'] and not twitter.author(tweet, twitter.user_id(twitter.original(tweet)))['verified']:
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

                if not twitter.author(tweet)['verified'] and twitter.author(tweet, twitter.user_id(twitter.original(tweet)))['verified']:
                    found = True
                    self.assertFalse(twitter.is_verified(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_is_verified_retweet(self):
        """
        Test that checking whether the author of a retweeted tweet is verified returns ``True`` only if the author is verified.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    if twitter.author(tweet, twitter.user_id(original))['verified']:
                        found = True
                        self.assertTrue(twitter.is_verified(tweet, twitter.user_id(original)))
                    else:
                        self.assertFalse(twitter.is_verified(tweet, twitter.user_id(original)))

        if not found:
            logger.warning('Trivial test')

    def test_is_verified_v2(self):
        """
        Test that when checking whether the tweet is from a verified author, the function returns ``True`` only if the author is verified.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.author(tweet)['verified']:
                    self.assertTrue(twitter.is_verified(tweet))
                else:
                    self.assertFalse(twitter.is_verified(tweet))

    def test_is_verified_v2_not_verified_retweet(self):
        """
        Test that when checking whether a retweet is from a verified author, the retweeting author is checked.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    continue

                if twitter.author(tweet)['verified'] and not twitter.author(tweet, twitter.user_id(twitter.original(tweet)))['verified']:
                    found = True
                    self.assertTrue(twitter.is_verified(tweet))

        if not found:
            logger.warning('Trivial test')

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if not twitter.is_retweet(tweet):
                    continue

                if not twitter.author(tweet)['verified'] and twitter.author(tweet, twitter.user_id(twitter.original(tweet)))['verified']:
                    found = True
                    self.assertFalse(twitter.is_verified(tweet))

        if not found:
            logger.warning('Trivial test')

    def test_is_verified_v2_retweet(self):
        """
        Test that checking whether the author of a retweeted tweet is verified returns ``True`` only if the author is verified.
        """

        found = False
        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if twitter.is_retweet(tweet):
                    original = twitter.original(tweet)
                    if twitter.author(tweet, original['author_id'])['verified']:
                        found = True
                        self.assertTrue(twitter.is_verified(tweet, twitter.user_id(original)))
                    else:
                        self.assertFalse(twitter.is_verified(tweet, twitter.user_id(original)))

        if not found:
            logger.warning('Trivial test')

    def is_acceptable_mention(self, text):
        """
        Check whether any mentions in the given text are acceptable.
        This happens when the mention is not actually a mention, but just an @, or an @ linking to a broken handle.

        :param text: The text to check for validity.
        :type text: str

        :return: A boolean indicating whether any mentions are acceptable.
                 If at least one is acceptable, the function returns True, essentially ending the test for the tweet.
        :rtype: bool
        """

        wrong_pattern = re.compile("@[0-9,\\s…]")
        no_space_pattern = re.compile("[^\\s]@")
        end_pattern = re.compile('@$')

        """
        Allow for some manual validation.
        """
        not_accounts = [ 'real_realestsounds', 'nevilleiesta', 'naija927', 'naijafm92.7', 'manchesterunited', 'ManchesterUnited',
                         'clintasena', 'Maksakal88', 'Aubamayeng7', 'JustWenginIt', 'marcosrojo5', 'btsportsfootball',
                         'Nsibirwahall', 'YouTubeより', 'juniorpepaseed', 'Mezieblog', 'UtdAlamin', 'spurs_vincente',
                         '@sports_sell', '@Coast2CoastFM', '@Scottangus12' ]
        if '@' in text:
            if '@@' in text or ' @ ' in text or '@&gt;' in text or any(account in text for account in not_accounts):
                return True
            if end_pattern.findall(text):
                return True
            if no_space_pattern.findall(text):
                return True
            if wrong_pattern.findall(text):
                return True

        return False

    def test_expand_mentions(self):
        """
        Test replacing mentions in a sample tweet.
        """

        text = "Python visualization library Multiplex: It looks amazing, great job  @NicholasMamo"
        tweet = { 'entities':
                    { 'user_mentions':
                        [ {
                            "screen_name": "NicholasMamo",
                            "name": "Nicholas Mamo",
                        } ]
                    },
                  'id_str': random.randint(0, 100)
                }
        self.assertEqual("Python visualization library Multiplex: It looks amazing, great job  Nicholas Mamo", twitter.expand_mentions(text, tweet))

    def test_expand_mentions_case_insensitive(self):
        """
        Test that when replacing mentions, the replacement is case-insensitive.
        """

        text = "Python visualization library Multiplex: It looks amazing, great job  @nicholasmamo"
        tweet = { 'entities':
                    { 'user_mentions':
                        [ {
                            "screen_name": "NicholasMamo",
                            "name": "Nicholas Mamo",
                        } ]
                    },
                  'id_str': random.randint(0, 100)
                }
        self.assertEqual("Python visualization library Multiplex: It looks amazing, great job  Nicholas Mamo", twitter.expand_mentions(text, tweet))

    def test_expand_mentions_multiple_times(self):
        """
        Test that when a mention appears multiple times, all such mentions are replaced.
        """

        text = "Python visualization library Multiplex by @NicholasMamo: It looks amazing, great job  @nicholasmamo"
        tweet = { 'entities':
                    { 'user_mentions':
                        [ {
                            "screen_name": "NicholasMamo",
                            "name": "Nicholas Mamo",
                        } ]
                    },
                  'id_str': random.randint(0, 100)
                }
        self.assertEqual("Python visualization library Multiplex by Nicholas Mamo: It looks amazing, great job  Nicholas Mamo", twitter.expand_mentions(text, tweet))

    def test_expand_mentions_several(self):
        """
        Test that when there are several mentions, they are all replaced.
        """

        text = "RT @Quantum_Stat: Python visualization library Multiplex: It looks amazing, great job  @nicholasmamo"
        tweet = { 'entities':
                    { 'user_mentions':
                        [ {
                            "screen_name": "NicholasMamo",
                            "name": "Nicholas Mamo",
                        }, {
                            "screen_name": "Quantum_Stat",
                            "name": "Quantum Stat",
                        } ]
                    },
                  'id_str': random.randint(0, 100)
                }
        self.assertEqual("RT Quantum Stat: Python visualization library Multiplex: It looks amazing, great job  Nicholas Mamo", twitter.expand_mentions(text, tweet))

    def test_expand_mentions_retain_unknown(self):
        """
        Test that when there are unknown mentions, they are retained.
        """

        text = "RT @Quantum_Stat: Python visualization library Multiplex: It looks amazing, great job  @nicholasmamo"
        tweet = { 'entities':
                    { 'user_mentions':
                        [ {
                            "screen_name": "NicholasMamo",
                            "name": "Nicholas Mamo",
                        } ]
                    },
                  'id_str': random.randint(0, 100)
                }
        self.assertEqual("RT @Quantum_Stat: Python visualization library Multiplex: It looks amazing, great job  Nicholas Mamo", twitter.expand_mentions(text, tweet))

    def test_expand_mentions_correct(self):
        """
        Test that mentions are replaced correctly.
        """

        text = "RT @Quantum_Stat: From the latest @Quantum_Stat newsletter: Python visualization library Multiplex: It looks amazing, great job  @nicholasmamo"
        tweet = { 'entities':
                    { 'user_mentions':
                        [ {
                            "screen_name": "NicholasMamo",
                            "name": "Nicholas Mamo",
                        }, {
                            "screen_name": "Quantum_Stat",
                            "name": "Quantum Stat",
                        } ]
                    },
                  'id_str': random.randint(0, 100)
                }
        self.assertEqual("RT Quantum Stat: From the latest Quantum Stat newsletter: Python visualization library Multiplex: It looks amazing, great job  Nicholas Mamo", twitter.expand_mentions(text, tweet))

    def test_expand_mentions_all(self):
        """
        Test that after replacing mentions, there are no '@' symbols.
        """

        no_space_pattern = re.compile("[^\\s]@")

        corpus = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'understanding', 'CRYCHE.json')
        with open(corpus) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                original = tweet
                while twitter.is_retweet(tweet):
                    tweet = twitter.original(tweet)

                if "extended_tweet" in tweet:
                    text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
                else:
                    text = tweet.get("text", "")

                if twitter.is_quote(tweet):
                    tweet = twitter.quoted(tweet)
                    if "extended_tweet" in tweet:
                        text += ' ' + tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
                    else:
                        text += ' ' + tweet.get("text", "")

                cleaned = twitter.expand_mentions(text, original)

                if self.is_acceptable_mention(cleaned) or no_space_pattern.findall(text):
                    continue

                self.assertFalse('@' in cleaned)

    def test_expand_mentions_v2_all(self):
        """
        Test that after replacing mentions, there are no '@' symbols.
        """

        no_space_pattern = re.compile("[^\\s]@")

        corpus = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json')
        with open(corpus) as f:
            for i, line in enumerate(f):
                tweet = json.loads(line)
                original = tweet
                text = twitter.full_text(tweet)

                cleaned = twitter.expand_mentions(text, original)

                acceptable = { '1506646715029667843', # not a whole world
                               '1506646740182708224' } # Russian?
                if self.is_acceptable_mention(cleaned) or tweet['data']['id'] in acceptable or no_space_pattern.findall(text):
                    continue

                # mentions in the original tweet do not have user information, so they cannot be expanded
                self.assertTrue('@' not in cleaned or sum( len(included['entities'].get('mentions', [ ]))
                                                           for included in tweet['includes'].get('tweets', [ ]) ))

    def test_expand_mentions_none(self):
        """
        Test expanding mentions from a corpus where one user has an empty display name.
        """

        corpus = os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', '#CeltaSevillaFC.json')
        with open(corpus) as f:
            for line in f:
                tweet = json.loads(line)
                text = twitter.full_text(tweet)
                text = twitter.expand_mentions(text, tweet)

                if self.is_acceptable_mention(text):
                    continue

                self.assertFalse('@' in text)
