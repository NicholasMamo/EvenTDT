"""
FUEGO (codename that means absolutely nothing) is a feature-pivot consumer built on the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`'s own feature-pivot method.
Differently from the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`, FUEGO uses a sliding time-window instead of checkpoints.
This allows for more accurate results in real-time.

.. note::

	Since FUEGO uses only a feature-pivot method, it is not very granular on its own.
	Therefore this consumer can only extract granular developments when combined with a :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer`.
	For a combination of document-pivot and feature-pivot approaches, see the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`.
"""