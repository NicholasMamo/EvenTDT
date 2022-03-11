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
import tarfile
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger
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

    def __init__(self, queue, speed=1, sample=1, *args, **kwargs):
        """
        Create the :class:`~twitter.file.simulated_reader.SimulatedFileReader` with the file from where to read tweets and the :class:`~queues.Queue` where to store them.
        The ``speed`` is an extra parameter in addition to the :class:`~twitter.file.FileReader`'s parameters.

        :param queue: The queue to which to add the tweets.
        :type queue: :class:`~queues.Queue`
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

        super(SimulatedFileReader, self).__init__(queue, *args, **kwargs)

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
    async def read(self, file, max_lines=-1, max_time=-1, skip_lines=0, skip_time=0):
        """
        Read the file and add each line as a dictionary to the queue.

        :param file: The file path or a list of file paths from where to read the tweets.
                     If ``.tar.gz`` files are provided, the function looks for ``sample.json`` or ``event.json`` files.
        :type file: str or list of str
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

        :return: The number of tweets read from the file.
        :rtype: int
        """

        read = 0
        sample = 0 # the sampling progress: when it reaches or exceeds 1, the reader reads the next tweet and resets it to the remainder
        start = time.time()

        files = [ file ] if type(file) is str else file
        first = self._first(files)
        for file in files:
            if file.endswith('.tar.gz'):
                with tarfile.open(file) as archive:
                    for member in archive:
                        if member.name.endswith('/event.json') or member.name.endswith('/sample.json'):
                            logger.info(f"{file}: {member.name}")
                            with archive.extractfile(member) as _file:
                                skipped_lines, skipped_time = self.skip(_file, skip_lines, skip_time)
                                skip_lines, skip_time = max(skip_lines - skipped_lines, 0), max(skip_time - skipped_time, 0)
                                read, sample = await self._read_more(_file, read, first, start, sample, max_lines=max_lines, max_time=max_time)
            else:
                with open(file) as _file:
                    skipped_lines, skipped_time = self.skip(_file, skip_lines, skip_time)
                    skip_lines, skip_time = max(skip_lines - skipped_lines, 0), max(skip_time - skipped_time, 0)
                    read, sample = await self._read_more(_file, read, first, start, sample, max_lines=max_lines, max_time=max_time)

        return read

    def _first(self, files):
        """
        Get the timestamp of the first tweet in the given file or files.

        :param files: The list of file paths from where to read the tweets.
                     If ``.tar.gz`` files are provided, the function looks for ``sample.json`` or ``event.json`` files.
        :type files: list of str

        :return: The timestamp of the first tweet in the given file or files.
        :rtype: str or list of str
        """

        for file in files:
            if file.endswith('.tar.gz'):
                with tarfile.open(file) as archive:
                    for member in archive:
                        if member.name.endswith('/event.json') or member.name.endswith('/sample.json'):
                            logger.info(f"{file}: {member.name}")
                            with archive.extractfile(member) as _file:
                                for line in _file:
                                    tweet = json.loads(line)
                                    return extract_timestamp(tweet)
            else:
                with open(file) as _file:
                    for line in _file:
                        tweet = json.loads(line)
                        return extract_timestamp(tweet)

    async def _read_more(self, file, read, first, start, sample, max_lines=-1, max_time=-1):
        """
        Perform the actual reading from the opened file.

        :param file: The opened file from where to skip the tweets.
        :type file: file
        :param read: The number of tweets read so far.
        :type read: int
        :param first: The timestamp of the first tweet in the list of files, used to regulate the simulated stream.
        :type first: int
        :param start: The timestamp when the reading started, used to regulate the simulated stream.
        :type start: int
        :param sample: The current sampling fraction.
        :type sample: float
        :param max_lines: The maximum number of lines to read.
                          If the number is negative, it is ignored.
        :type max_lines: int
        :param max_time: The maximum time in seconds to spend reading from the file.
                         The time is taken from tweets' timestamps.
                         If the number is negative, it is ignored.
        :type max_time: int

        :return: A tuple including the number of tweets read from the file and the current sampling fraction.
        :rtype: tuple
        """

        # go through each line and add it to the queue
        for i, line in enumerate(file):
            tweet = json.loads(line)
            created_at = extract_timestamp(tweet)

            # if the maximum number of lines, or the time, has been exceeded, stop reading
            if max_lines >= 0 and read >= max_lines:
                return read, sample

            if max_time >= 0 and created_at - first >= max_time:
                return read, sample

            """
            If the tweet is 'in the future', stop reading until the reader catches up.
            It is only after it catches up that the tweet is added to the queue.
            """
            elapsed = time.time() - start
            if (created_at - first) / self.speed > elapsed and self.active:
                await asyncio.sleep((created_at - first) / self.speed - elapsed)

            # if the reader has been interrupted, stop reading
            if not self.active:
                return read, sample

            # only add a tweet if it is valid
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

        return read, sample
