"""
The :class:`~twitter.file.staggered_reader.StaggeredFileReader` is a file reader that reads a corpus at a constant pace.
This results in a steady and predictable stream of tweets.
Therefore the :class:`~twitter.file.staggered_reader.StaggeredFileReader` allows the application to receive as many tweets as it can handle, and handle them as well as it can.
For this reason, it is most opportune when the :ref:`consumer's <consumers>` performance under strain is not important, but its results are.
"""

import json

import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from twitter import *
from twitter.file import FileReader

class StaggeredFileReader(FileReader):
    """
    The :class:`~twitter.file.staggered_reader.StaggeredFileReader` is based on the :class:`~twitter.file.FileReader`, so it reads tweets from a file and adds it to a queue.
    However, unlike the :class:`~twitter.file.simulated_reader.SimulatedFileReader`, it reads tweets at a constant pace.
    It reads a few tweets at a time, stops and waits.

    The pace of the :class:`~twitter.file.staggered_reader.StaggeredFileReader` is governed by the ``rate`` and the ``skip_rate``.
    The ``rate`` is the number of tweets to read per second from the file.
    The :class:`~twitter.file.staggered_reader.StaggeredFileReader` does not read a bunch of tweets and sleeps for the rest of the second, but spaces them out over a second.
    On the other hand, the ``skip_rate`` is the number is the number of tweets to skip every second.
    Therefore the approach works skips a number of tweets per second, and then reads a number of tweets.

    :ivar rate: The number of lines to read per second.
    :vartype rate: float
    :ivar skip_rate: The number of lines to skip for each line read.
    :vartype skip_rate: int
    """

    def __init__(self, queue, f, rate=1, skip_rate=0, *args, **kwargs):
        """
        Create the :class:`~twitter.file.staggered_reader.StaggeredFileReader` with the file from where to read tweets and the :class:`~queues.Queue` where to store them.
        The ``rate`` and ``skip_rate`` are extra parameters in addition to the :class:`~twitter.file.FileReader`'s parameters.

        :param queue: The queue to which to add the tweets.
        :type queue: :class:`~queues.Queue`
        :param f: The opened file from where to read the tweets.
        :type f: file
        :param max_lines: The maximum number of lines to read.
                          If the number is negative, it is ignored.
        :type max_lines: int
        :param max_time: The maximum time in seconds to spend reading from the file.
                         The time is taken from tweets' timestamps.
                         If the number is negative, it is ignored.
        :type max_time: int
        :param skip_lines: The number of lines to skip from the beginning of the file.
        :type skip_lines: int
        :param skip_time: The number of seconds to skip from the beginning of the file.
        :type skip_time: int
        :param rate: The number of lines to read per second.
        :type rate: float
        :param skip_rate: The number of lines to skip for each line read.
        :type skip_rate: int

        :raises ValueError: When the rate is not an integer.
        :raises ValueError: When the rate is zero or negative.
        :raises ValueError: When the number of lines to skip after each read is not an integer.
        :raises ValueError: When the number of lines to skip after each read is negative.
        """

        super(StaggeredFileReader, self).__init__(queue, f, *args, **kwargs)

        """
        Validate the inputs.
        """
        if rate % 1:
            raise ValueError(f"The rate must be an integer; received {rate}")

        if rate <= 0:
            raise ValueError(f"The rate must be positive; received {rate}")

        if skip_rate % 1:
            raise ValueError(f"The rate of lines to skip after each read must be an integer; received {skip_rate}")

        if skip_rate < 0:
            raise ValueError(f"The rate of lines to skip after each read cannot be negative; received {skip_rate}")

        self.rate = rate
        self.skip_rate = skip_rate

    @FileReader.reading
    async def read(self):
        """
        Read the file and add each line as a dictionary to the queue.
        """

        file = self.file

        """
        Extract the timestamp from the first tweet, then reset the file pointer.
        """
        pos = file.tell()
        line = file.readline()
        if not line:
            return
        first = extract_timestamp(json.loads(line))
        file.seek(pos)

        """
        Go through each line and add it to the queue
        Time how long it takes to read each tweet to avoid extra time skipping.
        """
        for i, line in enumerate(file):
            start = time.time()

            """
            If the maximum number of lines, or time, has been exceeded, stop reading.
            """
            if self.max_lines >= 0 and i >= self.max_lines:
                break

            tweet = json.loads(line)
            if self.max_time >= 0 and extract_timestamp(tweet) - first >= self.max_time:
                break

            """
            If the reader has been interrupted, stop reading.
            """
            if not self.active:
                break

            self.queue.enqueue(tweet)

            """
            Skip some lines if need be.
            """
            for _ in range(self.skip_rate):
                file.readline()

            """
            If there is a limit on the number of lines to read per minute, sleep a bit.
            The calculation considers how long reading the tweet took.
            """
            elapsed = time.time() - start
            if self.rate > 0:
                sleep = 1/self.rate - elapsed
                if sleep > 0:
                    time.sleep(sleep)
