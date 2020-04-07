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

from multiprocessing import Process
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

	parser.add_argument('-f', '--file', nargs=1, type=str, required=True,
						help='<Required> The file to consume.')
	parser.add_argument('-c', '--consumer', nargs=1, type=consumer, required=True,
						help='<Required> The consumer to use.')
	parser.add_argument('-u', '--understanding', nargs=1, type=str, required=False,
						help='<Optional> The understanding file used to understand the event.')
	parser.add_argument('-s', '--speed', nargs=1, type=float, required=False, default=1,
						help='<Optional> The understanding file used to understand the event.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()

	"""
	Register and create a shared queue.
	"""
	BaseManager.register("Queue", Queue)
	manager = BaseManager()
	manager.start()
	queue = manager.Queue()

	"""
	Create a consumer with the shared queue.
	Then, create two processes.
	Both processes share the event loop and queue.
	"""
	consumer = args.consumer[0](queue)
	loop = asyncio.get_event_loop()
	stream = Process(target=stream_process, args=(loop, queue, args.file[0], ))
	consume = Process(target=consume_process, args=(loop, consumer, ))
	stream.start()
	consume.start()

	"""
	When the consumption tool is interrupted, show a prompt with information.
	"""
	def sigint_handler(signal, frame):
		logger.info("Waiting for reading and consumption processes to end")

	signal.signal(signal.SIGINT, sigint_handler)

	"""
	Wait for the streaming and consumption jobs to finish.
	Then, close the loop and shut down the base manager.
	"""
	stream.join()
	consume.join()
	loop.close()
	manager.shutdown()

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

def consume_process(loop, consumer):
	"""
	Consume the incoming tweets.

	:param loop: The main event loop.
	:type loop: :class:`asyncio.unix_events._UnixSelectorEventLoop`
	:param consumer: The consumer to use to process tweets.
	:type consumer: :class:`queues.consumers.consumer.Consumer`
	"""

	async def consume(consumer):
		"""
		Consume the queue's tweets.

		:param consumer: The consumer to use to process tweets.
		:type consumer: :class:`queues.consumers.consumer.Consumer`
		"""

		"""
		When the consumption process is interrupted, stop consuming tweets.
		"""
		def sigint_handler(signal, frame):
			consumer.stop()
			logger.info("Interrupted consumer")

		signal.signal(signal.SIGINT, sigint_handler)

		await consumer.run()

	loop.run_until_complete(consume(consumer))

def consumer(consumer):
	"""
	Convert the given string into a consumer class.
	The accepted consumers are:

		#. :class:`~queues.consumers.print_consumer.PrintConsumer`

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
