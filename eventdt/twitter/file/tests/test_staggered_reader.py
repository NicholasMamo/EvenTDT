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

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, rate=0.1)

    def test_float_rate(self):
        """
        Test that when creating a staggered file reader with a rounded float rate, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, rate=1.0))

    def test_integer_rate(self):
        """
        Test that when creating a staggered file reader with an integer rate, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, rate=1))

    def test_zero_rate(self):
        """
        Test that when creating a staggered file reader with a rate of zero, a ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, rate=0)

    def test_negative_rate(self):
        """
        Test that when creating a staggered file reader with a negative rate, a ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, rate=-1)

    def test_floating_point_skip_lines(self):
        """
        Test that when creating a staggered file reader with a floating point number of lines to skip, a ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, skip_lines=0.1)

    def test_float_skip_lines(self):
        """
        Test that when creating a staggered file reader with a rounded float number of lines to skip, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_lines=1.0))

    def test_integer_skip_lines(self):
        """
        Test that when creating a staggered file reader with an integer number of lines to skip, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_lines=1))

    def test_negative_skip_lines(self):
        """
        Test that when creating a staggered file reader with a negative number of lines to skip, a ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, skip_lines=-1)

    def test_zero_skip_lines(self):
        """
        Test that when creating a staggered file reader that skips no lines, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_lines=0))

    def test_positive_skip_lines(self):
        """
        Test that when creating a staggered file reader that skips a positive number of lines, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_lines=1))

    def test_negative_skip_time(self):
        """
        Test that when creating a staggered file reader with a negative number of seconds to skip, a ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, skip_time=-1)

    def test_zero_skip_time(self):
        """
        Test that when creating a staggered file reader that skips no time, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_time=0))

    def test_positive_skip_time(self):
        """
        Test that when creating a staggered file reader that skips a positive number of seconds, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_time=1))

    def test_floating_point_skip_rate(self):
        """
        Test that when creating a staggered file reader with a floating point number of lines to skip after each read, a ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, skip_rate=0.1)

    def test_float_skip_rate(self):
        """
        Test that when creating a staggered file reader with a rounded float number of lines to skip after each read, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_rate=1.0))

    def test_integer_skip_rate(self):
        """
        Test that when creating a staggered file reader with an integer number of lines to skip after each read, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_rate=1))

    def test_negative_skip_rate(self):
        """
        Test that when creating a staggered file reader with a negative number of lines to skip after each read, a ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertRaises(ValueError, StaggeredFileReader, Queue(), f, skip_rate=-1)

    def test_zero_skip_rate(self):
        """
        Test that when creating a staggered file reader that skips no lines, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_rate=0))

    def test_positive_skip_rate(self):
        """
        Test that when creating a staggered file reader that skips a positive number of lines after each read, no ValueError is raised.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            self.assertTrue(StaggeredFileReader(Queue(), f, skip_rate=1))

    async def test_read(self):
        """
        Test reading the corpus without skipping anything.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600)
            self.assertEqual(0, queue.length())
            await reader.read()
            self.assertEqual(600, queue.length())

    async def test_read_skip_no_lines(self):
        """
        Test that when reading the corpus after skipping no lines, all tweets are loaded.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_lines=0)
            await reader.read()
            self.assertEqual(600, queue.length())

    async def test_read_skip_lines(self):
        """
        Test reading the corpus after skipping a number of lines.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_lines=100)
            await reader.read()
            self.assertEqual(500, queue.length())

    async def test_read_skip_all_lines(self):
        """
        Test that when all lines are skipped, the queue is empty.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_lines=600)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_read_skip_excess_lines(self):
        """
        Test that when excess lines are skipped, the queue is empty.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_lines=601)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_read_skip_no_time(self):
        """
        Test that when reading the corpus after skipping no time, all tweets are loaded.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_time=0)
            await reader.read()
            self.assertEqual(600, queue.length())

    async def test_read_skip_lines(self):
        """
        Test reading the corpus after skipping some time.
        """

        """
        Calculate the number of lines that should be skipped.
        """
        skipped = 0
        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            for line in lines:
                if extract_timestamp(json.loads(line)) == start:
                    skipped += 1
                else:
                    break

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_time=1)
            await reader.read()
            self.assertEqual(600 - skipped, queue.length())

    async def test_read_skip_all_time(self):
        """
        Test reading the corpus after skipping all time.
        """

        """
        Calculate the number of lines that should be skipped.
        """
        skip = 0
        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))
            skip = end - start

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_time=skip)
            await reader.read()
            self.assertEqual(50, queue.length())

    async def test_read_skip_excess_time(self):
        """
        Test reading the corpus after excess time.
        """

        """
        Calculate the number of lines that should be skipped.
        """
        skip = 0
        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))
            skip = end - start

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_time=skip + 1)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_skip_rate(self):
        """
        Test that when using the skip rate, the tweets are distributed evenly.
        """

        """
        Calculate the start and end of the corpus.
        """
        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, skip_rate=1)
            await reader.read()
            self.assertEqual(300, queue.length())
            self.assertEqual(start, extract_timestamp(queue.head()))
            self.assertEqual(end, extract_timestamp(queue.tail()))

    async def test_rate(self):
        """
        Test that when using the rate, the time scales accordingly.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100)
            start = time.time()
            await reader.read()
            self.assertTrue(6 <= round(time.time() - start, 2) <= 6.2)
            self.assertEqual(600, queue.length())

    async def test_rate_with_skip(self):
        """
        Test that when using the rate while skipping, the time scales accordingly.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=100, skip_rate=1)
            start = time.time()
            await reader.read()
            self.assertTrue(3 <= round(time.time() - start, 2) <= 3.1)
            self.assertEqual(300, queue.length())

    async def test_max_lines(self):
        """
        Test that when limiting the number of lines, only a few are returned.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_lines=100)
            await reader.read()
            self.assertEqual(100, queue.length())

    async def test_max_lines_zero(self):
        """
        Test that when reading zero lines, no lines are returned.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_lines=0)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_max_lines_all(self):
        """
        Test that when reading all lines, all lines are returned.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_lines=600)
            await reader.read()
            self.assertEqual(600, queue.length())

    async def test_max_lines_excess(self):
        """
        Test that when reading excess lines, all lines are returned.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_lines=1200)
            await reader.read()
            self.assertEqual(600, queue.length())

    async def test_max_lines_with_skip(self):
        """
        Test that when limiting the number of lines and employing skipping, only a few are returned.
        """

        """
        Calculate the start and end of the corpus.
        """
        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_lines=100, skip_rate=5)
            await reader.read()
            self.assertEqual(100, queue.length())
            self.assertEqual(start, extract_timestamp(queue.head()))
            self.assertEqual(end, extract_timestamp(queue.tail()))

    async def test_max_time(self):
        """
        Test that when limiting the time, only a few are returned.
        """

        """
        Calculate the start and end of the corpus.
        """
        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_time=1)
            await reader.read()
            self.assertEqual(100, queue.length())
            self.assertEqual(start, extract_timestamp(queue.head()))
            self.assertEqual(start, extract_timestamp(queue.tail()))

    async def test_max_time_zero(self):
        """
        Test that when the time is zero, nothing is returned.
        """

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_time=0)
            await reader.read()
            self.assertEqual(0, queue.length())

    async def test_max_time_all(self):
        """
        Test that when all the time is allowed, the entire corpus is returned.
        """

        """
        Calculate the start and end of the corpus.
        """
        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_time=end - start + 1)
            await reader.read()
            self.assertEqual(600, queue.length())

    async def test_max_time_excess(self):
        """
        Test that when excess time is allowed, the entire corpus is returned.
        """

        """
        Calculate the start and end of the corpus.
        """
        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            lines = f.readlines()
            start = extract_timestamp(json.loads(lines[0]))
            end = extract_timestamp(json.loads(lines[-1]))

        with open(os.path.join(os.path.dirname(__file__), 'corpus.json'), 'r') as f:
            queue = Queue()
            reader = StaggeredFileReader(queue, f, rate=600, max_time=end - start + 2)
            await reader.read()
            self.assertEqual(600, queue.length())
