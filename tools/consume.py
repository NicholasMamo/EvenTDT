#!/usr/bin/env python3

"""
The consumer receives an input file and consumes it with one of the given consumers.
This consumer is split into two asynchronous tasks.
The first task reads the file, and the second consumes it.

The dataset files are expected to contain one tweet on every line, encoded as JSON strings.

To run the script, use:

.. code-block:: bash

    ./implementation/consume.py \\
		-f data/event/event.json

Accepted arguments:

	- ``-f --file``			*<Required>* The file to consume.

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

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Consume a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-f', '--file', nargs=1, type=str, required=True,
						help='<Required> The file to consume.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	print(args.file)

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
