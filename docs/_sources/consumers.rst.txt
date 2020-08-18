************
9. Consumers
************

.. meta::
   :description: The consumer functionality of EvenTDT
   :keywords: Python, TDT, queue, consumer

.. automodule:: queues
  :members:
  :special-members:

.. _consumers:

Consumers
=========

Queue data is consumed by consumers.
Each consumer dequeues the accumulated data and processes it or outputs it.
There are various base classes for consumers, covering both real-time and buffered consumption.

.. automodule:: queues.consumers.consumer
   :members:
   :special-members:

.. automodule:: queues.consumers.buffered_consumer
   :members:
   :special-members:

Simple Consumers
----------------

.. automodule:: queues.consumers.print_consumer
   :members:
   :special-members:

.. automodule:: queues.consumers.stat_consumer
   :members:
   :special-members:

.. _consumers_algorithms:

Algorithms
----------

.. automodule:: queues.consumers.eld_consumer
   :members:
   :special-members:

.. automodule:: queues.consumers.fire_consumer
   :members:
   :special-members:

.. automodule:: queues.consumers.zhao_consumer
   :members:
   :special-members:
