"""
The skeleton of the MVP, accelerating the file input.

This skeleton may also be used in the final version.
The main changes all go into the consumer.
"""

from datetime import datetime

from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager

from tweepy import OAuthHandler
from tweepy import Stream

import asyncio
import json
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))

from logger import logger

from queues.consumer.print_consumer import PrintConsumer
from queues.consumer.stat_consumer import StatConsumer
from queues.consumer.eld.baseline_consumer import BaselineConsumer
from queues.consumer.eld.eld_consumer import SimulatedELDConsumer
from queues.consumer.eld.zhao_consumer import ZhaoConsumer
from queues.queue.queue import Queue

from summarization.algorithms.update import baseline_mmr, mamo_graph, mamo_mmr

from twitter import globals
from twitter.twevent.file_listener import StaggeredFileListener
from twitter.twevent.simulated_file_listener import SimulatedFileListener

logger.set_logging_level(logger.LogLevel.INFO)

topic_detection_algorithms = {
	"ELD": SimulatedELDConsumer,
	"baseline": ZhaoConsumer
}

summarization_algorithms = {
	"Graph": mamo_graph.DocumentGraphSummarizer,
	"FMMR": mamo_mmr.FragmentedMMR
}

"""
How long the consumer should spend understanding the event
"""
UNDERSTANDING_DURATION = 3600

"""
How long the event should be tracked
"""
EVENT_DURATION = 3600 * 2.5

"""
The length of the time window
"""
TIME_WINDOW = 30

"""
How much of the stream should be skipped
"""
SKIP_TIME = 3600 * 0./12.

"""
The words that should be filtered out (usually the seed set)
"""
FILTER_WORDS = []

"""
The stream's speed
"""
SPEED = 1

if len(sys.argv) < 4:
	logger.error("Parameters: <file name without extension> <TDT: ELD|baseline> <summarization: FMMR|Graph>")
	exit()
else:
	NAME, TDT, SUMMARIZATION = sys.argv[1:4]

min_size = int(sys.argv[4]) if len(sys.argv) > 4 else 3

tdt = topic_detection_algorithms.get(TDT, None)
summarization = summarization_algorithms.get(SUMMARIZATION, None)
if tdt is None or summarization is None:
	logger.error("Incorrect parameters")
	exit()

logger.info("Name: %s" % NAME)
logger.info("TDT: %s" % tdt.__name__)
logger.info("Summarization: %s" % summarization.__name__)

"""
The name of the file if a file listener is used
"""
FILENAME = "%s.json" % NAME
UNDERSTANDING_FILENAME = "u_%s_APD.json" % (NAME[:NAME.index("_")] if "_" in NAME else NAME)
EVENT_IDF_FILENAME = "/mnt/data/idf/%s" % FILENAME
TIMELINE_FILENAME = "/var/www/html/%s.json" % NAME
IDF = "idf.json"
KNOWN_PARTICIPANTS = []

"""
The keywords to track
"""
KEYWORDS = ["morning"]

"""
Authenticate with Tweepy
"""
auth = OAuthHandler(globals.CONSUMER_KEY, globals.CONSUMER_SECRET)
auth.set_access_token(globals.ACCESS_TOKEN, globals.ACCESS_TOKEN_SECRET)

class QueueManager(BaseManager):
	"""
	A dummy class used to share the queue between processes
	"""
	pass

def understand_task(loop, consumer, return_dict):
	"""
	Create the task that understands the queue
	"""
	(idf, participants, ) = loop.run_until_complete(asyncio.gather(understand_queue(consumer), ))[0]
	return_dict["idf"] = idf
	return_dict["participants"] = participants

def consume_task(loop, consumer, idf):
	"""
	Create the task that consumes the queue
	"""
	loop.run_until_complete(consume_queue(consumer, idf))

def understand_stream_task(loop, queue):
	"""
	Create the task that streams data from Twitter for understanding
	"""
	# loop.run_until_complete(create_stream(UNDERSTANDING_FILENAME, 600, 0, speed=30))
	loop.run_until_complete(create_stream(UNDERSTANDING_FILENAME, UNDERSTANDING_DURATION, 0, speed=60))

def consume_stream_task(loop, queue):
	"""
	Create the task that streams data from Twitter for consumption
	"""
	loop.run_until_complete(create_stream(FILENAME, EVENT_DURATION, SKIP_TIME))

async def create_stream(filename, max_time, skip_time, speed=SPEED):
	"""
	Stream information from Twitter using the given listener
	"""
	with open(os.path.join("/mnt/data/twitter", filename)) as f:
		listener = SimulatedFileListener(queue, f, speed=speed, max_time=max_time/speed, skip_time=skip_time) # skip the first hour
		# listener = StaggeredFileListener(queue, f, skip_time=10, max_time=EVENT_DURATION, lines_per_second=100)
		await listener.read()

async def understand_queue(consumer):
	"""
	Glean an initial understanding of the event.
	"""
	# _, topics = await consumer.run(initial_wait=6, max_inactivity=3) # with the baseline consumer
	with open(os.path.join("/home/memonick/data", IDF), "r") as idf_file:
		general_idf = json.loads(idf_file.readline())
		(idf, participants) = await consumer.understand(understanding_period=UNDERSTANDING_DURATION, general_idf=general_idf, initial_wait=10, max_time=EVENT_DURATION, max_inactivity=10, known_participants=KNOWN_PARTICIPANTS) # with the ELD consumer
		logger.info("Understanding finished")
		return (idf, participants)

async def consume_queue(consumer, idf):
	"""
	Consume the queue
	"""
	logger.info("Event tracking starting")
	(clusters, timeline, ) = await consumer.run(idf, max_time=EVENT_DURATION, initial_wait=10, max_inactivity=10, min_size=min_size, summarization_algorithm=summarization, timeline_filename=TIMELINE_FILENAME) # with the ELD consumer

	# with open("/mnt/evaluation/tdt/raw/%s_%s_%s_%d_raw.json" % (NAME, TDT, SUMMARIZATION, min_size), "w") as f:
	# 	for (breaking_clusters, timestamp) in clusters:
	# 		r = {
	# 			"clusters": [{
	# 				"terms": terms,
	# 				"cluster": cluster.to_array(),
	# 			} for terms, cluster in breaking_clusters],
	# 			"timestamp": timestamp
	# 		}
	# 		f.write("%s\n" % json.dumps(r))
	#
	# with open("/mnt/evaluation/tdt/timeline/%s_%s_%s_%d_timeline.json" % (NAME, TDT, SUMMARIZATION, min_size), "w") as f:
	# 	for summary in timeline:
	# 		f.write("%s\n" % json.dumps(summary.to_array()))

"""
Register the queue with the manager
This allows it to be shared between the two processes
"""
QueueManager.register("Queue", Queue)

"""
Create the manager and start it up
From this manager, also create a queue
The consumer will use this queue
"""
manager = QueueManager()
manager.start()
queue = manager.Queue()
normal_manager = Manager()
return_dict = normal_manager.dict()
# consumer = BaselineConsumer(queue, periodicity=5)
consumer = tdt(queue, time_window=TIME_WINDOW, filter_words=FILTER_WORDS)

loop = asyncio.get_event_loop() # the event loop

if True and os.path.isfile(EVENT_IDF_FILENAME):
	with open(EVENT_IDF_FILENAME, "r") as f:
		return_dict["idf"] = json.loads(f.readline())
	logger.info("IDF loaded with %d documents" % return_dict["idf"]["DOCUMENTS"])
else:
	"""
	Two processes make up the workflow.
	The first part understands the stream.
	"""
	p_stream = Process(target=understand_stream_task, args=(loop, queue, ))
	p_understand = Process(target=understand_task, args=(loop, consumer, return_dict, ))

	"""
	Start the understanding processes
	"""
	p_stream.start()
	logger.info("Stream started with pid %s" % p_stream.pid)
	p_understand.start()
	logger.info("Understanding started with pid %s" % p_understand.pid)

	"""
	And wait for them to finish
	"""
	p_stream.join()
	logger.info("Stream finished")
	p_understand.join()
	logger.info("Consumer finished")

	with open(EVENT_IDF_FILENAME, "w") as f:
		f.write(json.dumps(return_dict["idf"]))

"""
Two processes make up the workflow.
The second part consumes the stream.
"""
queue.dequeue_all()
p_stream = Process(target=consume_stream_task, args=(loop, queue, ))
p_consume = Process(target=consume_task, args=(loop, consumer, return_dict["idf"], ))

"""
Start the consuming processes
"""
p_stream.start()
logger.info("Stream started with pid %s" % p_stream.pid)
p_consume.start()
logger.info("Consuming started with pid %s" % p_consume.pid)

"""
And wait for them to finish
"""
stream_out = p_stream.join()
logger.info("Stream finished")
understand_out = p_consume.join()
logger.info("Consumer finished")

"""
Clean up
"""
loop.close()
manager.shutdown()
