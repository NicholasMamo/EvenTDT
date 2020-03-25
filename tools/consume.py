#!/usr/bin/env python3

"""
The consumer receives an input file and consumes it with one of the given consumers.
This consumer is split into two asynchronous tasks.
The first task reads the file, and the second consumes it.

The dataset files are expected to contain one tweet on every line, encoded as JSON strings.

To run the script, use:

.. code-block:: bash

    ./implementation/consume.py \\
	-f data/event/event.json \\
	-c PrintConsumer

Accepted arguments:

	- ``-f --file``			*<Required>* The file to consume.
	- ``-c --class``		*<Required>* The consumer to use; supported: `PrintConsumer`.

"""

import argparse
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from queues.consumers import PrintConsumer

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``			*<Required>* The file to consume.
		- ``-c --class``		*<Required>* The consumer to use; supported: `PrintConsumer`.

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

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	print(args.file)
	print(args.consumer)

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
		'printconsumer': PrintConsumer
	}

	if consumer.lower() in consumers:
		return consumers[consumer.lower()]

	raise argparse.ArgumentTypeError(f"Invalid consumer value: {consumer}")

if __name__ == "__main__":
	main()
