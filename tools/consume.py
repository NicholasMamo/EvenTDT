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

    ./tools/consume.py \\
	-f data/event/event.json \\
	-c PrintConsumer

Accepted arguments:

	- ``-f --file``					*<Required>* The file to consume.
	- ``-c --class``				*<Required>* The consumer to use; supported: `ELDConsumer`, `FIREConsumer`, `PrintConsumer`, `StatConsumer`, `ZhaoConsumer`.
	- ``-u --understanding``		*<Optional>* The understanding file used to understand the event.
	- ``-s --speed``				*<Optional>* The speed at which the file is consumed, defaults to 1.
	- ``--skip``					*<Optional>* The amount of time to skip from the beginning of the file in minutes, defaults to 0.
	- ``--max-inactivity``			*<Optional>* The maximum time in seconds to wait for new tweets to arrive before stopping, defaults to 60 seconds.
	- ``--max-time``				*<Optional>* The maximum time in minutes to spend reading the corpus, indefinite if it is less than 0.
	- ``--no-cache``				*<Optional>* If specified, the cached understanding is not used. The new understanding is cached instead.
	- ``--scheme``					*<Optional>* If specified, the path to the :class:`~nlp.weighting.TermWeightingScheme` to use. If it is not specified, the :class:`~nlp.weighting.tf.TF` scheme is used.
	- ``--min-size``				*<Optional>* The minimum number of tweets in a cluster to consider it as a candidate topic, defaults to 3.
	- ``--threshold``				*<Optional>* The minimum similarity between a tweet and a cluster to add the tweet to the cluster, defaults to 0.5.
	- ``--max-intra-similarity``	*<Optional>* The maximum intra-similarity of documents in a cluster to consider it as a candidate topic, defaults to 0.8.
	- ``--splits``					*<Optional>* The path to a file containing splits for the consumer, splitting the stream into multiple streams based on the tokens. If given, the tool expects a CSV file, where each line represents a split.

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

import tools
from logger import logger
from objects.exportable import Exportable
from nlp.weighting import TermWeightingScheme
from eventdt.queues import Queue
from queues.consumers import *
from queues.consumers.algorithms import *
from twitter.file import SimulatedFileReader

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``					*<Required>* The file to consume.
		- ``-c --class``				*<Required>* The consumer to use; supported: `ELDConsumer`, `FIREConsumer`, `PrintConsumer`, `StatConsumer`, `ZhaoConsumer`.
		- ``-u --understanding``		*<Optional>* The understanding file used to understand the event.
		- ``-s --speed``				*<Optional>* The speed at which the file is consumed, defaults to 1.
		- ``--skip``					*<Optional>* The amount of time to skip from the beginning of the file in minutes, defaults to 0.
		- ``--max-inactivity``			*<Optional>* The maximum time in seconds to wait for new tweets to arrive before stopping, defaults to 60 seconds.
		- ``--max-time``				*<Optional>* The maximum time in minutes to spend reading the corpus, indefinite if it is less than 0.
		- ``--no-cache``				*<Optional>* If specified, the cached understanding is not used. The new understanding is cached instead.
		- ``--scheme``					*<Optional>* If specified, the path to the :class:`~nlp.weighting.TermWeightingScheme` to use. If it is not specified, the :class:`~nlp.weighting.tf.TF` scheme is used. This can be overwritten if there is event understanding.
		- ``--min-size``				*<Optional>* The minimum number of tweets in a cluster to consider it as a candidate topic, defaults to 3.
		- ``--threshold``				*<Optional>* The minimum similarity between a tweet and a cluster to add the tweet to the cluster, defaults to 0.5.
		- ``--max-intra-similarity``	*<Optional>* The maximum intra-similarity of documents in a cluster to consider it as a candidate topic, defaults to 0.8.
		- ``--splits``					*<Optional>* The path to a file containing splits for the consumer, splitting the stream into multiple streams based on the tokens. If given, the tool expects a CSV file, where each line represents a split.

	:return: The command-line arguments.
	:rtype: :class:`argparse.Namespace`
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
	parser.add_argument('--skip', type=int, required=False, default=0,
						help='<Optional> The amount of time to skip from the beginning of the file in minutes, defaults to 0.')
	parser.add_argument('--max-inactivity', type=int, required=False, default=60,
						help='<Optional> The maximum time in seconds to wait for new tweets to arrive before stopping, defaults to 60 seconds.')
	parser.add_argument('--max-time', type=int, required=False, default=-1,
						help='<Optional> The maximum time in minutes to spend reading the corpus, indefinite if it is less than 0.')
	parser.add_argument('--no-cache', action="store_true",
						help='<Optional> If specified, the cached understanding is not used. The new understanding is cached instead.')
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
	parser.add_argument('--splits', type=splits, required=False, default=None,
						help='<Optional> The path to a file containing splits for the consumer, splitting the stream into multiple streams based on the tokens. If given, the tool expects a CSV file, where each line represents a split.')

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
	Get the meta arguments.
	"""
	cmd = tools.meta(args)
	cmd['consumer'] = str(vars(args)['consumer'])
	cmd['scheme'] = str(type(vars(args)['scheme']))

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
		if args['no_cache'] or not tools.cache_exists(args['understanding']):
			logger.info("Starting understanding period")
			understanding = understand(**args)['understanding']
			tools.save(cache, understanding)
			args.update(understanding)
			logger.info("Understanding period ended")
		else:
			args.update(tools.load(cache))

	"""
	Consume the event with the main file.
	"""
	logger.info("Starting event period")
	timeline = consume(**args)
	timeline['meta'] = cmd
	tools.save(os.path.join(dir, '.out', filename), timeline)
	logger.info("Event period ended")

	asyncio.get_event_loop().close()

def understand(understanding, consumer, max_inactivity, scheme=None, *args, **kwargs):
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
	:param max_inactivity: The maximum time, in seconds, to wait for new tweets to arrive before stopping.
	:type max_inactivity: int
	:param scheme: The scheme to use when consuming the file.
	:type scheme: :class:`~nlp.weighting.TermWeightingScheme`

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
	understand = Process(target=understand_process, args=(comm, loop, consumer, max_inactivity, ))
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

def consume(file, consumer, speed, max_inactivity, max_time=-1, skip=0, splits=None,
			scheme=None, min_size=3, threshold=0.5, max_intra_similarity=0.8, *args, **kwargs):
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
	:type consumer: type
	:param speed: The speed with which to read the file.
	:type speed: float
	:param max_inactivity: The maximum time, in seconds, to wait for new tweets to arrive before stopping.
	:type max_inactivity: int
	:param max_time: The maximum time in minutes to spend reading the corpus, indefinite if it is less than 0.
	:type max_time: int
	:param skip: The amount of time to skip from the beginning of the file in minutes, defaults to 0.
	:type skip: int
	:param splits: A list of splits for the consumer.
				   If they are given, the function uses a :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer`.
	:type splits: list of list of str
	:param scheme: The scheme to use when consuming the file.
	:type scheme: :class:`~nlp.weighting.TermWeightingScheme`
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
	consumer = create_consumer(consumer, queue, scheme=scheme,
							   min_size=min_size, threshold=threshold,
							   max_intra_similarity=max_intra_similarity)

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
					 kwargs={ 'speed': speed, 'skip_time': skip * 60,
					 		  'max_time': (max_time * 60 if max_time >= 0 else max_time) })
	consume = Process(target=consume_process, args=(comm, loop, consumer, max_inactivity, ))
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

def stream_process(loop, queue, file, skip_time=0, speed=1, max_time=-1, *args, **kwargs):
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
	:param max_time: The maximum time in minutes to spend reading the corpus, indefinite if it is less than 0.
	:type max_time: int
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
		reader = SimulatedFileReader(queue, f, skip_time=skip_time, speed=speed, max_time=max_time)
		loop.run_until_complete(read(reader))

	logger.info("Streaming ended")

def understand_process(comm, loop, consumer, max_inactivity):
	"""
	Consume the incoming tweets to understand the event.

	:param comm: The dictionary used by the understanding process to communicate data back to the main loop.
	:type comm: :class:`multiprocessing.managers.DictProxy`
	:param loop: The main event loop.
	:type loop: :class:`asyncio.unix_events._UnixSelectorEventLoop`
	:param consumer: The consumer to use to process tweets.
	:type consumer: :class:`~queues.consumers.consumer.Consumer`
	:param max_inactivity: The maximum time, in seconds, to wait for new tweets to arrive before stopping.
	:type max_inactivity: int
	"""

	async def understand(consumer, max_inactivity):
		"""
		Understand the queue's tweets.

		:param consumer: The consumer to use to process tweets.
		:type consumer: :class:`~queues.consumers.consumer.Consumer`
		:param max_inactivity: The maximum time, in seconds, to wait for new tweets to arrive before stopping.
		:type max_inactivity: int
		"""

		"""
		When the consumption process is interrupted, stop consuming tweets.
		"""
		def sigint_handler(signal, frame):
			consumer.stop()
			logger.info("Interrupted understanding")

		signal.signal(signal.SIGINT, sigint_handler)

		return await consumer.understand(max_inactivity=max_inactivity)

	comm['understanding'] = loop.run_until_complete(asyncio.gather(understand(consumer, max_inactivity)))[0]
	logger.info("Understanding ended")

def consume_process(comm, loop, consumer, max_inactivity):
	"""
	Consume the incoming tweets.

	:param comm: The dictionary used by the consumption process to communicate data back to the main loop.
	:type comm: :class:`multiprocessing.managers.DictProxy`
	:param loop: The main event loop.
	:type loop: :class:`asyncio.unix_events._UnixSelectorEventLoop`
	:param consumer: The consumer to use to process tweets.
	:type consumer: :class:`~queues.consumers.consumer.Consumer`
	:param max_inactivity: The maximum time, in seconds, to wait for new tweets to arrive before stopping.
	:type max_inactivity: int
	"""

	async def consume(consumer, max_inactivity):
		"""
		Consume the queue's tweets.

		:param consumer: The consumer to use to process tweets.
		:type consumer: :class:`~queues.consumers.consumer.Consumer`
		:param max_inactivity: The maximum time, in seconds, to wait for new tweets to arrive before stopping.
		:type max_inactivity: int
		"""

		"""
		When the consumption process is interrupted, stop consuming tweets.
		"""
		def sigint_handler(signal, frame):
			consumer.stop()
			logger.info("Interrupted consumer")

		signal.signal(signal.SIGINT, sigint_handler)

		return await consumer.run(max_inactivity=max_inactivity)

	comm['timeline'] = loop.run_until_complete(consume(consumer, max_inactivity))
	logger.info("Consumption ended")

def create_consumer(consumer, queue, splits=None, scheme=None, min_size=3, threshold=0.5, max_intra_similarity=0.8):
	"""
	Create a consumer.
	If splits are given, the function creates a :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer`.

	:param consumer: The type of consumer to use.
	:type consumer: type
	:param splits: A list of splits for the consumer.
				   If they are given, the function uses a :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer`.
	:type splits: list of list of str
	:param queue: The queue that will receive tweets for consumption.
	:type queue: :class:`~queues.Queue`
	:param scheme: The scheme to use when consuming the file.
	:type scheme: None or :class:`~nlp.weighting.TermWeightingScheme`
	:param min_size: The minimum number of tweets in a cluster to consider it as a candidate topic, defaults to 3.
	:type min_size: int
	:param threshold: The minimum similarity between a tweet and a cluster to add the tweet to the cluster, defaults to 0.5.
	:type threshold: float
	:param max_intra_similarity: The maximum intra-similarity of documents in a cluster to consider it as a candidate topic, defaults to 0.8.
	:type max_intra_similarity: float

	:return: A consumer with the given parameters.
	:rtype: :class:`~queues.consumers.Consumer`
	"""

	if consumer is ELDConsumer:
		return consumer(queue, scheme=scheme, min_size=min_size, threshold=threshold,
						max_intra_similarity=max_intra_similarity)
	elif consumer is FIREConsumer:
		return consumer(queue, scheme=scheme, min_size=min_size, threshold=threshold)

	return consumer(queue)

def consumer(consumer):
	"""
	Convert the given string into a consumer class.
	The accepted consumers are:

		#. :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`,
		#. :class:`~queues.consumers.algorithms.fire_consumer.FIREConsumer`,
		#. :class:`~queues.consumers.print_consumer.PrintConsumer`,
		#. :class:`~queues.consumers.stat_consumer.StatConsumer`, and
		#. :class:`~queues.consumers.algorithms.zhao_consumer.ZhaoConsumer`

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
	:rtype: :class:`~nlp.weighting.TermWeightingScheme`
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

def splits(file):
	"""
	Load the splits from the given file.

	:param file: The path to the splits file.
				 This function expects a CSV file.
	:type file: str

	:return: A list of splits.
	:rtype: list of str
	"""

	splits = [ ]

	with open(file) as f:
		for line in f:
			tokens = line.split(',')
			tokens = [ token.strip() for token in tokens ]
			splits.append(tokens)

	return splits

if __name__ == "__main__":
	main()
