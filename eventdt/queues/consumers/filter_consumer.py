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

    async def _consume(self, max_inactivity, *args, **kwargs):
        """
        Consume the queue, filtering the tweets before passing them on to the consumer

        :param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
                               If it is negative, the consumer keeps waiting for input until the maximum time expires.
        :type max_inactivity: int
        """

        pass

class DummyFilterConsumer(FilterConsumer):
    """
    A dummy :class:`~queues.consumers.filter_consumer.FilterConsumer` that accepts all tweets.
    It is used only for testing purposes.
    """
