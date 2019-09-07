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
	"Zhao": ZhaoConsumer,
}

summarization_algorithms = {
	"Graph": mamo_graph.DocumentGraphSummarizer,
	"FMMR": mamo_mmr.FragmentedMMR,
	"MMR": baseline_mmr.BaselineMMR
}

"""
How long the event should be tracked
"""
EVENT_DURATION = 3600 * 2.5

"""
The length of the time window
"""
TIME_WINDOW = 10

"""
How much of the stream should be skipped
"""
SKIP_TIME = 3600 * 0./6.

"""
The stream's speed
"""
SPEED = 1

if len(sys.argv) < 4:
	logger.error("Parameters: <file name without extension> <TDT: Zhao|baseline> <summarization: FMMR|Graph|baseline>")
	exit()
else:
	NAME, TDT, SUMMARIZATION = sys.argv[1:4]

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
KNOWN_PARTICIPANTS = []

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

def consume_task(loop, consumer, idf):
	"""
	Create the task that consumes the queue
	"""
	loop.run_until_complete(consume_queue(consumer, idf))

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

async def consume_queue(consumer, idf):
	"""
	Consume the queue
	"""
	logger.info("Event tracking starting")
	(timeline, ) = await consumer.run(max_time=EVENT_DURATION, initial_wait=10, max_inactivity=30) # with the ELD consumer

	with open("/mnt/evaluation/tdt/timeline/%s_%s_%s_timeline.json" % (NAME, TDT, SUMMARIZATION), "w") as f:
		for summary in timeline:
			f.write("%s\n" % json.dumps(summary.to_array()))

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

loop = asyncio.get_event_loop() # the event loop

if True and os.path.isfile(EVENT_IDF_FILENAME):
	with open(EVENT_IDF_FILENAME, "r") as f:
		return_dict["idf"] = json.loads(f.readline())
	logger.info("IDF loaded with %d documents" % return_dict["idf"]["DOCUMENTS"])
else:
	logger.error("IDF file not found, baseline cannot create it")
	exit()

consumer = tdt(queue, periodicity=TIME_WINDOW, idf=return_dict["idf"])

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
