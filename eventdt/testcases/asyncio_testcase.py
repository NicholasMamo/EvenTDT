import asyncio
import os
import random
import sys
import time
import unittest

async def print_name(name):
	n = await get_name(name)
	print(n)

async def get_name(name):
	await asyncio.sleep(1)
	return "c-%s" % (name)

def get_random():
	return random.randint(0, 10)

async def aget_random():
	return random.randint(0, 10)

async def arandom_stop(loop):
	while True:
		await asyncio.sleep(2)
		i = await aget_random()
		print("A:", i)
		if i == 0:
			break
	print("A Ended")

async def random_stop(loop):
	while True:
		await asyncio.sleep(2)
		i = get_random()
		print("NA:", i)
		if i == 0:
			break
	print("NA Ended")

async def multiple_tasks():
	loop = asyncio.get_event_loop()
	input_coroutines = [
	  	random_stop(loop),
	  	arandom_stop(loop)
	]
	res = await asyncio.gather(*input_coroutines, return_exceptions=True)
	return res

loop = asyncio.get_event_loop()
loop.run_until_complete(multiple_tasks())
loop.close()
