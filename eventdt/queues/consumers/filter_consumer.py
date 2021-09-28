"""
The :class:`~queues.consumers.filter_consumer.FilterConsumer` builds on the base :class:`~queues.consumers.Consumer` class.
Its job is to filter incoming tweets, only adding to the queue tweets that satisfy some conditions.
"""

from abc import abstractmethod
import asyncio
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from queues import Queue
from queues.consumers import Consumer

class FilterConsumer(Consumer):
    """
    The :class:`~queues.consumers.filter_consumer.FilterConsumer` class acts as a supervisor for an incoming stream of tweets.
    It reads all tweets, but only passes to a consumer those that satisfy certain conditions.
    In its state, the consumer stores a list of these conditions.

    This class mainly re-works the basic consumption method to decide whether to accept tweets.
    To change how the consumer works, you need to override some or all of the following functions:

    - <Optional> :func:`~queues.consumers.filter_consumer.FilterConsumer._preprocess`: Pre-process all incoming tweets.
      This function is used whenever the child consumers all perform the same pre-processing tasks.
      By default, it does not change tweets.
    - <Required> :func:`~queues.consumers.filter_consumer.FilterConsumer._satisfies`: Check whether a tweet satisfies a condition.
      This is the central function that filters tweets.

    The ``filters`` and the :func:`~queues.consumers.filter_consumer.FilterConsumer._satisfies` are tightly-linked.
    Each filter becomes the input to the latter function.
    For example, the following implementation of the :func:`~queues.consumers.filter_consumer.FilterConsumer._satisfies` function splits tweets according to their length.
    Therefore the splits should be ranges of tweet lengths, such as ``(0, 140), (140, 280)``.

    .. code-block:: python

        def _satisfies(self, item, condition):

            min_length, max_length = condition
            return min_length <= len(item['text']) < max_length

    :ivar filters: A list of filters, or conditions that determine whether a tweet should be retained or discarded.
                   The type of the filters depends on what the :func:`~queues.consumers.filter_consumer.FilterConsumer._satisfies` function looks for.
    :type filters: list
    :ivar matches: The function that is used to check whether a tweet satisfies the filters.

                   - If ``any`` is provided, the consumer assigns a tweet to a stream if it satisfies any of the filters.
                   - If ``all`` is provided, the consumer assigns a tweet to a stream if it satisfies all of the filters.

                   A custom function can be provided.
                   For example, a custom function can define that a tweet satisfies the filter if it includes at least two conditions in it.
                   If one is given, it must receive as input a number of boolean values.
                   Its output must be a boolean indicating whether the tweet satisfies the conditions of the filter.
    :vartype matches: func
    :ivar consumer: The consumer that will receive the tweets that satisfy the filter.
    :vartype consumer: list of :class:`~queues.consumers.Consumer`
    """

    def __init__(self, queue, filters, consumer, matches=all, *args, **kwargs):
        """
        Initialize the consumer with its :class:`~queues.Queue`, which receives tweets to filter.
        This function creates one :class:`~queues.consumers.Consumer` which will receive the filtered tweets.
        Any additional arguments or keyword arguments are passed on to this consumer's constructor.

        :param queue: The queue that receives the entire stream.
        :type queue: :class:`~queues.Queue`
        :param filters: A list of filters, or conditions that determine whether a tweet should be retained or discarded.
                        The type of the filters depends on what the :func:`~queues.consumers.filter_consumer.FilterConsumer._satisfies` function looks for.
        :type filters: list or tuple
        :param consumer: The type of :class:`~queues.consumers.Consumer` to create, which will process filtered lists.
        :type consumer: type
        :param matches: The function that is used to check whether a tweet satisfies the filters.

                        - If ``any`` is provided, the consumer assigns a tweet to a stream if it satisfies any of the filters.
                        - If ``all`` is provided, the consumer assigns a tweet to a stream if it satisfies all of the filters.

                        A custom function can be provided.
                        For example, a custom function can define that a tweet satisfies the filter if it includes at least two conditions in it.
                        If one is given, it must receive as input a number of boolean values.
                        Its output must be a boolean indicating whether the tweet satisfies the conditions of the split.
        :type matches: func
        """

        super(FilterConsumer, self).__init__(queue)

        if type(filters) not in [ list, tuple ]:
            raise ValueError(f"Expected a list or tuple of filters; received { type(filters) }")

        self.filters = filters
        self.matches = matches
        self.consumer = consumer(Queue(), *args, **kwargs)

    async def run(self, wait=0, max_inactivity=-1, *args, **kwargs):
        """
        Update the flags to indicate that the consumer is running and start consuming the :class:`~queues.Queue`.
        At the same time, the :class:`~queues.consumers.filter_consumer.FilterConsumer` starts running the consumer that processes filtered tweets.

        If the :class:`~queues.Queue` is being populated by a :class:`~twitter.file.FileReader`, there might be an initial delay until the :class:`~queues.Queue` receives any data.
        This is because the :class:`~twitter.file.FileReader` supports skipping tweets, which introduces some latency.
        When skipping a lot of time or lines, this latency can get very large.
        You can use the ``wait`` parameter to delay running the consumer by a few seconds to wait for the :class:`~twitter.file.FileReader` to finish skipping part of the corpus.

        In addition, corpora may be sparse with periods of time during which little data is fed to the consumer.
        This can also happen when the :class:`~twitter.listeners.TweetListener` fails to collect tweets because of errors in the Twitter API.
        The ``max_inactivity`` parameter is the allowance, in seconds, for how long the consumer should wait without receiving input before it decides no more data will arrive and stop.

        :param wait: The time, in seconds, to wait until starting to consume the :class:`~queues.Queue`.
                     This is used when the :class:`~twitter.file.FileReader` spends a lot of time skipping tweets.
        :type wait: int
        :param max_inactivity: The maximum time, in seconds, to wait idly without input before stopping the consumer.
                               If it is negative, the consumer keeps waiting for input indefinitely.
        :type max_inactivity: int

        :return: The output from the filter consumer's own consumer.
        :rtype: any
        """

        await asyncio.sleep(wait)
        self._started()
        results = await asyncio.gather(
            self._consume(*args, max_inactivity=max_inactivity, **kwargs),
            self.consumer.run(wait=wait, max_inactivity=-1)
        )
        self._stopped()
        return { **results[1], **results[0] } # reversed so that the number of filtered tweets is not overwritten

    def stop(self):
        """
        Set a flag to stop accepting new tweets.
        This function also stops the child consumer.

        .. note::
            Contrary to the name of the function, the function sets the ``active`` flag to ``False``, not the ``stopped`` flag to ``True``.
            This function merely asks the consumer to stop accepting new tweets for processing.
            When the consumer actually stops, after it finishes processing whatever tweets it has, it sets the ``stopped`` flag to ``True`` itself.
        """

        self.active = False
        self.consumer.stop()

    async def _consume(self, max_inactivity, *args, **kwargs):
        """
        Consume the queue, filtering the tweets before passing them on to the consumer

        :param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
                               If it is negative, the consumer keeps waiting for input until the maximum time expires.
        :type max_inactivity: int

        :return: A dictionary with the number of consumed tweets in the ``consumed`` key.
                 Only tweets that pass through the filters are considered to be consumed.
        :rtype: dict
        """

        consumed = 0

        # the consumer should keep working until it is stopped
        while self.active:
            # if the queue is idle, wait for input
            inactive = await self._wait_for_input(max_inactivity=max_inactivity)
            if not inactive:
                break

            # consumption empties the queue and goes over all of its items
            items = self.queue.dequeue_all()
            items = [ self._preprocess(item) for item in items ]

            # check which items satisfy conditions to be added to the consumers
            for item in items:
                if self._satisfies(item, self.filters):
                    consumed += 1
                    self.consumer.queue.enqueue(item)

        self.stop()
        return { 'filter_consumed': consumed }

    @abstractmethod
    def _satisfies(self, item, condition):
        """
        Check whether the given item satisfies the condition.

        :param item: The tweet, or a pre-processed version of it.
        :type item: any
        :param condition: The condition to check for.
                          The type of the condition depends on what the function looks for.
        :type condition: any

        :return: A boolean indicating whether the given item satisfies the condition.
                 If it satisfies the condition, the split consumer adds the item to the corresponding stream.
        :rtype: bool
        """

        pass

    def _preprocess(self, tweet):
        """
        Pre-process the given tweet.

        This function is used when all of the :class:`~queues.consumers.filter_consumer.FilterConsumer`'s own consumers perform the same pre-processing on the tweet.
        In this case, pre-processing can be used to make the child consumers more efficient by pre-processing the tweets only once.

        By default, this function does not change the tweet.

        :param tweet: The tweet to pre-process.
        :type tweet: dict

        :return: The pre-processed tweet.
                 This function does not change the tweet at all, but it can be overriden.
        :rtype: dict
        """

        return tweet

class DummyFilterConsumer(FilterConsumer):
    """
    A dummy :class:`~queues.consumers.filter_consumer.FilterConsumer` that accepts all tweets.
    It is used only for testing purposes.
    """

    def _satisfies(self, item, condition):
        """
        This function always returns true, adding the tweets to all streams.

        :param item: The tweet, or a pre-processed version of it.
        :type item: any
        :param condition: The condition to check for.
        :type condition: any

        :return: A boolean value of ``True``, adding the tweet to all streams.
        :rtype: bool
        """

        return True
