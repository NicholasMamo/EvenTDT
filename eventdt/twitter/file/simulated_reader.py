"""
The :class:`~twitter.file.simulated_reader.SimulatedFileReader` simulates the real-time stream by adding tweets to the queue as if the tweets were being received in real-time.
It pretends that the event is ongoing, and adds data to the queue according to when they happened.
This means that in high-volume periods, the :class:`~twitter.file.simulated_reader.SimulatedFileReader` adds many tweets to the :class:`~queues.Queue`.
In low-volume periods, it enqueues fewer tweets.

Since the :class:`~twitter.file.simulated_reader.SimulatedFileReader` has high fidelity, it is most appropriate in experimental or evaluation settings.
Since the volume is likely to change, it also tests the :ref:`consumers' <consumers>` performance in volatile or high-volume situations.
"""

import asyncio
import json
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from twitter import *
from twitter.file import FileReader

class SimulatedFileReader(FileReader):
    """
    The :class:`~twitter.file.simulated_reader.SimulatedFileReader` is based on the :class:`~twitter.file.FileReader`, so it reads tweets from a file and adds it to a queue.
    This works like a simulation, as if the event was happening at the same time.

    In addition to the parameters accepted by the :class:`~twitter.file.FileReader`, it also accepts the ``speed``.
    Since the :class:`~twitter.file.simulated_reader.SimulatedFileReader` simulates the stream as if it is happening in real-time, the ``speed`` is a function of time as well.

    The ``sample`` parameter is used as a systematic sampling mechanism.
    For every :math:`sample` tweets, the simulated reader reads only one.
    By the end, the simulated reader reads :math:`1/sample` of all tweets in the corpus.

    :ivar speed: The reading speed as a function of time.
                 If it is set to 0.5, for example, the event progresses at half the speed.
                 If it is set to 2, the event progresses at double the speed.
    :vartype speed: int
    :ivar sample: The fraction of tweets to read.
                  The reader uses systematic sampling, reading $\\frac{1}{n}$ samples.
                  If 1 is given, the simulated reader reads all tweets.
                  If 0.5 is given, the simulated reader reads every other tweet.
    :vartype sample: int or float
    """

    def __init__(self, queue, f, speed=1, sample=1, *args, **kwargs):
        """
        Create the :class:`~twitter.file.simulated_reader.SimulatedFileReader` with the file from where to read tweets and the :class:`~queues.Queue` where to store them.
        The ``speed`` is an extra parameter in addition to the :class:`~twitter.file.FileReader`'s parameters.

        :param queue: The queue to which to add the tweets.
        :type queue: :class:`~queues.Queue`
        :param f: The opened file from where to read the tweets.
        :type f: file
        :param speed: The reading speed, considered to be a function of time.
                      If it is set to 0.5, for example, the event progresses at half the speed.
                      If it is set to 2, the event progresses at double the speed.
        :type speed: int
        :param sample: The fraction of tweets to read.
                       The reader uses systematic sampling, reading $\\frac{1}{n}$ samples.
                       If 1 is given, the simulated reader reads all tweets.
                       If 0.5 is given, the simulated reader reads every other tweet.
        :type sample: int or float

        :raises ValueError: When the speed is zero or negative.
        :raises ValueError: When the sampling rate is not between 0 and 1.
        """

        super(SimulatedFileReader, self).__init__(queue, f, *args, **kwargs)

        """
        Validate the inputs.
        """
        if speed <= 0:
            raise ValueError(f"The speed must be positive; received {speed}")

        if sample > 1 or sample < 0:
            raise ValueError(f"The rate of lines to skip after each read must be between 0 and 1; received {sample}")

        self.speed = speed
        self.sample = sample

    @FileReader.reading
    async def read(self, max_lines=-1, max_time=-1, *args, **kwargs):
        """
        Read the file and add each line as a dictionary to the queue.

        :param max_lines: The maximum number of lines to read.
                          If the number is negative, it is ignored.
        :type max_lines: int
        :param max_time: The maximum time in seconds to spend reading from the file.
                         The time is taken from tweets' timestamps.
                         If the number is negative, it is ignored.
        :type max_time: int

        :return: The number of tweets read from the file.
        :rtype: int
        """

        await super(SimulatedFileReader, self).read(*args, **kwargs)

        read = 0

        """
        Extract the timestamp from the first tweet, then reset the file pointer.
        """
        file = self.file
        pos = file.tell()
        line = file.readline()
        if not line:
            return
        first = extract_timestamp(json.loads(line))
        file.seek(pos)

        """
        Go through each line and add it to the queue.
        """
        sample = 0 # the sampling progress: when it reaches or exceeds 1, the reader reads the next tweet and resets it to the remainder
        start = time.time()
        for i, line in enumerate(file):
            tweet = json.loads(line)
            created_at = extract_timestamp(tweet)

            """
            If the maximum number of lines, or the time, has been exceeded, stop reading.
            """
            if max_lines >= 0 and i >= max_lines:
                break

            if max_time >= 0 and created_at - first >= max_time:
                break

            """
            If the tweet is 'in the future', stop reading until the reader catches up.
            It is only after it catches up that the tweet is added to the queue.
            """
            elapsed = time.time() - start
            if (created_at - first) / self.speed > elapsed and self.active:
                await asyncio.sleep((created_at - first) / self.speed - elapsed)

            """
            If the reader has been interrupted, stop reading.
            """
            if not self.active:
                break

            """
            Only add a tweet if it is valid.
            """
            if self.valid(tweet):
                """
                The increment is the sampling interval, but the reader only reads a tweet if the sampling weight reaches 1.
                If the sampling interval is 0.5, the sampling weight reaches 1 at every other tweet, so the reader will read every other tweet.
                """
                sample += self.sample
                if sample >= 1: # if it's time to read a new tweet, read one
                    sample -= 1 # keep the remainder
                    self.queue.enqueue(tweet)
                    read += 1

        return read
