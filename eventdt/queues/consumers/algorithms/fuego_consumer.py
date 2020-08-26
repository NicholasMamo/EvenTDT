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
