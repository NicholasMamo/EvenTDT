************
9. Consumers
************

.. meta::
   :description: The consumer functionality of EvenTDT
   :keywords: Python, TDT, queue, consumer

Queues
======

EvenTDT collects tweets and processes them.
In-between collecting and processing, the tweets go into a queue data structure.
In this way, the consumers can process the data in the same order as it was received.
The queue functionality is a special class.

.. automodule:: queues.queue
   :members:
   :private-members:
   :special-members:

Consumers
=========

Queue data is consumed by consumers.
Each consumer dequeues the accumulated data and processes it or outputs it.
There are various base classes for consumers, covering both real-time and buffered consumption.

.. automodule:: queues.consumers.consumer
   :members:
   :private-members:
   :special-members:

.. automodule:: queues.consumers.buffered_consumer
   :members:
   :private-members:
   :special-members:

Simple Consumers
----------------

.. automodule:: queues.consumers.print_consumer
   :members:
   :private-members:
   :special-members:

.. automodule:: queues.consumers.stat_consumer
   :members:
   :private-members:
   :special-members:

Algorithms
----------

.. automodule:: queues.consumers.eld_consumer
   :members:
   :private-members:
   :special-members:

.. automodule:: queues.consumers.fire_consumer
   :members:
   :private-members:
   :special-members:

.. automodule:: queues.consumers.zhao_consumer
   :members:
   :private-members:
   :special-members:
