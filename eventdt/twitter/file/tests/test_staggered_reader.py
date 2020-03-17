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
from twitter.file.staggered_reader import StaggeredFileReader

class TestStaggeredFileReader(unittest.TestCase):
	"""
	Test the functionality of the staggered file reader.
	"""

	def async_test(f):
		def wrapper(*args, **kwargs):
			coro = asyncio.coroutine(f)
			future = coro(*args, **kwargs)
			loop = asyncio.get_event_loop()
			loop.run_until_complete(future)
		return wrapper

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
