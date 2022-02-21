"""
Test the functionality of the Streamv2 class.
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
from listeners import BearerTokenAuth, Streamv2

class TestStreamv2(unittest.TestCase):
    """
    Test the functionality of the Streamv2.
    """

    def test_get_all_rules_list(self):
        """
        Test that initially, all the rules are empty.
        """

        auth = BearerTokenAuth(conf.ACCOUNTS[2]['CONSUMER_KEY'], conf.ACCOUNTS[2]['CONSUMER_SECRET'])
        stream = Streamv2(auth)
        self.assertEqual(list, type(stream.get_all_rules()))

    def test_get_all_rules_none(self):
        """
        Test that if there are no rules, getting all rules still returns an empty list instead of failing.
        """

        auth = BearerTokenAuth(conf.ACCOUNTS[2]['CONSUMER_KEY'], conf.ACCOUNTS[2]['CONSUMER_SECRET'])
        stream = Streamv2(auth)
        stream.delete_all_rules()
        self.assertEqual([ ], stream.get_all_rules())

    def test_delete_rules(self):
        """
        Test that after deleting rules, there really are no rules left.
        """

        auth = BearerTokenAuth(conf.ACCOUNTS[2]['CONSUMER_KEY'], conf.ACCOUNTS[2]['CONSUMER_SECRET'])
        stream = Streamv2(auth)
        rules = [{ 'value': 'olympique lyonnais lang:en' , 'tag': 'test'}]
        stream.set_rules(rules)
        stream.delete_all_rules()
        self.assertFalse(stream.get_all_rules())

    def test_delete_rules_returns_list(self):
        """
        Test that when deleting rules, the function returns an empty list.
        """

        auth = BearerTokenAuth(conf.ACCOUNTS[2]['CONSUMER_KEY'], conf.ACCOUNTS[2]['CONSUMER_SECRET'])
        stream = Streamv2(auth)
        rules = [{ 'value': 'olympique lyonnais lang:en' , 'tag': 'test'}]
        stream.set_rules(rules)
        stream.delete_all_rules()
        self.assertEqual([ ], stream.get_all_rules())

    def test_delete_rules_no_rules(self):
        """
        Test that when deleting rules but there are none, the function still returns an empty list instead of failing.
        """

        auth = BearerTokenAuth(conf.ACCOUNTS[2]['CONSUMER_KEY'], conf.ACCOUNTS[2]['CONSUMER_SECRET'])
        stream = Streamv2(auth)
        rules = [{ 'value': 'olympique lyonnais lang:en' , 'tag': 'test'}]
        stream.set_rules(rules)
        stream.delete_all_rules()
        stream.delete_all_rules() # delete the rules twice
        self.assertEqual([ ], stream.get_all_rules())
