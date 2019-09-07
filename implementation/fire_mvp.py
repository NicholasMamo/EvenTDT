"""
The skeleton of the MVP
This skeleton may also be used in the final version
The main changes all go into the consumer
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
from queues.consumer.eld.fire_consumer import FIREConsumer
from queues.queue.queue import Queue

from twitter import globals
from twitter.twevent.listener import TweetListener
from twitter.twevent.simulated_file_listener import SimulatedFileListener
from twitter.twevent.queued_listener import QueuedListener

"""
How long the event should be tracked
"""
EVENT_DURATION = 3600 * 2.5

"""
The name of the file if a file listener is used
"""
FILENAME = "TOTMCI_APD.json"

"""
The keywords to track
"""
KEYWORDS = ["morning"]

IDF = "idf.json"

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

def consume_task(loop, consumer):
	"""
	Create the task that consumes the queue
	"""
	loop.run_until_complete(consume_queue(consumer))

def stream_task(loop, queue):
	"""
	Create the task that streams data from Twitter
	"""
	listener = QueuedListener(queue, max_time=EVENT_DURATION)
	loop.run_until_complete(create_stream(listener))

async def create_stream(listener):
	"""
	Stream information from Twitter using the given listener
	"""
	with open(os.path.join("/mnt/data/twitter", FILENAME)) as f:
	# with open(os.path.join(os.path.dirname(__file__), "../data/twitter", FILENAME)) as f:
		listener = SimulatedFileListener(queue, f, speed=2, max_time=EVENT_DURATION/2, skip_time=0)
		await listener.read()

	# stream = Stream(auth, listener)
	# stream.filter(track=KEYWORDS)

async def consume_queue(consumer):
	"""
	Consume the queue
	"""
	_, topics = await consumer.run(initial_wait=6, max_inactivity=3)
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

with open(os.path.join("/home/memonick/data", IDF), "r") as idf_file:
	general_idf = json.loads(idf_file.readline())

consumer = FIREConsumer(queue, periodicity=30, idf=general_idf)

loop = asyncio.get_event_loop() # the event loop

"""
Two processes make up the workflow
The first one streams from Twitter
The second one consumes the tweets
"""
p_stream = Process(target=stream_task, args=(loop, queue, ))
p_consumer = Process(target=consume_task, args=(loop, consumer, ))

"""
Start the processes
"""
p_stream.start()
logger.info("Stream started with pid %s" % p_stream.pid)
p_consumer.start()
logger.info("Consumer started with pid %s" % p_consumer.pid)

"""
And wait for them to finish
"""
p_stream.join()
logger.info("Stream finished")
p_consumer.join()
logger.info("Consumer finished")

"""
Clean up
"""
loop.close()
manager.shutdown()
