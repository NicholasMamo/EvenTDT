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
from queues.queue.queue import Queue

from twitter import globals
from twitter.twevent.file_listener import StaggeredFileListener
from twitter.twevent.simulated_file_listener import SimulatedFileListener

logger.set_logging_level(logger.LogLevel.INFO)

"""
How long the consumer should spend understanding the event
"""
# UNDERSTANDING_DURATION = 3600 - 600 # used when the understanding period is part of the file
UNDERSTANDING_DURATION = 0 # used when the understanding period is in a file of its own

"""
How long the event should be tracked
"""
EVENT_DURATION = 3600*2.5

"""
The length of the time window
"""
TIME_WINDOW = 20

"""
How much of the stream should be skipped
"""
# SKIP_TIME = 900
SKIP_TIME = 0

"""
The words that should be filtered out (usually the seed set)
"""
# FILTER_WORDS = ["brabel", "belbra", "bel", "bra"]
# FILTER_WORDS = ["beleng", "engbel", "bel", "eng"]
# FILTER_WORDS = ["fracro", "crofra", "fra", "cro"]
# FILTER_WORDS = ["#CommunityShield", "crofra", "fra", "cro"]
# FILTER_WORDS = ["communityshield", "cfc", "mcfc", "chemci", "mciche", "community", "shield", "manchester", "city", "chelsea"]
# FILTER_WORDS = ["communityshield", "cfc", "mcfc", "chemci", "mciche"]
# FILTER_WORDS = ["muntot", "totmun", "mun", "tot", "coy", "live", "stream", "link", "manu", "ginobili", "spur", "antonio"]
# FILTER_WORDS = ["munwol", "wolmun", "mun", "wol"]
# FILTER_WORDS = ["whuche", "chewhu", "whu", "che"]
# FILTER_WORDS = ["arseve", "evears", "ars", "eve"]
FILTER_WORDS = ["whumun", "munwhu", "whu", "mun"]

"""
The stream's speed
"""
SPEED = 4

"""
The name of the file if a file listener is used
"""
FILENAME = "WHUMUN.json"
IDF = "idf.json"

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
	loop.run_until_complete(create_stream(UNDERSTANDING_DURATION, SKIP_TIME))

def consume_stream_task(loop, queue):
	"""
	Create the task that streams data from Twitter for consumption
	"""
	loop.run_until_complete(create_stream(EVENT_DURATION, SKIP_TIME + UNDERSTANDING_DURATION))

async def create_stream(max_time, skip_time):
	"""
	Stream information from Twitter using the given listener
	"""
	with open(os.path.join("/mnt/data/twitter", FILENAME)) as f:
		listener = SimulatedFileListener(queue, f, speed=SPEED, max_time=max_time/SPEED, skip_time=skip_time) # skip the first hour
		# listener = StaggeredFileListener(queue, f, skip_time=10, max_time=EVENT_DURATION, lines_per_second=100)
		await listener.read()

async def understand_queue(consumer):
	"""
	Glean an initial understanding of the event.
	"""
	# _, topics = await consumer.run(initial_wait=6, max_inactivity=3) # with the baseline consumer
	with open(os.path.join("/home/memonick/data", IDF), "r") as idf_file:
		general_idf = json.loads(idf_file.readline())
		(idf, participants) = await consumer.understand(understanding_period=UNDERSTANDING_DURATION, general_idf=general_idf, initial_wait=10, max_time=EVENT_DURATION, max_inactivity=10) # with the ELD consumer
		logger.info("Understanding finished")
		return (idf, participants)

async def consume_queue(consumer, idf):
	"""
	Consume the queue
	"""
	logger.info("Event tracking starting")
	topics = await consumer.run(idf, max_time=EVENT_DURATION, initial_wait=10, max_inactivity=3) # with the ELD consumer
	# _, topics = await consumer.run(EVENT_DURATION)

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
consumer = SimulatedELDConsumer(queue, time_window=TIME_WINDOW, filter_words=FILTER_WORDS)

loop = asyncio.get_event_loop() # the event loop

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

"""
Two processes make up the workflow.
The second part consumes the stream.
"""
queue.dequeue_all()
p_stream = Process(target=consume_stream_task, args=(loop, queue, ))
p_understand = Process(target=consume_task, args=(loop, consumer, return_dict["idf"], ))

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
stream_out = p_stream.join()
logger.info("Stream finished")
understand_out = p_understand.join()
logger.info("Consumer finished")

"""
Clean up
"""
loop.close()
manager.shutdown()
