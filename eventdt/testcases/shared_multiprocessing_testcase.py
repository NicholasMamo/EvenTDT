import math
import time
from multiprocessing import Process
from multiprocessing.managers import BaseManager

class CustomManager(BaseManager):
	pass

class Container:

	i = 0

	def inc(self):
		self.i += 1

	def pprint(self):
		print("i:", self.i)

	def __str__(self):
		print(str(self.i))

def increment(c):
	for i in range(0, 3):
		c.inc()
		time.sleep(0.5)

def print_i(c):
	for i in range(0, 3):
		c.pprint()
		time.sleep(0.5)

CustomManager.register("Container", Container)
manager = CustomManager()
manager.start()
container = manager.Container()

p_i = Process(target=increment, args=(container, ))
p_p = Process(target=print_i, args=(container, ))

p_i.start()
p_p.start()

p_i.join()
p_p.join()

manager.shutdown()
