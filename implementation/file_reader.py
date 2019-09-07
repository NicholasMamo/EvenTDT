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

sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))

from queues.consumer.print_consumer import PrintConsumer
from queues.consumer.stat_consumer import StatConsumer
from queues.queue.queue import Queue
from twitter import globals
from twitter.twevent.file_listener import StaggeredFileListener
from twitter.twevent.simulated_file_listener import SimulatedFileListener

FILENAME = "twitter/COLENG.json"

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

def consume_task(loop, consumer):
	"""
	Create the task that consumes the queue
	"""
	loop.run_until_complete(consume_queue(consumer))

def stream_task(loop, queue):
	"""
	Create the task that streams data from a file
	"""
	loop.run_until_complete(create_stream(queue))

async def create_stream(queue):
	"""
	Stream information from Twitter using the given listener
	"""
	with open(os.path.join(os.path.dirname(__file__), "../data", FILENAME)) as f:
		# listener = StaggeredFileListener(queue, f, max_lines=100, lines_per_second=2, skip=0)
		listener = SimulatedFileListener(queue, f, max_time=60)
		listener.read()

async def consume_queue(consumer):
	"""
	Consume the queue
	"""
	await consumer.run(max_inactivity=1)

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
consumer = StatConsumer(queue, periodicity=10)

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
