"""
Test the functionality of the collect tool.
"""

import json
import os
import sys
import time
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..'),
          os.path.join(os.path.dirname(__file__), '..', '..', 'eventdt') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import collect
from logger import logger
logger.set_logging_level(logger.LogLevel.ERROR)

class TestCollect(unittest.TestCase):
    """
    Test the functionality of the collect tool.
    """

    def test_setup_rules_one_per_keyword(self):
        """
        Test that one rule is created for each keyword.
        """

        keywords = [ "Olympique Lyonnais", "Malta" ]
        rules = collect.setup_rules(keywords)
        self.assertEqual(len(keywords), len(rules))

    def test_setup_rules_list_of_dict(self):
        """
        Test that the created rules are returned as a list of dictionaries.
        """

        keywords = [ "Olympique Lyonnais", "Malta" ]
        rules = collect.setup_rules(keywords)
        self.assertEqual(list, type(rules))
        self.assertTrue(all( type(rule) is dict for rule in rules ))

    def test_setup_rules_keywords_unchanged(self):
        """
        Test that the keywords do not change in the rules.

        The function uses `startswith` instead of checking for equivalence since it depends on
        """

        keywords = [ "(Olympique OR Lyonnais)", "Malta" ]
        rules = collect.setup_rules(keywords)
        for keyword, rule in zip(keywords, rules):
            self.assertTrue(rule['value'].startswith(keyword))

    def test_setup_rules_no_lang(self):
        """
        Test that when no language is provided, the keywords include no language option.
        """

        keywords = [ "(Olympique OR Lyonnais)", "Malta" ]
        rules = collect.setup_rules(keywords, lang=None)
        self.assertTrue(all( 'lang' not in rule['value'] for rule in rules ))

    def test_setup_rules_lang_all(self):
        """
        Test that when a language is provided, it appears in every rule.
        """

        keywords = [ "(Olympique OR Lyonnais)", "Malta" ]
        rules = collect.setup_rules(keywords, lang='en')
        self.assertTrue(all( 'lang:en' in rule['value'] for rule in rules ))

    def test_set_rules_with_retweets(self):
        """
        Test that when accepting retweets, none of the rules have any flags relating to retweets.
        """

        keywords = [ "(Olympique OR Lyonnais)", "Malta" ]
        rules = collect.setup_rules(keywords, no_retweets=False)
        self.assertTrue(all( 'is:retweet' not in rule['value'] for rule in rules ))

    def test_setup_rules_no_retweets_all(self):
        """
        Test that when retweets should be excluded, all rules reject retweets.
        """

        keywords = [ "(Olympique OR Lyonnais)", "Malta" ]
        rules = collect.setup_rules(keywords, no_retweets=True)
        self.assertTrue(all( '-is:retweet' in rule['value'] for rule in rules ))

    def test_setup_rules_tags_exclude_options(self):
        """
        Test that the rules include only the keywords and no other options.
        """

        keywords = [ "(Olympique OR Lyonnais)", "Malta" ]
        rules = collect.setup_rules(keywords, no_retweets=True, lang='en')
        for keyword, rule in zip(keywords, rules):
            self.assertEqual(keyword, rule['tag'])
