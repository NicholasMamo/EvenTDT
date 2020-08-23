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

	:ivar splits: A list of splits, or conditions that determine into which queue a tweet goes.
	:vartype splits: list
	"""

	def __init__(self, queue, splits):
		"""
		Initialize the consumer with its :class:`~queues.Queue`.

		:param queue: The queue that receives the entire stream.
		:type queue: :class:`~queues.Queue`
		:param splits: A list of splits, or conditions that determine into which queue a tweet goes.
		:type splits: list
		"""

		super(SplitConsumer, self).__init__(queue)
		self.splits = splits
