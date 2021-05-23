"""
Test the functionality of the staggered file reader.
"""

import asyncio
import json
import os
import sys
import time
import unittest

from datetime import datetime
from tweepy import OAuthHandler, Stream

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from queues import Queue
from twitter import *
from twitter.file.staggered_reader import StaggeredFileReader

class TestStaggeredFileReader(unittest.IsolatedAsyncioTestCase):
    """
    Test the functionality of the staggered file reader.
    """

    def test_floating_point_rate(self):
        """
        Test that when creating a staggered file reader with a floating point rate, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, rate=0.1)

    def test_float_rate(self):
        """
        Test that when creating a staggered file reader with a rounded float rate, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, rate=1.0))

    def test_integer_rate(self):
        """
        Test that when creating a staggered file reader with an integer rate, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, rate=1))

    def test_zero_rate(self):
        """
        Test that when creating a staggered file reader with a rate of zero, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, rate=0)

    def test_negative_rate(self):
        """
        Test that when creating a staggered file reader with a negative rate, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, rate=-1)

    def test_floating_point_skip_lines(self):
        """
        Test that when creating a staggered file reader with a floating point number of lines to skip, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, skip_lines=0.1)

    def test_float_skip_lines(self):
        """
        Test that when creating a staggered file reader with a rounded float number of lines to skip, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_lines=1.0))

    def test_integer_skip_lines(self):
        """
        Test that when creating a staggered file reader with an integer number of lines to skip, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_lines=1))

    def test_negative_skip_lines(self):
        """
        Test that when creating a staggered file reader with a negative number of lines to skip, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, skip_lines=-1)

    def test_zero_skip_lines(self):
        """
        Test that when creating a staggered file reader that skips no lines, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_lines=0))

    def test_positive_skip_lines(self):
        """
        Test that when creating a staggered file reader that skips a positive number of lines, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_lines=1))

    def test_negative_skip_time(self):
        """
        Test that when creating a staggered file reader with a negative number of seconds to skip, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, skip_time=-1)

    def test_zero_skip_time(self):
        """
        Test that when creating a staggered file reader that skips no time, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_time=0))

    def test_positive_skip_time(self):
        """
        Test that when creating a staggered file reader that skips a positive number of seconds, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_time=1))

    def test_init_default_sample(self):
        """
        Test that when creating a staggered file reader, the default sampling rate is 1.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = StaggeredFileReader(Queue(), f)
            self.assertEqual(1, reader.sample)

    def test_floating_point_sample(self):
        """
        Test that when creating a staggered file reader with a floating point number of lines to skip after each read, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, sample=1.1)

    def test_float_sample(self):
        """
        Test that when creating a staggered file reader with a rounded float number of lines to skip after each read, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, sample=1.0))

    def test_integer_sample(self):
        """
        Test that when creating a staggered file reader with an integer number of lines to skip after each read, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, sample=1))

    def test_negative_sample(self):
        """
        Test that when creating a staggered file reader with a negative number of lines to skip after each read, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, sample=-1)

    def test_zero_sample(self):
        """
        Test that when creating a staggered file reader with a sampling rate of 0, it raises a ValueError.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, sample=0)

    def test_positive_sample(self):
        """
        Test that when creating a staggered file reader that samples each line, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, sample=1))

    async def test_read(self):
        """
        Test reading the corpus without skipping anything.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100)
            self.assertEqual(0, queue.length())
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_read_skip_no_lines(self):
        """
        Test that when reading the corpus after skipping no lines, all tweets are loaded.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_lines=0)
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_read_skip_lines(self):
        """
        Test reading the corpus after skipping a number of lines.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_lines=100)
            await reader.read()
            self.assertEqual(500, queue.length())

    async def test_read_skip_all_lines(self):
        """
        Test that when all lines are skipped, the queue is empty.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_lines=100)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_read_skip_excess_lines(self):
        """
        Test that when excess lines are skipped, the queue is empty.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_lines=601)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_read_skip_no_time(self):
        """
        Test that when reading the corpus after skipping no time, all tweets are loaded.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_time=0)
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_read_skip_lines(self):
        """
        Test reading the corpus after skipping some time.
        """

        """
        Calculate the number of lines that should be skipped.
        """
        skipped = 0
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            for line in lines:
                if extract_timestamp(json.loads(line)) == start:
                    skipped += 1
                else:
                    break

                    file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_time=1)
            await reader.read()
            self.assertEqual(100 - skipped, queue.length())

    async def test_read_skip_all_time(self):
        """
        Test reading the corpus after skipping all time.
        """

        """
        Calculate the number of lines that should be skipped.
        """
        skip = 0
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))
            skip = end - start

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_time=skip)
            await reader.read()
            self.assertEqual(5, queue.length()) # 5 tweets in the last second

    async def test_read_skip_excess_time(self):
        """
        Test reading the corpus after excess time.
        """

        """
        Calculate the number of lines that should be skipped.
        """
        skip = 0
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))
            skip = end - start

            file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_time=skip + 1)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_read_return_read_lines(self):
        """
        Test that when reading the corpus, the function returns the number of read tweets.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100)
            read = await reader.read()
            self.assertEqual(100, read)

    async def test_read_return_equals_queue_length(self):
        """
        Test that when reading the corpus, the number of read tweets is the same as the number of tweets in the queue.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100)
            read = await reader.read()
            self.assertEqual(queue.length(), read)

    async def test_sample(self):
        """
        Test that when using the skip rate, the tweets are distributed evenly.
        """

        """
        Calculate the start and end of the corpus.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, sample=2)
            await reader.read()
            self.assertEqual(50, queue.length())
            self.assertEqual(start, extract_timestamp(queue.head()))
            self.assertEqual(end, extract_timestamp(queue.tail()))

    async def test_rate(self):
        """
        Test that when using the rate, the time scales accordingly.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100)
            start = time.time()
            await reader.read()
            self.assertTrue(0.9 <= round(time.time() - start, 2) <= 1.1)
            self.assertEqual(100, queue.length())

    async def test_max_lines(self):
        """
        Test that when limiting the number of lines, only a few are returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_lines=100)
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_max_lines_zero(self):
        """
        Test that when reading zero lines, no lines are returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_lines=0)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_max_lines_all(self):
        """
        Test that when reading all lines, all lines are returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_lines=100)
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_max_lines_excess(self):
        """
        Test that when reading excess lines, all lines are returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_lines=1200)
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_max_lines_with_skip(self):
        """
        Test that when limiting the number of lines and employing skipping, only a few are returned.
        """

        """
        Calculate the start and end of the corpus.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_lines=100, sample=5)
            await reader.read()
            self.assertEqual(20, queue.length())
            self.assertEqual(start, extract_timestamp(queue.head()))
            self.assertEqual(end, extract_timestamp(queue.tail()))

    async def test_max_time(self):
        """
        Test that when limiting the time, only a few are returned.
        """

        """
        Calculate the start and end of the corpus.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

            file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_time=1)
            await reader.read()
            self.assertEqual(2, queue.length()) # 2 tweets in the first second
            self.assertEqual(start, extract_timestamp(queue.head()))
            self.assertEqual(start, extract_timestamp(queue.tail()))

    async def test_max_time_zero(self):
        """
        Test that when the time is zero, nothing is returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_time=0)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_max_time_all(self):
        """
        Test that when all the time is allowed, the entire corpus is returned.
        """

        """
        Calculate the start and end of the corpus.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

            file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_time=end - start + 1)
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_max_time_excess(self):
        """
        Test that when excess time is allowed, the entire corpus is returned.
        """

        """
        Calculate the start and end of the corpus.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

            file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, max_time=end - start + 2)
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_skip_retweets(self):
        """
        Test that when skipping retweets, none of the tweets read from the corpus are retweets.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_retweets=True)
            await reader.read()
            self.assertTrue(queue.length())
            self.assertTrue(all( not is_retweet(tweet) for tweet in queue.queue ))

        """
        Test that all the correct tweets are in the queue.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if is_retweet(tweet):
                    self.assertFalse(tweet in queue.queue)
                else:
                    self.assertTrue(tweet in queue.queue)

    async def test_no_skip_retweets(self):
        """
        Test that when not skipping retweets, all of the tweets in the corpus are retained.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_retweets=False)
            await reader.read()
            self.assertTrue(queue.length())
            self.assertTrue(any( is_retweet(tweet) for tweet in queue.queue ))

        """
        Test that all the tweets are in the queue.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertTrue(tweet in queue.queue)

    async def test_skip_unverified(self):
        """
        Test that when skipping tweets from unverified authors, none of the tweets read from the corpus are from unverified authors.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=1000, skip_unverified=True)
            await reader.read()
            self.assertTrue(queue.length())
            self.assertTrue(all( is_verified(tweet) for tweet in queue.queue ))

        """
        Test that all the correct tweets are in the queue.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            for line in f:
                tweet = json.loads(line)
                if is_verified(tweet):
                    self.assertTrue(tweet in queue.queue)
                else:
                    self.assertFalse(tweet in queue.queue)

    async def test_no_skip_unverified(self):
        """
        Test that when not skipping tweets from unverified authors, all of the tweets in the corpus are retained.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=1000, skip_unverified=False)
            await reader.read()
            self.assertTrue(queue.length())
            self.assertTrue(any( is_verified(tweet) for tweet in queue.queue ))

        """
        Test that all the tweets are in the queue.
        """
        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertTrue(tweet in queue.queue)

    async def test_skip_retweets_but_not_unverified(self):
        """
        Test that when skipping retweets, but not tweets from unverified authors, retweets are not retained.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=1000, skip_retweets=True, skip_unverified=False)
            await reader.read()
            self.assertTrue(queue.length())
            self.assertTrue(not any( is_retweet(tweet) for tweet in queue.queue ))
            self.assertTrue(any( is_verified(tweet) for tweet in queue.queue ))
