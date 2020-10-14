"""
Test the functionality of the TweetrListener.
"""

import json
import os
import sys
import time
import unittest

from datetime import datetime
from tweepy import OAuthHandler, Stream

paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from config import conf
from listeners import TweetListener

class TestTweetListener(unittest.TestCase):
    """
    Test the functionality of the TweetrListener.
    """

    def clean(f):
        """
        A decorator that removes the data file after writing it to a file.
        """

        def wrapper(*args, **kwargs):
            """
            The function first calls the test and then removes the data file, assumed to be called `data.json`.
            """

            f(*args, **kwargs)
            os.remove(os.path.join(os.path.dirname(__file__), 'data.json'))

        return wrapper

    def authenticate(self):
        """
        Create the authentication object.

        :return: The authentication object.
        :rtype: :class:`tweepy.OAuthHandler`
        """

        auth = OAuthHandler(conf.ACCOUNTS[0]['CONSUMER_KEY'], conf.ACCOUNTS[0]['CONSUMER_SECRET'])
        auth.set_access_token(conf.ACCOUNTS[0]['ACCESS_TOKEN'], conf.ACCOUNTS[0]['ACCESS_TOKEN_SECRET'])
        return auth

    @clean
    def test_collect(self):
        """
        Test collecting data very simply.
        """

        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'w') as f:
            listener = TweetListener(f, max_time=2)
            stream = Stream(self.authenticate(), listener)
            stream.filter(track=[ 'is' ])

        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'r') as f:
            lines = f.readlines()
            self.assertTrue(lines)
            for line in lines:
                self.assertTrue('id' in json.loads(line))

    @clean
    def test_collect_filtered(self):
        """
        Test collecting data with a few attributes.
        """

        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'w') as f:
            listener = TweetListener(f, max_time=2, attributes=[ 'id', 'text' ])
            stream = Stream(self.authenticate(), listener)
            stream.filter(track=[ 'is' ])

        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'r') as f:
            lines = f.readlines()
            self.assertTrue(lines)
            for line in lines:
                self.assertEqual(set([ 'id', 'text' ]), set(json.loads(line)))

    @clean
    def test_collect_empty_attribute_list(self):
        """
        Test that collecting data with an empty attribute list returns everything.
        """

        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'w') as f:
            listener = TweetListener(f, max_time=2, attributes=[ ])
            stream = Stream(self.authenticate(), listener)
            stream.filter(track=[ 'is' ])

        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'r') as f:
            lines = f.readlines()
            self.assertTrue(lines)
            for line in lines:
                self.assertLessEqual(10, len(json.loads(line)))

    @clean
    def test_collect_none_attribute(self):
        """
        Test that collecting data with `None` as the attributes returns everything.
        """

        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'w') as f:
            listener = TweetListener(f, max_time=2, attributes=None)
            stream = Stream(self.authenticate(), listener)
            stream.filter(track=[ 'is' ])

        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'r') as f:
            lines = f.readlines()
            self.assertTrue(lines)
            for line in lines:
                self.assertLessEqual(10, len(json.loads(line)))

    @clean
    def test_collect_time(self):
        """
        Test that when collecting data, the time limit is respected.
        """

        start = time.time()
        with open(os.path.join(os.path.dirname(__file__), 'data.json'), 'w') as f:
            listener = TweetListener(f, max_time=3, attributes=[ ])
            stream = Stream(self.authenticate(), listener)
            stream.filter(track=[ 'is' ])
        self.assertEqual(3, round(time.time() - start))
