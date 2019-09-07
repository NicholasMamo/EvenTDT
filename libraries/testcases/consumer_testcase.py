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
import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], '../'))

from logger import logger

from queues.consumer.stat_consumer import StatConsumer
from queues.queue.queue import Queue

from twitter import globals
from twitter.twevent.listener import TweetListener
from twitter.twevent.queued_listener import QueuedListener

"""
How long the event should be tracked
"""
EVENT_DURATION = 60 * 10

"""
The keywords to track
"""
KEYWORDS = ["morning", "night"]

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

def get_time():
	"""
	Get the time string
	"""
	return datetime.now().strftime("%H:%M:%S")

def consume_task(loop, queue):
	"""
	Create the task that consumes the queue
	"""
	loop.run_until_complete(consume_queue(queue))

def stream_task(loop, queue):
	"""
	Create the task that streams data from Twitter
	"""
	listener = QueuedListener(queue, max_time=EVENT_DURATION, silent=False)
	loop.run_until_complete(create_stream(listener))

async def create_stream(listener):
	"""
	Stream information from Twitter using the given listener
	"""
	stream = Stream(auth, listener)
	stream.filter(track=KEYWORDS)

async def consume_queue(queue):
	"""
	Consume the queue
	"""

	wait = 0 # number of times the queue was empty
	last_timestamp = 0
	total_tweets, misplaced_tweets = 0, { }
	while wait < 3:
		if queue.length() == 0:
			wait += 1
		else:
			wait = 0

		tweets = queue.dequeue_all()
		for tweet in tweets:
			total_tweets += 1
			timestamp_ms = int(tweet["timestamp_ms"]) - int(tweet["timestamp_ms"]) % 1000
			timestamp = int(timestamp_ms / 1000)
			if timestamp < last_timestamp:
				misplaced_tweets[last_timestamp - timestamp] = misplaced_tweets.get(last_timestamp - timestamp, 0) + 1
			last_timestamp = timestamp

			if total_tweets > 0 and total_tweets % 100 == 0:
				logger.info("%d tweets read, %.2f%% tweets misplaced" % (total_tweets, sum(misplaced_tweets.values())/total_tweets * 100))
			if total_tweets > 0 and total_tweets % 100 == 0:
				logger.info("Breakdown of misplacement: %s" % ('; '.join([ "%ds: %d" % (delay, frequency) for delay, frequency in misplaced_tweets.items() ])))
		time.sleep(1)

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

loop = asyncio.get_event_loop() # the event loop

"""
Two processes make up the workflow
The first one streams from Twitter
The second one consumes the tweets
"""
p_stream = Process(target=stream_task, args=(loop, queue, ))
p_consumer = Process(target=consume_task, args=(loop, queue, ))

"""
Start the processes
"""
p_stream.start()
print(get_time(), "Stream started with pid", p_stream.pid)
p_consumer.start()
print(get_time(), "Consumer started with pid", p_consumer.pid)

"""
And wait for them to finish
"""
p_stream.join()
print(get_time(), "Stream finished")
p_consumer.join()
print(get_time(), "Consumer finished")

"""
Clean up
"""
loop.close()
manager.shutdown()
