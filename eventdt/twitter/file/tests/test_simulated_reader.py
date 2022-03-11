"""
Test the functionality of the simulated file reader.
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
from twitter.file.simulated_reader import SimulatedFileReader

class TestSimulatedFileReader(unittest.IsolatedAsyncioTestCase):
    """
    Test the functionality of the simulated file reader.
    """

    def test_init_default_speed(self):
        """
        Test that when creating a simulated file reader, the default speed is 1.
        """

        reader = SimulatedFileReader(Queue())
        self.assertEqual(1, reader.speed)

    def test_positive_speed(self):
        """
        Test that when creating a simulated file reader with a positive speed, no ValueError is raised.
        """

        self.assertTrue(SimulatedFileReader(Queue(), speed=1))

    def test_zero_speed(self):
        """
        Test that when creating a simulated file reader with a speed of zero, a ValueError is raised.
        """

        self.assertRaises(ValueError, SimulatedFileReader, Queue(), speed=0)

    def test_negative_speed(self):
        """
        Test that when creating a simulated file reader with a negative speed, a ValueError is raised.
        """

        self.assertRaises(ValueError, SimulatedFileReader, Queue(), speed=-1)

    def test_init_default_sample(self):
        """
        Test that when creating a simulated file reader, the default sampling rate is 1.
        """

        reader = SimulatedFileReader(Queue())
        self.assertEqual(1, reader.sample)

    def test_init_float_sample(self):
        """
        Test that when creating a simulated file reader with a rounded float number of lines to skip after each read, no ValueError is raised.
        """

        self.assertTrue(SimulatedFileReader(Queue(), sample=1.0))

    def test_init_integer_sample(self):
        """
        Test that when creating a simulated file reader with an integer number of lines to skip after each read, no ValueError is raised.
        """

        self.assertTrue(SimulatedFileReader(Queue(), sample=1))

    def test_init_negative_sample(self):
        """
        Test that when creating a simulated file reader with a negative number of lines to skip after each read, a ValueError is raised.
        """

        self.assertRaises(ValueError, SimulatedFileReader, Queue(), sample=-1)

    def test_init_zero_sample(self):
        """
        Test that when creating a simulated file reader with a sampling rate of 0, no ValueError is raised.
        """

        self.assertTrue(SimulatedFileReader(Queue(), sample=1))

    def test_init_float_sample(self):
        """
        Test that when creating a simulated file reader with a floating-point sampling rate, no ValueError is raised.
        """

        self.assertTrue(SimulatedFileReader(Queue(), sample=0.5))

    async def test_read(self):
        """
        Test reading the corpus without skipping anything.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        self.assertEqual(0, queue.length())
        await reader.read(file)
        self.assertEqual(100, queue.length())

    async def test_read_skip_no_lines(self):
        """
        Test that when reading the corpus after skipping no lines, all tweets are loaded.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, skip_lines=0)
        self.assertEqual(100, queue.length())

    async def test_read_skip_lines(self):
        """
        Test reading the corpus after skipping a number of lines.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, skip_lines=50)
        self.assertEqual(50, queue.length())

    async def test_read_skip_all_lines(self):
        """
        Test that when all lines are skipped, the queue is empty.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, skip_lines=100)
        self.assertEqual(0, queue.length())

    async def test_read_skip_excess_lines(self):
        """
        Test that when excess lines are skipped, the queue is empty.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, skip_lines=101)
        self.assertEqual(0, queue.length())

    async def test_read_skip_no_time(self):
        """
        Test that when reading the corpus after skipping no time, all tweets are loaded.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, skip_time=0)
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

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, skip_time=1)
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

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, skip_time=skip)
        self.assertEqual(5, queue.length()) # there were 5 tweets in the last second

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
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, skip_time=skip + 1)
        self.assertEqual(0, queue.length())

    async def test_read_return_read_lines(self):
        """
        Test that when reading the corpus, the function returns the number of read tweets.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        read = await reader.read(file)
        self.assertEqual(100, read)

    async def test_read_return_equals_queue_length(self):
        """
        Test that when reading the corpus, the number of read tweets is the same as the number of tweets in the queue.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        read = await reader.read(file)
        self.assertEqual(queue.length(), read)

    async def test_read_sample_all(self):
        """
        Test that when reading the corpus with full sampling, the full corpus is read.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=10, sample=1)
        read = await reader.read(file)
        self.assertEqual(100, read)

    async def test_read_sample_none(self):
        """
        Test that when reading the corpus with a sampling rate of 0, no tweets are read.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=10, sample=0)
        read = await reader.read(file)
        self.assertEqual(0, read)

    async def test_read_sample(self):
        """
        Test that when reading the corpus with sampling, only a part of the corpus is read.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=10, sample=0.5)
        read = await reader.read(file)
        self.assertEqual(50, read)

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=10, sample=(1/3))
        read = await reader.read(file)
        self.assertEqual(33, read)

    async def test_read_sample_not_adjacent(self):
        """
        Test that when reading the corpus with full sampling, the tweets are equally-spaced.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            tweets = [ json.loads(tweet) for tweet in f.readlines() ]

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=10, sample=0.5)
        read = await reader.read(file)
        self.assertEqual(50, read)
        self.assertEqual(tweets[1::2], queue.queue)

    async def test_normal_speed(self):
        """
        Test that when using normal speed, the time it takes is equivalent to the length of the corpus.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'

        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))
            length = end - start

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=1)
        start = time.time()
        await reader.read(file)
        self.assertEqual(100, queue.length())
        self.assertEqual(length, round(time.time() - start))

    async def test_double_speed(self):
        """
        Test that when using double speed, the time it takes is equivalent to half the length of the corpus.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'

        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))
            length = end - start

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=2)
        start = time.time()
        await reader.read(file)
        self.assertEqual(100, queue.length())
        self.assertEqual(length / 2., round(time.time() - start, 1))

    async def test_half_speed(self):
        """
        Test that when using half speed, the time it takes is equivalent to double the length of the corpus.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'

        with open(file, 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))
            length = end - start

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=0.5)
        start = time.time()
        await reader.read(file)
        self.assertEqual(100, queue.length())
        self.assertEqual(length * 2., round(time.time() - start, 1))

    async def test_max_lines(self):
        """
        Test that when limiting the number of lines, only a few are returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, max_lines=100)
        self.assertEqual(100, queue.length())

    async def test_max_lines_zero(self):
        """
        Test that when reading zero lines, no lines are returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, max_lines=0)
        self.assertEqual(0, queue.length())

    async def test_max_lines_all(self):
        """
        Test that when reading all lines, all lines are returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, max_lines=100)
        self.assertEqual(100, queue.length())

    async def test_max_lines_excess(self):
        """
        Test that when reading excess lines, all lines are returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, max_lines=1200)
        self.assertEqual(100, queue.length())

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

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, max_time=1)
        self.assertEqual(2, queue.length())
        self.assertEqual(start, extract_timestamp(queue.head()))
        self.assertEqual(start, extract_timestamp(queue.tail()))

    async def test_max_time_zero(self):
        """
        Test that when the time is zero, nothing is returned.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, max_time=0)
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

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, max_time=end - start + 1)
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

        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100)
        await reader.read(file, max_time=end - start + 2)
        self.assertEqual(100, queue.length())

    async def test_skip_retweets(self):
        """
        Test that when skipping retweets, none of the tweets read from the corpus are retweets.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100, skip_retweets=True)
        await reader.read(file)
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
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100, skip_retweets=False)
        await reader.read(file)
        self.assertTrue(queue.length())
        self.assertTrue(any( is_retweet(tweet) for tweet in queue.queue ))

        """
        Test that all the tweets are in the queue.
        """
        with open(file, 'r') as f:
            for line in f:
                tweet = json.loads(line)
                self.assertTrue(tweet in queue.queue)

    async def test_skip_unverified(self):
        """
        Test that when skipping tweets from unverified authors, none of the tweets read from the corpus are from unverified authors.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100, skip_unverified=True)
        await reader.read(file)
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
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100, skip_unverified=False)
        await reader.read(file)
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
        queue = Queue()
        reader = SimulatedFileReader(queue, speed=100, skip_retweets=True, skip_unverified=False)
        await reader.read(file)
        self.assertTrue(queue.length())
        self.assertTrue(not any( is_retweet(tweet) for tweet in queue.queue ))
        self.assertTrue(any( is_verified(tweet) for tweet in queue.queue ))
