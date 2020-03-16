************
8. Consumers
************

.. meta::
   :description: The consumer functionality of EvenTDT
   :keywords: Python, TDT, queue, consumer

EvenTDT collects tweets and processes them.
In-between collecting and processing, the tweets go into a queue data structure.
In this way, the consumers can process the data in the same order as it was received.
The queue functionality is a special class.

.. automodule:: queues.queue.queue
   :members:
   :private-members:
   :special-members:

Queue data is consumed by consumers.
Each consumer dequeues the accumulated data and processes it or outputs it.
