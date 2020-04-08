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
	- ``--no-cache``			*<Optional>* If specified, the cached understanding is not used. The new understanding is cached instead.

"""

import argparse
import asyncio
import copy
import importlib
import json
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
from objects.exportable import Exportable
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
		- ``--no-cache``			*<Optional>* If specified, the cached understanding is not used. The new understanding is cached instead.

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
	parser.add_argument('--no-cache', action="store_true",
						help='<Optional> If specified, the cached understanding is not used. The new understanding is cached instead.')

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

	Priority is given to cached understanding.
	The only exception is when cache is explictly disabled or there is no cache.
	"""
	args = vars(args)
	if args['understanding']:
		if args['no_cache'] or not cache_exists(args['understanding']):
			logger.info("Starting understanding period")
			understanding = understand(**args)['understanding']
			cache(args['understanding'], understanding)
			args['understanding'] = understanding
			logger.info("Understanding period ended")
		else:
			args.update(load_cache(args['understanding']))

	"""
	Consume the event with the main file.
	"""
	logger.info("Starting event period")
	consume(**args)
	logger.info("Event period ended")

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

def cache_exists(file, cache_dir='.cache'):
	"""
	Check whether cache exists for the given file.
	The cache exists in a cache directory and has the same name as the given file.

	:param file: The path to the file whose cache will be sought.
	:type file: str
	:param cache_dir: The directory where cache is stored.
					  This is relative to the file's directory.
	:type cache: str

	:return: A boolean indicating whether cache exists for the given file.
	:rtype: bool
	"""

	dir = os.path.dirname(file)
	filename = os.path.basename(file)
	cache_dir = os.path.join(dir, cache_dir)
	if os.path.exists(cache_dir) and os.path.isdir(cache_dir):
		cache_file = os.path.join(cache_dir, filename)
		return os.path.exists(cache_file) and os.path.isfile(cache_file)

	return False

def cache(file, data, cache_dir='.cache'):
	"""
	Cache the given data to the given file.
	The cache exists in a cache directory and has the same name as the given file.
	The function saves cache as a JSON file.

	:param file: The path to the file containing the inital understanding data.
				 Its name will be used to save the cache the understanding with the same name.
	:type file: str
	:param data: The data to cache.
				  The function expects a dictionary that can be JSON serializable.
				  The function tries to convert the values that cannot be serialized to arrays.
				  Only classes that inherit the :class:`~objects.exportable.Exportable` can be converted to arrays.
				  This is done through the :func:`~objects.exportable.Exportable.to_array` function.
	:type data: dict
	:param cache_dir: The directory where cache is stored.
					  This is relative to the file's directory.
	:type cache_dir: str
	"""

	dir = os.path.dirname(file)
	filename = os.path.basename(file)

	"""
	Create the cache directory if it doesn't exist.
	"""
	cache_dir = os.path.join(dir, cache_dir)
	if not os.path.exists(cache_dir):
		os.path.mkdir(cache_dir)

	"""
	Encode the data and save it.
	"""
	data = copy.deepcopy(data)
	encode(data)
	cache_file = os.path.join(cache_dir, filename)
	with open(cache_file, 'w') as f:
		f.write(json.dumps(data))

def encode(data):
	"""
	Try to encode the given data.
	This function expects a dictionary and checks if values are JSON serializable.
	If this is not possible, instances of :class:`~objects.exportable.Exportable` are converted to arrays.
	This is done through the :func:`~objects.exportable.Exportable.to_array` function.

	:param data: The data to encode.
	:type data: dict

	:return: The encoded data.
	:rtype dict:
	"""

	"""
	Go over the cache and see if the values are serializable.
	"""
	for key in data:
		try:
			data[key] = json.loads(json.dumps(data.get(key)))
		except TypeError:
			if type(data[key]) is dict:
				encode(data.get(key))
			else:
				data[key] = data.get(key).to_array()

def load_cache(file, cache_dir='.cache'):
	"""
	Cache the given data to the given file.
	The cache exists in a cache directory and has the same name as the given file.
	The function saves cache as a JSON file.

	:param file: The path to the file containing the inital understanding data.
				 Its name will be used to save the cache the understanding with the same name.
	:type file: str
	:param cache_dir: The directory where cache is stored.
					  This is relative to the file's directory.
	:type cache_dir: str

	:return: A new dictionary with the understanding.
	:rtype: dict
	"""

	dir = os.path.dirname(file)
	filename = os.path.basename(file)

	"""
	Read the data as a JSON string.
	"""
	cache_dir = os.path.join(dir, cache_dir)
	cache_file = os.path.join(cache_dir, filename)
	with open(cache_file, 'r') as f:
		line = f.readline()
		data = json.loads(line)

	return decode(data)

def decode(data):
	"""
	A function that recursively decodes cached data.
	By decoded, it means that objects are created where necessary or possible.
	Only classes that inherit the :class:`~objects.exportable.Exportable` can be decoded.
	This is done through the :func:`~objects.exportable.Exportable.from_array` function.

	:param data: The data to decode.
	:type data: dict

	:return: A dictionary, but this time decoded.
	:rtype: dict
	"""

	data = copy.deepcopy(data)
	for key in data:
		if 'class' in data.get(key):
			module = importlib.import_module(Exportable.get_module(data.get(key).get('class')))
			cls = getattr(module, Exportable.get_class(data.get(key).get('class')))
			data[key] = cls.from_array(data.get(key))
		elif type(data.get(key)) is dict:
			data[key] = decode(data.get(key))

	return data

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
