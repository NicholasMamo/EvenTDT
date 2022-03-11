"""
Test the functionality of the :class:`~twitter.file.FileReader`.
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

class TestFileReader(unittest.IsolatedAsyncioTestCase):
    """
    Test the functionality of the :class:`~twitter.file.FileReader`.
    The test uses the :class:`~twitter.file.SimulatedFileReader` since the original is an abstract class.
    """

    async def test_skip_returns_tuple(self):
        """
        Test that when skipping, the returned value is a tuple.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'

        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            value = reader.skip(f, lines=10, time=10)
            self.assertEqual(tuple, type(value))

    async def test_skip_max_lines_integer(self):
        """
        Test that when skipping, the returned skipped lines is an integer.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'

        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            lines, time = reader.skip(f, lines=10, time=10)
            self.assertEqual(int, type(lines))

    async def test_skip_max_time_integer(self):
        """
        Test that when skipping, the returned skipped time is an integer.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'

        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            lines, time = reader.skip(f, lines=10, time=10)
            self.assertEqual(0, time % 1)

    async def test_skip_none(self):
        """
        Test that when skipping nothing, the returned values are both zero.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'

        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            lines, time = reader.skip(f, lines=0, time=0)
            self.assertEqual(0, lines)
            self.assertEqual(0, time)

    async def test_skip_floating_point_skip_lines(self):
        """
        Test that when creating a staggered file reader with a floating point number of lines to skip, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            with self.assertRaises(ValueError):
                await reader.read(f, skip_lines=0.1)

    async def test_skip_float_skip_lines(self):
        """
        Test that when creating a staggered file reader with a rounded float number of lines to skip, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            self.assertTrue(await reader.read(f, skip_lines=1.0))

    async def test_skip_integer_skip_lines(self):
        """
        Test that when creating a staggered file reader with an integer number of lines to skip, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            self.assertTrue(await reader.read(f, skip_lines=1))

    async def test_skip_negative_skip_lines(self):
        """
        Test that when creating a staggered file reader with a negative number of lines to skip, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            with self.assertRaises(ValueError):
                await reader.read(f, skip_lines=-1)

    async def test_skip_zero_skip_lines(self):
        """
        Test that when creating a staggered file reader that skips no lines, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            self.assertTrue(await reader.read(f, skip_lines=0))

    async def test_skip_positive_skip_lines(self):
        """
        Test that when creating a staggered file reader that skips a positive number of lines, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            self.assertTrue(await reader.read(f, skip_lines=1))

    async def test_skip_negative_skip_time(self):
        """
        Test that when creating a staggered file reader with a negative number of seconds to skip, a ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            with self.assertRaises(ValueError):
                await reader.read(f, skip_time=-1)

    async def test_skip_zero_skip_time(self):
        """
        Test that when creating a staggered file reader that skips no time, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            self.assertTrue(await reader.read(f, skip_time=0))

    async def test_skip_positive_skip_time(self):
        """
        Test that when creating a staggered file reader that skips a positive number of seconds, no ValueError is raised.
        """

        file = 'eventdt/tests/corpora/CRYCHE-100.json'
        with open(file, 'r') as f:
            reader = SimulatedFileReader(Queue(), speed=100)
            self.assertTrue(await reader.read(f, skip_time=1))
