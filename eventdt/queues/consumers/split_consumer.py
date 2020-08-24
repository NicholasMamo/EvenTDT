"""
The :class:`~queues.consumers.split_consumer.SplitConsumer` builds on the base :class:`~queues.consumers.Consumer` class, but splits the incoming stream of tweets into several streams.
These streams are simply a list of :class:`~queues.Queue` instances.

The :class:`~queues.consumers.split_consumer.SplitConsumer` creates as many :class:`~queues.consumers.Consumer` instances as there :class:`~queues.Queue` instances—one :class:`~queues.Queue` for each :class:`~queues.consumers.Consumer`.
All consumers process the tweets in their own :class:`~queues.Queue` as usual.

The way the consumer splits the stream depends entirely on the the implementation.
The consumer can assign each tweet to just one stream, to multiple streams, or even discard tweets.

.. note::

	The :class:`~queues.consumers.split_consumer.SplitConsumer` is based on the :class:`~queues.consumers.Consumer` class, so it operates in real-time.
	All this means is that it sends tweets to the appropriate consumer without delay.
	The processing, however, does not have to be in real-time.
	The individual consumers that process the split streams can be based on the :class:`~queues.consumers.buffered_consumer.BufferedConsumer` and process tweets in batches.
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

class SplitConsumer(Consumer):
	"""
	The :class:`~queues.consumers.split_consumer.SplitConsumer` class acts as a supervisor.
	It reads all of the incoming tweets and dispatches them to one of its consumers.

	In its state, the consumer maintains a list of these conditions.
	Associated with each condition is one class:`~queues.consumers.Consumer` that receives the tweets from that split.

	This class mainly re-works the basic consumption method to decide where to send off tweets.
	To change how the consumer works, you might need to override the following functions:

	- <Optional> :func:`~queues.consumers.split_consumer.SplitConsumer._preprocess`: Pre-process all incoming tweets.
	  This function is used whenever the child consumers all perform the same pre-processing tasks.
	  When tweets can be added to multiple streams, this function can improve efficiency.
	  By default, it does not change tweets.
	- <Required> :func:`~queues.consumers.split_consumer.SplitConsumer._satisfies`: Check whether a tweet satisfies a condition.
	  This is the central function that all split consumers need to implement.
	  It decides how to route tweets to the different tweets.

	The ``splits`` and the :func:`~queues.consumers.split_consumer.SplitConsumer._satisfies` are tightly-linked.
	Each split becomes the input to the latter function.
	For example, the following implementation of the :func:`~queues.consumers.split_consumer.SplitConsumer._satisfies` function splits tweets according to their length.
	Therefore the splits should be ranges of tweet lengths, such as ``(0, 140), (140, 280)``.

	.. code-block:: python

		def _satisfies(self, item, condition):

			min_length, max_length = condition
			return min_length <= len(item['text']) < max_length

	:ivar splits: A list of splits, or conditions that determine into which queue a tweet goes.
				  The type of the splits depends on what the :func:`~queues.consumers.split_consumer.SplitConsumer._satisfies` function looks for.
	:vartype splits: list
	:ivar consumers: The consumers that will receive the tweets from the different splits.
					 Each consumer corresponds to one split.
	:vartype consumers: list of :class:`~queues.consumers.Consumer`
	"""

	def __init__(self, queue, splits, consumer, *args, **kwargs):
		"""
		Initialize the consumer with its :class:`~queues.Queue`.

		For each given split, this function creates one :class:`~queues.consumers.Consumer` of the given type.
		This consumer has its own queue, which receive tweets that satisfy the associated condition.

		Any additional arguments or keyword arguments are passed on to the consumer's constructor.

		:param queue: The queue that receives the entire stream.
		:type queue: :class:`~queues.Queue`
		:param splits: A list of splits, or conditions that determine into which queue a tweet goes.
					   The type of the splits depends on what the :func:`~queues.consumers.split_consumer.SplitConsumer._satisfies` function looks for.
		:type splits: list or tuple
		:param consumer: The type of :class:`~queues.consumers.Consumer` to create for each split.
		:type consumer: type
		"""

		super(SplitConsumer, self).__init__(queue)

		if type(splits) not in [ list, tuple ]:
			raise ValueError(f"Expected a list or tuple of splits; received { type(splits) }")

		self.splits = splits
		self.consumers = self._consumers(consumer, len(splits), *args, **kwargs)

	async def run(self, wait=0, max_inactivity=-1, *args, **kwargs):
		"""
		Update the flags to indicate that the consumer is running and start consuming the :class:`~queues.Queue`.
		At the same time, the :class:`~queues.consumers.split_consumer.SplitConsumer` starts running its own consumers.

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

		:return: The output of the consumer, if any, as a tuple.
		:rtype: any
		"""

		await asyncio.sleep(wait)
		self._started()
		results = await asyncio.gather(
			self._consume(*args, max_inactivity=max_inactivity, **kwargs),
			*[ consumer.run(wait=wait, max_inactivity=max_inactivity) for consumer in self.consumers ]
		)
		self._stopped()
		return results[1:]

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

	def _consumers(self, consumer, n, *args, **kwargs):
		"""
		Create the consumers which will receive the tweets from each stream.

		Any additional arguments or keyword arguments are passed on to the consumer's constructor.

		:param consumer: The type of :class:`~queues.consumers.Consumer` to create.
		:type consumer: type
		:param n: The number of cnsumers to create.
				  This number is equivalent to the number of splits.
		:type n: int

		:return: A number of consumers, equivalent to the given number.
				 All consumers are identical to each other, but have their own :class:`~queues.Queue`.
		:rtype: list of :class:`~queues.consumers.Consumer`
		"""

		return [ consumer(Queue(), *args, **kwargs) for _ in range(n) ]

	def _preprocess(self, tweet):
		"""
		Pre-process the given tweet.

		This function is used when all of the :class:`~queues.consumers.split_consumer.SplitConsumer`'s own consumers perform the same pre-processing on the tweet.
		In this case, pre-processing can be used to make the child consumers more efficient by pre-processing the tweets only once.

		By default, this function does not change the tweet.

		:param tweet: The tweet to pre-process.
		:type tweet: dict

		:return: The pre-processed tweet.
				 This function does not change the tweet at all, but it can be overriden.
		:rtype: dict
		"""

		return tweet

class DummySplitConsumer(SplitConsumer):
	"""
	A dummy :class:`~queues.consumers.split_consumer.SplitConsumer` that adds all tweets to all streams.
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
