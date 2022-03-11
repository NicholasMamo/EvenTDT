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

    The pace of the :class:`~twitter.file.staggered_reader.StaggeredFileReader` is governed by the ``rate`` and the ``sample``.
    The ``rate`` is the number of tweets to read per second from the file.
    The :class:`~twitter.file.staggered_reader.StaggeredFileReader` does not read a bunch of tweets and sleeps for the rest of the second, but spaces them out over a second.

    On the other hand, the ``sample`` parameter is used as a systematic sampling mechanism.
    For every :math:`sample` tweets, the staggered reader reads only one.
    By the end, the staggered reader reads :math:`1/sample` of all tweets in the corpus.

    :ivar rate: The number of lines to read per second.
    :vartype rate: float
    :ivar sample: The fraction of tweets to read.
                  The reader uses systematic sampling, reading $\\frac{1}{n}$ samples.
                  If 1 is given, the simulated reader reads all tweets.
                  If 0.5 is given, the simulated reader reads every other tweet.
    :vartype sample: int or float
    """

    def __init__(self, queue, rate=1, sample=1, *args, **kwargs):
        """
        Create the :class:`~twitter.file.staggered_reader.StaggeredFileReader` with the file from where to read tweets and the :class:`~queues.Queue` where to store them.
        The ``rate`` and ``sample`` are extra parameters in addition to the :class:`~twitter.file.FileReader`'s parameters.

        :param queue: The queue to which to add the tweets.
        :type queue: :class:`~queues.Queue`
        :param rate: The number of lines to read per second.
        :type rate: float
        :param sample: The fraction of tweets to read.
                       The reader uses systematic sampling, reading $\\frac{1}{n}$ samples.
                       If 1 is given, the simulated reader reads all tweets.
                       If 0.5 is given, the simulated reader reads every other tweet.
        :type sample: int or float

        :raises ValueError: When the rate is not an integer.
        :raises ValueError: When the rate is zero or negative.
        :raises ValueError: When the number of lines to skip after each read is not an integer.
        :raises ValueError: When the number of lines to skip after each read is negative.
        :raises ValueError: When the sampling rate is not between 0 and 1.
        """

        super(StaggeredFileReader, self).__init__(queue, *args, **kwargs)

        """
        Validate the inputs.
        """
        if rate % 1:
            raise ValueError(f"The rate must be an integer; received {rate}")

        if rate <= 0:
            raise ValueError(f"The rate must be positive; received {rate}")

        if sample > 1 or sample < 0:
            raise ValueError(f"The rate of lines to skip after each read must be between 0 and 1; received {sample}")

        self.rate = rate
        self.sample = sample

    @FileReader.reading
    async def read(self, file, max_lines=-1, max_time=-1, skip_lines=0, skip_time=0):
        """
        Read the file and add each line as a dictionary to the queue.

        :param file: The file path or a list of file paths from where to read the tweets.
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
        first = None

        files = [ file ] if type(file) is str else file
        for file in files:
            with open(file) as _file:
                skipped_lines, skipped_time = self.skip(_file, skip_lines, skip_time)
                skip_lines, skip_time = max(skip_lines - skipped_lines, 0), max(skip_time - skipped_time, 0)

                # go through each line and add it to the queue
                for i, line in enumerate(_file):
                    start = time.time()
                    tweet = json.loads(line)
                    created_at = extract_timestamp(tweet)
                    first = first or created_at

                    # if the maximum number of lines, or time, has been exceeded, stop reading
                    if max_lines >= 0 and read >= max_lines:
                        return read

                    if max_time >= 0 and created_at - first >= max_time:
                        return read

                        # if the reader has been interrupted, stop reading
                    if not self.active:
                        return read

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

                    """
                    If there is a limit on the number of lines to read per minute, sleep a bit.
                    The calculation considers how long reading the tweet took.
                    """
                    elapsed = time.time() - start
                    if self.rate > 0:
                        sleep = 1/self.rate - elapsed
                        if sleep > 0:
                            time.sleep(sleep)

        return read
