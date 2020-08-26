"""
FUEGO (codename that means absolutely nothing) is a feature-pivot consumer built on the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`'s own feature-pivot method.
Differently from the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`, FUEGO uses a sliding time-window instead of checkpoints.
This allows for more accurate results in real-time.

.. note::

	Since FUEGO uses only a feature-pivot method, it is not very granular on its own.
	Therefore this consumer can only extract granular developments when combined with a :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer`.
	For a combination of document-pivot and feature-pivot approaches, see the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from queues.consumers import Consumer

class FUEGOConsumer(Consumer):
	"""
	The :class:`~queues.consumers.fuego_consumer.FUEGOConsumer` is a real-time consumer with a custom algorithm to detect topics.
	Unlike other :ref:`consumers <consumers>`, the consumer has both a :func:`~queues.consumers.Consumer.ELDConsumer.run` and a :func:`~queues.consumers.fuego_consumer.FUEGOConsumer.understand` functions.
	The former is the normal processing step, whereas the :func:`~queues.consumers.fuego_consumer.FUEGOConsumer.understand` function precedes the event and builds a TF-IDF scheme for the event.
	"""

	def __init__(self, queue, *args, **kwargs):
		"""
		Create the consumer with a queue.

		:param queue: The queue that will be receiving tweets.
					  The consumer reads tweets from this queue and processes them.
		:type queue: :class:`~queues.Queue`
		"""

		super(FUEGOConsumer, self).__init__(queue, *args, **kwargs)

	async def understand(self, max_inactivity=-1, *args, **kwargs):
		"""
		Understanding precedes the event and is tasked with generating knowledge automatically.

		During understanding, the :class:`~queues.consumers.fuego_consumer.FUEGOConsumer` creates a :class:`~nlp.weighting.TermWeightingScheme` with an :class:`~nlp.weighting.global_schemes.idf.IDF` table based on the pre-event discussion.
		The consumer uses the :class:`~nlp.weighting.TermWeightingScheme` while processing tweets in real-time.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, it is ignored.
		:type max_inactivity: int

		:return: The :class:`~nlp.weighting.tfidf.TFIDF` scheme built from the documents from the pre-event tweets.
		:rtype: :class:`~nlp.weighting.tfidf.TFIDF`
		"""

		self._started()
		tfidf = await self._construct_idf(max_inactivity=max_inactivity)
		logger.info(f"TF-IDF constructed with { tfidf.global_scheme.documents } documents", process=str(self))
		self._stopped()
		return tfidf

	async def _construct_idf(self, max_inactivity):
		"""
		Construct the TF-IDF table from the pre-event discussion.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, it is ignored.
		:type max_inactivity: int

		:return: The constructed TF-IDF scheme.
		:rtype: :class:`~nlp.weighting.tfidf.TFIDF`
		"""

		return { }
	async def _consume(self, max_inactivity, *args, **kwargs):
		"""
		Consume and process the documents in the queue.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int

		:return: The constructed timeline.
		:rtype: :class:`~summarization.timeline.Timeline`
		"""

		pass
