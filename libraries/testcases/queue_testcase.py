import os
import random
import sys
import time
import unittest

sys.path.insert(1, os.path.join(sys.path[0], '../'))

from queues.consumer.print_consumer import PrintConsumer
from queues.queue.queue import Queue

import asyncio

class Generator(object):

	def __init__(self, q):
		self.q = q

	def generate(self):
		e = random.randint(0, 10)
		self.q.enqueue(e)
		return e

queue = Queue()
consumer = PrintConsumer(queue)
generator = Generator(queue)

async def generate(loop, queue, consumer):
	while True:
		# e = random.randint(0, 10)
		# queue.enqueue(e)
		# print("Added", e)
		e = generator.generate()
		print("Added", e)
		if e == 5:
			consumer.stop()
			break
		await asyncio.sleep(3)
	print("Waiting to stop the loop")
	while not consumer.is_stopped():
		await asyncio.sleep(1)
	print("Loop to stop")
	loop.stop()
	print("Loop stopped")

loop = asyncio.get_event_loop()
loop.create_task(generate(loop, queue, consumer))
loop.create_task(consumer.run())
loop.run_forever()
loop.close()
