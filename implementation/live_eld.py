"""
26/08/2018: No longer works after changes to the Document structure.

The skeleton of the MVP.

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
from queues.consumer.eld.eld_consumer import ELDConsumer
from queues.queue.queue import Queue

from twitter import globals
from twitter.twevent.listener import TweetListener
from twitter.twevent.simulated_file_listener import SimulatedFileListener
from twitter.twevent.queued_listener import QueuedListener

"""
How long the event should be tracked
"""
UNDERSTAND_DURATION = 30
EVENT_DURATION = 60 * 30

"""
The name of the file if a file listener is used
"""
IDF = "idf.json"

"""
The keywords to track
"""
KEYWORDS = ["#ARSMUN"]

"""
Authenticate with Tweepy
"""
auth = OAuthHandler(globals.ALT_CONSUMER_KEY, globals.ALT_CONSUMER_SECRET)
auth.set_access_token(globals.ALT_ACCESS_TOKEN, globals.ALT_ACCESS_TOKEN_SECRET)

class QueueManager(BaseManager):
	"""
	A dummy class used to share the queue between processes
	"""

	pass

def understand_task(loop, consumer, return_dict):
	"""
	Create the task that understands the event using Twitter
	"""

	(idf, participants, ) = loop.run_until_complete(asyncio.gather(understand_queue(consumer), ))[0]
	return_dict["idf"] = idf
	return_dict["participants"] = participants

def stream_task(loop, queue, keywords, max_time):
	"""
	Create the task that streams data from Twitter
	"""

	listener = QueuedListener(queue, max_time=max_time)
	loop.run_until_complete(create_stream(listener, keywords))

def consume_task(loop, consumer, idf):
	"""
	Create the task that consumes the queue
	"""

	loop.run_until_complete(consume_queue(consumer, idf))

async def understand_stream(listener):
	"""
	Stream information from Twitter using the given listener
	"""

	logger.info("Listening to %s" % ','.join(KEYWORDS))
	stream = Stream(auth, listener)
	stream.filter(track=KEYWORDS)

async def understand_queue(consumer):
	"""
	Consume the queue
	"""

	idf = open(os.path.join("/home/memonick/data", IDF))
	idf_dict = json.loads(idf.readline())
	idf.close()

	(idf, participants) = await consumer.understand(UNDERSTAND_DURATION, idf_dict, max_inactivity=10)
	return (idf, participants)

async def create_stream(listener, keywords):
	"""
	Stream information from Twitter using the given listener
	"""

	logger.info("Listening to %s" % ','.join(keywords))
	stream = Stream(auth, listener)
	stream.filter(track=keywords)

async def consume_queue(consumer, idf):
	"""
	Consume the queue
	"""

	await consumer.run(idf, max_time=EVENT_DURATION, max_inactivity=10)

"""
Register the queue with the manager
This allows it to be shared between the two processes
"""

QueueManager.register("Queue", Queue)
QueueManager.register("list", list)

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
consumer = ELDConsumer(queue, 10)
# consumer = PrintConsumer(queue)
# consumer = StatConsumer(queue, periodicity=5)

loop = asyncio.get_event_loop() # the event loop

"""
Two processes make up the workflow.
The first one streams from Twitter to understand the event.
The second one consumes these tweets.
"""

p_stream = Process(target=stream_task, args=(loop, queue, KEYWORDS, UNDERSTAND_DURATION))
p_understand = Process(target=understand_task, args=(loop, consumer, return_dict, ))
"""
Start the processes
"""

p_stream.start()
logger.info("Stream started with pid %s" % p_stream.pid)
p_understand.start()
logger.info("Consumer started with pid %s" % p_understand.pid)

"""
And wait for them to finish
"""

p_stream.join()
logger.info("Stream finished")
p_understand.join()
logger.info("Consumer finished")

"""
Now, consume the real queue
"""

p_stream = Process(target=stream_task, args=(loop, queue, KEYWORDS + return_dict["participants"], EVENT_DURATION ))
p_consumer = Process(target=consume_task, args=(loop, consumer, return_dict["idf"]))

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
