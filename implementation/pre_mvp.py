from multiprocessing import Process

from tweepy import OAuthHandler
from tweepy import Stream

import asyncio
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))

from queues.consumer.print_consumer import PrintConsumer
from queues.queue.queue import Queue
from twitter import globals
from twitter.twevent.listener import TweetListener
from twitter.twevent.queued_listener import QueuedListener

EVENT_DURATION = 5
FILENAME = "/home/memonick/data/twitter/test.json"
KEYWORDS = ["World Cup"]

queue = Queue()
consumer = PrintConsumer(queue)
# listener = TweetListener(FILENAME, max_time=EVENT_DURATION)
listener = QueuedListener(queue, max_time=EVENT_DURATION)
auth = OAuthHandler(globals.CONSUMER_KEY, globals.CONSUMER_SECRET)
auth.set_access_token(globals.ACCESS_TOKEN, globals.ACCESS_TOKEN_SECRET)

def consume_task(loop, consumer):
	loop.run_until_complete(consume_queue(consumer))

def stream_task(loop, listener):
	loop.run_until_complete(create_stream(listener))

def shutdown_task(loop, listener):
	loop.run_until_complete(shutdown(consumer))

async def shutdown(consumer):
	print("Shutdown task created")
	while not consumer.is_stopped():
		print("No activity")
		await asyncio.sleep(5)
	print("Shutdown initiated")
	loop.stop()

async def create_stream(listener, consumer):
	stream = Stream(auth, listener)
	print("Stream created")
	stream.filter(track=KEYWORDS, is_async=True)
	await asyncio.sleep(EVENT_DURATION)
	print("Stream finished")
	consumer.stop()

async def consume_queue(consumer):
	await consumer.run()

loop = asyncio.get_event_loop()
loop.create_task(create_stream(listener, consumer))
loop.create_task(consume_queue(consumer))
loop.create_task(shutdown(consumer))
loop.run_forever()
loop.close()
