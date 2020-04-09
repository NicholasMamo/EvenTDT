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

	- ``-f --file``					*<Required>* The file to consume.
	- ``-c --class``				*<Required>* The consumer to use; supported: `ELDConsumer`, `FIREConsumer`, `PrintConsumer`, `StatConsumer`, `ZhaoConsumer`.
	- ``-u --understanding``		*<Optional>* The understanding file used to understand the event.
	- ``-s --speed``				*<Optional>* The speed at which the file is consumed, defaults to 1.
	- ``--skip``					*<Optional>* The amount of time to skip from the beginning of the file in minutes, defaults to 0.
	- ``--no-cache``				*<Optional>* If specified, the cached understanding is not used. The new understanding is cached instead.
	- ``--scheme``					*<Optional>* If specified, the path to the :class:`~nlp.term_weighting.scheme.TermWeightingScheme` to use. If it is not specified, the :class:`~nlp.term_weighting.scheme.TF` scheme is used.
	- ``--min-size``				*<Optional>* The minimum number of tweets in a cluster to consider it as a candidate topic, defaults to 3.
	- ``--threshold``				*<Optional>* The minimum similarity between a tweet and a cluster to add the tweet to the cluster, defaults to 0.5.
	- ``--max-intra-similarity``	*<Optional>* The maximum intra-similarity of documents in a cluster to consider it as a candidate topic, defaults to 0.8.

"""

import argparse
import asyncio
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
from nlp.term_weighting.scheme import TermWeightingScheme
from queues import Queue
from queues.consumers import *
from twitter.file import SimulatedFileReader

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``					*<Required>* The file to consume.
		- ``-c --class``				*<Required>* The consumer to use; supported: `ELDConsumer`, `FIREConsumer`, `PrintConsumer`, `StatConsumer`, `ZhaoConsumer`.
		- ``-u --understanding``		*<Optional>* The understanding file used to understand the event.
		- ``-s --speed``				*<Optional>* The speed at which the file is consumed, defaults to 1.
		- ``--no-cache``				*<Optional>* If specified, the cached understanding is not used. The new understanding is cached instead.
		- ``--skip``					*<Optional>* The amount of time to skip from the beginning of the file in minutes, defaults to 0.
		- ``--scheme``					*<Optional>* If specified, the path to the :class:`~nlp.term_weighting.scheme.TermWeightingScheme` to use. If it is not specified, the :class:`~nlp.term_weighting.scheme.TF` scheme is used. This can be overwritten if there is event understanding.
		- ``--min-size``				*<Optional>* The minimum number of tweets in a cluster to consider it as a candidate topic, defaults to 3.
		- ``--threshold``				*<Optional>* The minimum similarity between a tweet and a cluster to add the tweet to the cluster, defaults to 0.5.
		- ``--max-intra-similarity``	*<Optional>* The maximum intra-similarity of documents in a cluster to consider it as a candidate topic, defaults to 0.8.

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
	parser.add_argument('--skip', type=int, required=False, default=0,
						help='<Optional> The amount of time to skip from the beginning of the file in minutes, defaults to 0.')
	parser.add_argument('--scheme', type=scheme, required=False, default=None,
						help="""<Optional> If specified, the path to the term-weighting scheme file.
								If it is not specified, the term frequency scheme is used instead.
								This can be overwritten if there is event understanding.""")
	parser.add_argument('--min-size', type=int, required=False, default=3,
						help='<Optional> The minimum number of tweets in a cluster to consider it as a candidate topic, defaults to 3.')
	parser.add_argument('--threshold', type=float, required=False, default=0.5,
						help='<Optional> The minimum similarity between a tweet and a cluster to add the tweet to the cluster, defaults to 0.5.')
	parser.add_argument('--max-intra-similarity', type=float, required=False, default=0.8,
						help='<Optional> The maximum intra-similarity of documents in a cluster to consider it as a candidate topic, defaults to 0.8.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
	dir = os.path.dirname(args.file)
	filename = os.path.basename(args.file)

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
		cache = os.path.join(dir, '.cache', os.path.basename(args['understanding']))
		if args['no_cache'] or not cache_exists(args['understanding']):
			logger.info("Starting understanding period")
			understanding = understand(**args)['understanding']
			save(cache, understanding)
			args.update(understanding)
			logger.info("Understanding period ended")
		else:
			args.update(load(cache))

	"""
	Consume the event with the main file.
	"""
	logger.info("Starting event period")
	timeline = consume(**args)
	save(os.path.join(dir, '.out', filename), timeline)
	logger.info("Event period ended")

	asyncio.get_event_loop().close()

def understand(understanding, consumer, scheme=None, *args, **kwargs):
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
	:param scheme: The scheme to use when consuming the file.
	:type scheme: :class:`~nlp.term_weighting.scheme.TermWeightingScheme`

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
	consumer = consumer(queue, scheme=scheme)

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

def consume(file, consumer, speed, scheme=None, skip=0,
			min_size=3, threshold=0.5, max_intra_similarity=0.8, *args, **kwargs):
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
	:param scheme: The scheme to use when consuming the file.
	:type scheme: :class:`~nlp.term_weighting.scheme.TermWeightingScheme`
	:param skip: The amount of time to skip from the beginning of the file in minutes, defaults to 0.
	:type skip: int
	:param min_size: The minimum number of tweets in a cluster to consider it as a candidate topic, defaults to 3.
	:type min_size: int
	:param threshold: The minimum similarity between a tweet and a cluster to add the tweet to the cluster, defaults to 0.5.
	:type threshold: float
	:param max_intra_similarity: The maximum intra-similarity of documents in a cluster to consider it as a candidate topic, defaults to 0.8.
	:type max_intra_similarity: float

	:return: A dictionary containing the timeline.
	:rtype: dict
	"""

	loop = asyncio.get_event_loop()

	"""
	Create a queue that will be shared between the streaming and understanding processes.
	"""
	queue_manager = BaseManager()
	queue_manager.start()
	queue = queue_manager.Queue()
	consumer = consumer(queue, scheme=scheme,
						min_size=min_size, threshold=threshold, max_intra_similarity=max_intra_similarity)

	"""
	Create a shared dictionary that processes can use to communicate with this function.
	"""
	manager = Manager()
	comm = manager.dict()

	"""
	Create and start the streaming and consumption processes.
	"""
	stream = Process(target=stream_process,
					 args=(loop, queue, file, ),
					 kwargs={ 'speed': speed, 'skip_time': skip * 60 })
	consume = Process(target=consume_process, args=(comm, loop, consumer, ))
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
	timeline = dict(comm)
	manager.shutdown()
	queue_manager.shutdown()

	return timeline

def stream_process(loop, queue, file, skip_time=0, speed=1, *args, **kwargs):
	"""
	Stream the file and add its tweets to the queue.

	:param loop: The main event loop.
	:type loop: :class:`asyncio.unix_events._UnixSelectorEventLoop`
	:param queue: The queue where to add tweets.
	:type queue: :class:`multiprocessing.managers.AutoProxy[Queue]`
	:param file: The path to the file to read.
	:type file: str
	:param skip_time: The amount of time to skip from the beginning of the file in minutes, defaults to 0.
	:type skip_time: int
	:param speed: The speed at which the file is consumed, defaults to 1.
	:type speed: float
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
		reader = SimulatedFileReader(queue, f, skip_time=skip_time, speed=speed)
		loop.run_until_complete(read(reader))

	logger.info("Streaming ended")

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

		return await consumer.understand(max_inactivity=60)

	comm['understanding'] = loop.run_until_complete(asyncio.gather(understand(consumer)))[0]
	logger.info("Understanding ended")

def consume_process(comm, loop, consumer):
	"""
	Consume the incoming tweets.

	:param comm: The dictionary used by the consumption process to communicate data back to the main loop.
	:type comm: :class:`multiprocessing.managers.DictProxy`
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

		return await consumer.run(max_inactivity=60)

	comm['timeline'] = loop.run_until_complete(consume(consumer))[0]
	logger.info("Consumption ended")

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

def save(file, data):
	"""
	Save the data to the given file.
	The function saves the data as a JSON file.

	:param file: The path to the file where to save the data.
	:type file: str
	:param data: The data to save.
				  The function expects a dictionary that can be JSON serializable.
				  The function tries to convert the values that cannot be serialized to arrays.
				  Only classes that inherit the :class:`~objects.exportable.Exportable` can be converted to arrays.
				  This is done through the :func:`~objects.exportable.Exportable.to_array` function.
	:type data: dict
	"""

	"""
	Create the directory if it doesn't exist.
	"""
	dir = os.path.dirname(file)
	if not os.path.exists(dir):
		os.mkdir(dir)

	"""
	Encode the data and save it.
	"""
	data = Exportable.encode(data)
	with open(file, 'w') as f:
		f.write(json.dumps(data))

def load(file):
	"""
	Load the data from the given file.

	:param file: The path to the file from where to load the data.
	:type file: str

	:return: A new dictionary with the loaded data.
	:rtype: dict
	"""

	"""
	Read the data as a JSON string.
	Then, decode the data and return it.
	"""
	with open(file, 'r') as f:
		line = f.readline()
		data = json.loads(line)

	return Exportable.decode(data)

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

def scheme(file):
	"""
	Load the term-weighting scheme from the given file.

	:param file: The path to the term-weighting scheme.
	:type file: str

	:return: The term-weighting scheme in the given file.
	:rtype: :class:`~nlp.term_weighting.scheme.TermWeightingScheme`
	"""

	"""
	Read the data as a JSON string.
	Then, decode it and return it.
	"""
	with open(file, 'r') as f:
		line = f.readline()
		data = json.loads(line)

	scheme = Exportable.decode(data)
	if type(scheme) is dict:
		for key in scheme:
			if isinstance(scheme.get(key), TermWeightingScheme):
				return scheme.get(key)

if __name__ == "__main__":
	main()
