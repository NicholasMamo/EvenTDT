"""
The :class:`~twitter.listeners.tweet_listener.TweetListener` is based on Tweepy's :class:`tweepy.stream.StreamListener`.
This listener receives tweets and saves them to file.
It is not responsible for filtering tweets; that is, the stream settings are set beforehand, and the :class:`~twitter.listeners.tweet_listener.TweetListener` only receives the output from this stream.

The :class:`~twitter.listeners.tweet_listener.TweetListener` accumulates tweets and periodically writes them to a file.
When the stream closes, it writes the last tweets to the file.

Tweet objects include a lot of attributes, which may not always be required and result in large corpora.
Therefore this listener also supports attribute filtering, which removes needless data from tweets before saving them to file.
"""

from tweepy.streaming import StreamListener

import json
import os
import sys
import time

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from logger import logger
from twitter import *

class TweetListener(StreamListener):
    """
    The :class:`~twitter.listeners.tweet_listener.TweetListener` handles the tweets that the stream sends.
    It does not configure the stream, but only processes the tweets it sends.

    The :class:`~twitter.listeners.tweet_listener.TweetListener`'s state stores the file pointer where to save files.
    By default, it accumulates tweets until the ``THRESHOLD`` constant is reached.
    At that point, the accumulated tweets are saved to file.
    In the meantime, it stores the tweets in the list of ``tweets``.

    Although listeners do not control the stream's specifications, they can stop it.
    The :class:`~twitter.listeners.tweet_listener.TweetListener` receives the ``max_time`` parameter which specifies, in seconds, the time to spend receiving tweets.
    The :func:`~twitter.listeners.tweet_listener.TweetListener.on_data` function stops the stream when it receives a tweet after this time expires.
    When it stops the stream, it saves any pending tweets to file.

    Tweet objects contain many attributes, some of which may not be needed, but which create large corpora.
    For example, feature-pivot algorithms that rely only on volume do not need anything except the tweet ID and the timestamp.
    Therefore the :class:`~twitter.listeners.tweet_listener.TweetListener` also stores the ``attributes`` variable.
    This represents a list of tweet attributes to save to file.
    If it is not given, the tweets are stored without any filtering.

    :cvar THRESHOLD: The number of tweets to accumulate before writing them to file.
    :vartype THRESHOLD: int

    :ivar ~.file: The opened file pointer where to write the tweets.
    :vartype ~.file: file
    :ivar tweets: The list of read tweets that have not been written to file yet.
    :vartype tweets: list
    :ivar max_time: The maximum time in seconds to spend receiving tweets.
                    When this time expires, the listener instructs the stream to stop accepting tweets.
    :vartype max_time: int
    :ivar start: The timestamp when the listener started waiting for tweets.
                 This variable is used to calculate the time the listener has spent receiving tweets.
    :vartype start: int
    :ivar retweets: A boolean indicating whether to collect retweets or not.
    :vartype retweets: bool
    :ivar attributes: The attributes to save from each tweet.
                      If ``None`` is given, the entire tweet objects are saved.
    :vartype attributes: list of str or None
    :var collected: The number of collected tweets, after filtering.
    :vartype collected: int
    """

    THRESHOLD = 200

    def __init__(self, f, retweets=True, max_time=3600, attributes=None):
        """
        Create the listener.
        Simultaneously set the file and the list of tweets.
        By default, the stream continues processing for an hour.

        :param f: The opened file pointer where to write the tweets.
        :type f: file
        :param retweets: A boolean indicating whether to collect retweets or not.
        :type retweets: bool
        :param max_time: The maximum time in seconds to spend receiving tweets.
                         When this time expires, the listener instructs the stream to stop accepting tweets.
        :type max_time: int
        :param attributes: The attributes to save from each tweet.
                           If ``None`` is given, the entire tweet objects are saved.
        :type attributes: list of str or None
        """

        self.file = f
        self.tweets = [ ]
        self.max_time = max_time
        self.start = time.time()
        self.retweets = retweets
        self.attributes = attributes or [ ]
        self.collected = 0

    def flush(self):
        """
        Flush the tweets to file.
        Data is saved as a string to file.

        .. note::

            At this point, tweets are already JSON dictionaries and have a newline character at the end.
            Since each tweet is a string representing a line, this function only concatenates these lines together.
        """

        self.collected += len(self.tweets)
        self.file.write(''.join(self.tweets))
        self.tweets = [ ]

    def on_data(self, data):
        """
        When the listener receives tweets, add them to a list.
        If there are many tweets, save them to file and reset the list of tweets.

        When the function adds tweets to the list, they are strings, ready to be saved by the :func:`~twitter.listeners.tweet_listener.TweetListener.flush` function.
        That means they are JSON-encoded strings with a newline character at the end.

        This function also checks if the listener has been listening for tweets for a long time.
        If it exceeds the ``max_time``, the function returns ``False`` so that the stream ends.

        :param data: The received data.
        :type data: str

        :return: A boolean indicating if the listener has finished reading tweets.
                 It is set to ``True`` normally.
                 When the elapsed time exceeds the ``max_time`` parameter, the :class:`~twitter.listeners.tweet_listener.TweetListener` returns ``False``.
                 This instructs the stream to stop receiving tweets.
        :rtype: bool
        """

        tweet = json.loads(data)
        if 'id' in tweet:
            if self.retweets or not is_retweet(tweet):
                tweet = self.filter(tweet)
                self.tweets.append(json.dumps(tweet) + "\n")


            """
            If the tweets have exceeded the threshold of tweets, save them to the file.
            """
            if len(self.tweets) >= self.THRESHOLD:
                self.flush()

            """
            Stop listening if the time limit has been exceeded.
            To stop listening, the function returns `False`, but not before saving any pending tweets.
            """
            current = time.time()
            if current - self.start < self.max_time:
                return True
            else:
                self.flush()
                return False

    def filter(self, tweet):
        """
        Filter the given tweet using the attributes specified when creating the :class:`~twitter.listeners.tweet_listener.TweetListener`.
        If no attributes were given, the tweet's attributes are all retained.

        :param tweet: The tweet attributes as a dictionary.
                      The keys are the attribute names and the values are the data.
        :type tweet: dict

        :return: The tweet as a dictionary with only the required attributes.
        :rtype: dict
        """

        """
        Return the tweet as it is if there are no attributes to filter.
        """
        if not self.attributes:
            return tweet

        """
        Otherwise, keep only the attributes in the list.
        """
        return { attribute: tweet.get(attribute) for attribute in self.attributes }

    def on_error(self, status):
        """
        Print any errors.

        :param status: The error status.
        :type status: str
        """

        logger.error(str(status))
