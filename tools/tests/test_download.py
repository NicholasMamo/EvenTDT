"""
Test the functionality of the download tool.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..'),
           os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from eventdt import twitter
import download as tool
import tools

class TestDownload(unittest.TestCase):
    """
    Test the functionality of the download tool.
    """

    def test_download_full_tweet_objects(self):
        """
        Test that when downloading tweets, the full tweet objects are returned.
        """

        file = 'eventdt/tests/corpora/ids-100.txt'
        original = 'eventdt/tests/corpora/#SOUARS-100.json'
        output = 'tools/tests/.out/downloaded.json'

        tools.save(output, {})
        tool.download(file, output, tool.authenticate())
        outlines = 0
        with open(original, 'r') as infile, open(output, 'r') as outfile:
            original, downloaded = [ json.loads(tweet) for tweet in infile.readlines() ], [ json.loads(tweet) for tweet in outfile.readlines() ]
            original = { tweet['id_str']: tweet for tweet in original }
            for tweet in downloaded:
                self.assertTrue(tweet['id_str'] in original)
                self.assertTrue(twitter.full_text(original[tweet['id_str']]), twitter.full_text(tweet))
                self.assertTrue(twitter.extract_timestamp(original[tweet['id_str']]), twitter.extract_timestamp(tweet))

    def test_download_same_order(self):
        """
        Test that when downloading tweets, they are downloaded in the same order as in the original list.
        """

        file = 'eventdt/tests/corpora/ids-100.txt'
        original = 'eventdt/tests/corpora/#SOUARS-100.json'
        output = 'tools/tests/.out/downloaded.json'

        tools.save(output, {})
        tool.download(file, output, tool.authenticate())
        outlines = 0
        with open(original, 'r') as infile, open(output, 'r') as outfile:
            original, downloaded = [ json.loads(tweet) for tweet in infile.readlines() ], [ json.loads(tweet) for tweet in outfile.readlines() ]
            original, downloaded = [ tweet['id_str'] for tweet in original ], [ tweet['id_str'] for tweet in downloaded ]
            original = [ id for id in original if id in downloaded ]
            self.assertEqual(original, downloaded)

    def test_download_number_of_tweets(self):
        """
        Test the number of tweets cannot exceed the number of original tweets.
        """

        file = 'eventdt/tests/corpora/ids-100.txt'
        original = 'eventdt/tests/corpora/#SOUARS-100.json'
        output = 'tools/tests/.out/downloaded.json'

        tools.save(output, {})
        tool.download(file, output, tool.authenticate())
        outlines = 0
        with open(original, 'r') as infile, open(output, 'r') as outfile:
            original, downloaded = [ json.loads(tweet) for tweet in infile.readlines() ], [ json.loads(tweet) for tweet in outfile.readlines() ]
            self.assertLessEqual(len(downloaded), len(original))

    def test_download_no_duplicates(self):
        """
        Test that there are no duplicates in the downloaded tweets.
        """

        file = 'eventdt/tests/corpora/ids-100.txt'
        original = 'eventdt/tests/corpora/#SOUARS-100.json'
        output = 'tools/tests/.out/downloaded.json'

        tools.save(output, {})
        tool.download(file, output, tool.authenticate())
        outlines = 0
        with open(output, 'r') as outfile:
            downloaded = [ json.loads(tweet)['id_str'] for tweet in outfile.readlines() ]
            self.assertEqual(len(downloaded), len(set(downloaded)))
