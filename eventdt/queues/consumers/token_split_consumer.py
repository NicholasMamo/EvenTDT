"""
The :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer` splits tweets into different streams based on what tokens they include.
This means that all splits have a simple, thematic focus.

This split consumer allows the splits to overlap, which means that tweets can be assigned to multiple streams.
However, it discards tweets that do not satisfy any split.
"""

from .split_consumer import SplitConsumer

class TokenSplitConsumer(SplitConsumer):
	"""
	The :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer` splits tweets into different streams based on what tokens they include.
	"""

	def _satisfies(self, item, condition):
		"""
		"""

		pass
