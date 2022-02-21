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
