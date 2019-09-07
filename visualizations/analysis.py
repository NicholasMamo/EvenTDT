"""
Functions used to analyze events, and subsequently help in the creation of visualizations.
"""

import datetime
import json
import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, "../libraries")
if path not in sys.path:
	sys.path.append(path)

from logger import logger

from queues.consumer.eld.eld_consumer import ELDConsumer
from queues.queue.queue import Queue

from vector.vector import Vector
from vector import vector_math

def count_tweets(*args, **kwargs):
	"""
	Count the number of tweets in each time window.

	:return: The number of documents in each time window, separated using the timestamp.
	:rtype: dict
	"""

	bin_data = aggregate_tweets(bin_function=count, *args, **kwargs)
	return bin_data

def calculate_nutrition(*args, **kwargs):
	"""
	Calculate the nutrition sets.

	:return: The nutrition for each encountered keyword separated by time windows.
	:rtype: dict
	"""

	bin_data = aggregate_tweets(bin_function=concatenate, *args, **kwargs)
	bin_data = { timestamp: vector_math.augmented_normalize(document, a=0).get_dimensions()
		for timestamp, document in bin_data.items() }
	return bin_data

def aggregate(store, time_window, data):
	"""
	Aggregate the data.

	:param store: The data store that needs to be updated.
		The keys are the time windows, and the values are the documents.
	:type store: dict
	:param time_window: The time window to which the new data belongs.
	:type time_window: int
	:param data: The new bin data.
	:type data: mixed

	:return: The updated store.
	:rtype: dict
	"""

	store[time_window] = store[time_window] if time_window in store else []
	store.get(time_window, []).extend(data)
	return store

def count(store, time_window, data):
	"""
	Count the data.

	:param store: The data store that needs to be updated.
		The keys are the time windows, and the values are the documents.
	:type store: dict
	:param time_window: The time window to which the new data belongs.
	:type time_window: int
	:param data: The new bin data.
	:type data: mixed

	:return: The updated store.
	:rtype: dict
	"""

	store[time_window] = store.get(time_window, 0) + len(data)
	return store

def concatenate(store, time_window, data):
	"""
	Concatenate all the documents.

	:param store: The data store that needs to be updated.
		The keys are the time windows, and the values are the documents.
	:type store: dict
	:param time_window: The time window to which the new data belongs.
	:type time_window: int
	:param data: The new bin data.
	:type data: mixed

	:return: The updated store.
	:rtype: dict
	"""

	consumer = ELDConsumer(Queue(), 60) # create a consumer that is used to simulate normal operation.
	data = consumer._tokenize(data)

	store[time_window] = vector_math.concatenate([store.get(time_window, Vector())] + data)
	return store

def aggregate_tweets(f, bin_size=-1, bin_function=aggregate, max_bins=-1, skip_bins=-1, track=None):
	"""
	Aggregate the documents.

	:param f: The file handle containing the data.
	:type f: file
	:param bin_size: The length (in seconds) of each time window.
		If a negative number is provided, everything is lumped into a single key.
	:type bin_size: int
	:param max_bins: The number of bins to include.
		If a negative number is provided, the entire event is covered.
	:type max_bins: int
	:param skip_bins: The number of bins to skip.
		If a negative number is provided, no bins are skipped.
	:type skip_bins: int
	:param track: The keyword to track.
		If it is not None, only documents mentioning the keyword are counted.
	:type track: str

	:return: The documents in each time window, separated using the timestamp.
	:rtype: dict
	"""

	bin_data = {}

	f.seek(0) # reset the file pointer

	consumer = ELDConsumer(Queue(), 60) # create a consumer that is used to simulate normal operation.

	"""
	If a track keyword is provided, tokenize it.
	"""
	if track is not None:
		track = list(consumer._tokenize([{"text": track, "timestamp_ms": 0}])[0].get_dimensions().keys())[0]


	"""
	Skip the initial tweets.
	"""
	start = None
	if skip_bins > 0:
		for line in f:
			tweet = json.loads(line)
			timestamp_ms = int(tweet["timestamp_ms"]) - int(tweet["timestamp_ms"]) % 1000
			timestamp = int(timestamp_ms / 1000)
			time_window = timestamp - timestamp % bin_size if bin_size > 0 else 0
			start = time_window if start is None else start

			if (time_window - start) / bin_size >= skip_bins:
				logger.info("Reading from time window at %s" % datetime.datetime.utcfromtimestamp(time_window).strftime("%H:%M:%S"))
				break

	"""
	Go through each line to count the documents.
	"""
	bin = [] # the tweets from the current bin
	current_time_window = None # the time window being added up right now
	for line in f:
		tweet = json.loads(line)

		"""
		Find the time window of the document.
		"""
		timestamp_ms = int(tweet["timestamp_ms"]) - int(tweet["timestamp_ms"]) % 1000
		timestamp = int(timestamp_ms / 1000)
		time_window = timestamp - timestamp % bin_size + bin_size if bin_size > 0 else 0
		if current_time_window is None:
			current_time_window = time_window
			logger.info("First time window at %s" % datetime.datetime.utcfromtimestamp(current_time_window).strftime("%H:%M:%S"))

		if time_window > current_time_window:
			"""
			If the time window is over, process the tweets.
			Stop counting if the desired number of bins have been reached.
			"""

			if max_bins > 0 and len(bin_data) > max_bins:
				break

			"""
			Document counts depend on whether a track keyword was provided.
			If one was indeed provided, it is sought in the tokenized documents.
			"""
			if track is not None:
				tokenized_documents = consumer._tokenize(bin)
				bin = [ document for document in tokenized_documents if track.lower() in document.get_dimensions() ]

			bin_data = bin_function(bin_data, current_time_window, bin)

			"""
			Finally, reset the records.
			"""
			bin = []
			current_time_window = time_window

		bin.append(tweet)

	"""
	Finalize the aggregation with any last tweets that have not been committed.
	"""
	if track is not None:
		tokenized_documents = consumer._tokenize(bin)
		bin = [ document for document in tokenized_documents if track.lower() in document.get_dimensions() ]

	bin_data = bin_function(bin_data, current_time_window, bin)

	logger.info("Last time window at %s" % datetime.datetime.utcfromtimestamp(current_time_window).strftime("%H:%M:%S"))

	return bin_data

def aggregate_documents(f, bin_size=-1, filter=True, *args, **kwargs):
	"""
	Based on the tweet aggregation.
	However, this returns :class:`vector.nlp.document.Document` instances.

	:param f: The file handle containing the data.
	:type f: file
	:param bin_size: The length (in seconds) of each time window.
		If a negative number is provided, everything is lumped into a single key.
	:type bin_size: int
	:param filter: A boolean indicating whether documents should be filtered.
	:type filter: bool

	:return: The documents in each time window, separated using the timestamp, as proper documents.
	:rtype: dict
	"""

	consumer = ELDConsumer(Queue(), 60) # create a consumer that is used to simulate normal operation.

	bin_data = aggregate_tweets(f, bin_size, *args, **kwargs)

	if filter:
		bin_data = { timestamp: consumer._filter_tweets(tweets)
			for timestamp, tweets in bin_data.items() }

	bin_data = { timestamp: consumer._tokenize(tweets)
		for timestamp, tweets in bin_data.items() }
	return bin_data
