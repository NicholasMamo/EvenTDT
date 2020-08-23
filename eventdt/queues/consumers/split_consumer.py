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
	Associated with each condition is one class:`~queues.consumers.Consumer` that receives the tweets from that split..

	:ivar splits: A list of splits, or conditions that determine into which queue a tweet goes.
	:vartype splits: list
	:ivar consumers: The consumers that will receive the tweets from the different splits.
					 Each consumer corresponds to one split.
	:vartype consumers: list of :class:`~queues.consumers.Consumer`
	"""

	def __init__(self, queue, splits, consumer):
		"""
		Initialize the consumer with its :class:`~queues.Queue`.

		For each given split, this function creates one :class:`~queues.consumers.Consumer` of the given type.
		This consumer has its own queue, which receive tweets that satisfy the associated condition.

		:param queue: The queue that receives the entire stream.
		:type queue: :class:`~queues.Queue`
		:param splits: A list of splits, or conditions that determine into which queue a tweet goes.
		:type splits: list
		:param consumer: The type of :class:`~queues.consumers.Consumer` to create for each split.
		:type consumer: type
		"""

		super(SplitConsumer, self).__init__(queue)

		self.splits = splits
		self.consumers = self._consumers(consumer, len(splits))

	def _consumers(self, consumer, n):
		"""
		Create the consumers which will receive the tweets from each stream.

		:param consumer: The type of :class:`~queues.consumers.Consumer` to create.
		:type consumer: type
		:param n: The number of cnsumers to create.
				  This number is equivalent to the number of splits.
		:type n: int

		:return: A number of consumers, equivalent to the given number.
				 All consumers are identical to each other, but have their own :class:`~queues.Queue`.
		:rtype: list of :class:`~queues.consumers.Consumer`
		"""

		return [ consumer(Queue()) for _ in range(n) ]

class DummySplitConsumer(SplitConsumer):
	"""
	A dummy :class:`~queues.consumers.split_consumer.SplitConsumer` that does nothing.
	It is used only for testing purposes.
	"""

	async def _consume(self, max_inactivity, *args, **kwargs):
		"""
		Consume the queue, doing nothing.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int
		"""

		pass
