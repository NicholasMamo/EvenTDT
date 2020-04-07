#!/usr/bin/env python3

"""
The consumer receives an input file and consumes it with one of the given consumers.
This consumer is split into two asynchronous tasks.
The first task reads the file, and the second consumes it.

If an understanding file is provided, it is used for the understanding task.
The process is similar to before, with two asynchronous tasks.
The first task reads the file, and the second consumes it, this time to understand the event.

All dataset files are expected to contain one tweet on every line, encoded as JSON strings.

To run the script, use:

.. code-block:: bash

    ./implementation/consume.py \\
	-f data/event/event.json \\
	-c PrintConsumer

Accepted arguments:

	- ``-f --file``				*<Required>* The file to consume.
	- ``-c --class``			*<Required>* The consumer to use; supported: `ELDConsumer`, `FIREConsumer`, `PrintConsumer`, `StatConsumer`, `ZhaoConsumer`.
	- ``-u --understanding``	*<Optional>* The understanding file used to understand the event.
	- ``-s --speed``			*<Optional>* The speed at which the file is consumed, defaults to 1.

"""

import argparse
import asyncio
import os
import signal
import sys

from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from logger import logger
from queues import Queue
from queues.consumers import *
from twitter.file import SimulatedFileReader

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``				*<Required>* The file to consume.
		- ``-c --class``			*<Required>* The consumer to use; supported: `ELDConsumer`, `FIREConsumer`, `PrintConsumer`, `StatConsumer`, `ZhaoConsumer`.
		- ``-u --understanding``	*<Optional>* The understanding file used to understand the event.
		- ``-s --speed``			*<Optional>* The speed at which the file is consumed, defaults to 1.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Consume a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The file to consume.')
	parser.add_argument('-c', '--consumer', type=consumer, required=True,
						help='<Required> The consumer to use.')
	parser.add_argument('-u', '--understanding', type=str, required=False,
						help='<Optional> The understanding file used to understand the event.')
	parser.add_argument('-s', '--speed', type=float, required=False, default=1,
						help='<Optional> The understanding file used to understand the event.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()

	"""
	Register the queue in the base manager.
	"""
	BaseManager.register("Queue", Queue)

	"""
	When the consumption tool is interrupted, do nothing.
	The separate processes receive the instruction separately.
	"""
	def sigint_handler(signal, frame):
		return

	signal.signal(signal.SIGINT, sigint_handler)

	"""
	If an understanding file was given, read and understand the file.
	This understanding replaces the understanding file.
	"""
	if args.understanding:
		logger.info("Starting understanding period")
		understanding = understand(**vars(args))
		args.understanding = understanding
		logger.info("Understanding period ended")

	"""
	Consume the event with the main file.
	"""
	consume(**vars(args))

	asyncio.get_event_loop().close()

def understand(understanding, consumer, *args, **kwargs):
	"""
	Run the understanding process.
	The arguments and keyword arguments should be the command-line arguments.

	Understanding uses two processes:

		#. Stream the file, and
		#. Understand the file.

	Both processes share the same event loop and queue.

	.. note::

		Understanding is sped up, on the assumption that processing is done retrospectively.

	:param understanding: The path to the file containing the event's understanding.
	:type understanding: str
	:param consumer: The type of consumer to use.
	:type consumer: :class:`~queues.consumers.consumer.Consumer`

	:return: A dictionary containing the understanding.
	:rtype: dict
	"""

	loop = asyncio.get_event_loop()

	"""
	Create a queue that will be shared between the streaming and understanding processes.
	"""
	queue_manager = BaseManager()
	queue_manager.start()
	queue = queue_manager.Queue()
	consumer = consumer(queue)

	"""
	Create a shared dictionary that processes can use to communicate with this function.
	"""
	manager = Manager()
	comm = manager.dict()

	"""
	Create and start the streaming and understanding processes.
	"""
	stream = Process(target=stream_process,
					 args=(loop, queue, understanding, ),
					 kwargs={ 'speed': 120 })
	understand = Process(target=understand_process, args=(comm, loop, consumer, ))
	stream.start()
	understand.start()
	stream.join()
	understand.join()

	"""
	Clean up understanding.
	"""
	understanding = dict(comm)
	manager.shutdown()
	queue_manager.shutdown()

	return understanding

def consume(file, consumer, speed, understanding=None, *args, **kwargs):
	"""
	Run the consumption process.
	The arguments and keyword arguments should be the command-line arguments.

	Consumption uses two processes:

		#. Stream the file, and
		#. Consume the file.

	Both processes share the same event loop and queue.

	:param file: The path to the file containing the event's tweets.
	:type file: str
	:param consumer: The type of consumer to use.
	:type consumer: :class:`~queues.consumers.consumer.Consumer`
	:param speed: The speed with which to read the file.
	:type speed: float
	:param understanding: The path to the file containing the event's understanding.
	:type understanding: str
	"""

	loop = asyncio.get_event_loop()

	"""
	Create a queue that will be shared between the streaming and understanding processes.
	"""
	queue_manager = BaseManager()
	queue_manager.start()
	queue = queue_manager.Queue()
	consumer = consumer(queue)

	"""
	Create and start the streaming and consumption processes.
	"""
	stream = Process(target=stream_process,
					 args=(loop, queue, file, ),
					 kwargs={ 'speed': speed })
	consume = Process(target=consume_process, args=(loop, consumer, ))
	stream.start()
	consume.start()

	"""
	Wait for the streaming and consumption jobs to finish.
	Then, close the loop and shut down the base manager.
	"""
	stream.join()
	consume.join()

	"""
	Clean up after the consumption.
	"""
	queue_manager.shutdown()

def stream_process(loop, queue, file, *args, **kwargs):
	"""
	Stream the file and add its tweets to the queue.

	Any additional arguments and keyword arguments are passed to the :func:`~twitter.file.simulated_reader.SimulatedFileReader.__init__` constructor.

	:param loop: The main event loop.
	:type loop: :class:`asyncio.unix_events._UnixSelectorEventLoop`
	:param queue: The queue where to add tweets.
	:type queue: :class:`multiprocessing.managers.AutoProxy[Queue]`
	:param file: The path to the file to read.
	:type file: str
	"""

	async def read(reader):
		"""
		Read the file.

		:param reader: The file reader to use.
		:type reader: :class:`twitter.file.reader.FileReader`
		"""

		"""
		When the reading process is interrupted, stop reading tweets.
		"""
		def sigint_handler(signal, frame):
			reader.stop()
			logger.info("Interrupted file reader")

		signal.signal(signal.SIGINT, sigint_handler)

		await reader.read()

	with open(file, 'r') as f:
		reader = SimulatedFileReader(queue, f, *args, **kwargs)
		loop.run_until_complete(read(reader))

def understand_process(comm, loop, consumer):
	"""
	Consume the incoming tweets to understand the event.

	:param comm: The dictionary used by the understanding process to communicate data back to the main loop.
	:type comm: :class:`multiprocessing.managers.DictProxy`
	:param loop: The main event loop.
	:type loop: :class:`asyncio.unix_events._UnixSelectorEventLoop`
	:param consumer: The consumer to use to process tweets.
	:type consumer: :class:`~queues.consumers.consumer.Consumer`
	"""

	async def understand(consumer):
		"""
		Understand the queue's tweets.

		:param consumer: The consumer to use to process tweets.
		:type consumer: :class:`~queues.consumers.consumer.Consumer`
		"""

		"""
		When the consumption process is interrupted, stop consuming tweets.
		"""
		def sigint_handler(signal, frame):
			consumer.stop()
			logger.info("Interrupted understanding")

		signal.signal(signal.SIGINT, sigint_handler)

		return await consumer.understand(max_inactivity=1)

	comm['understanding'] = loop.run_until_complete(asyncio.gather(understand(consumer)))[0]

def consume_process(loop, consumer):
	"""
	Consume the incoming tweets.

	:param loop: The main event loop.
	:type loop: :class:`asyncio.unix_events._UnixSelectorEventLoop`
	:param consumer: The consumer to use to process tweets.
	:type consumer: :class:`~queues.consumers.consumer.Consumer`
	"""

	async def consume(consumer):
		"""
		Consume the queue's tweets.

		:param consumer: The consumer to use to process tweets.
		:type consumer: :class:`~queues.consumers.consumer.Consumer`
		"""

		"""
		When the consumption process is interrupted, stop consuming tweets.
		"""
		def sigint_handler(signal, frame):
			consumer.stop()
			logger.info("Interrupted consumer")

		signal.signal(signal.SIGINT, sigint_handler)

		await consumer.run(max_inactivity=1)

	loop.run_until_complete(consume(consumer))

def consumer(consumer):
	"""
	Convert the given string into a consumer class.
	The accepted consumers are:

		#. :class:`~queues.consumers.eld_consumer.ELDConsumer`,
		#. :class:`~queues.consumers.fire_consumer.FIREConsumer`,
		#. :class:`~queues.consumers.print_consumer.PrintConsumer`,
		#. :class:`~queues.consumers.stat_consumer.StatConsumer`, and
		#. :class:`~queues.consumers.zhao_consumer.ZhaoConsumer`

	:param consumer: The consumer string.
	:type consumer: str

	:return: The class that corresponds to the given consumer.
	:rtype: class

	:raises argparse.ArgumentTypeError: When the given consumer string is invalid.
	"""

	consumers = {
		'eldconsumer': ELDConsumer,
		'fireconsumer': FIREConsumer,
		'printconsumer': PrintConsumer,
		'statconsumer': StatConsumer,
		'zhaoconsumer': ZhaoConsumer,
	}

	if consumer.lower() in consumers:
		return consumers[consumer.lower()]

	raise argparse.ArgumentTypeError(f"Invalid consumer value: {consumer}")

if __name__ == "__main__":
	main()
