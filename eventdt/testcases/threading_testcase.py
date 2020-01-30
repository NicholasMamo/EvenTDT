import math
import threading
import time

# compare difference with multiprocessing_testcase.py using top -u memonick
# press 1 to see CPU usage per core
# when timed, this takes 43.8s

start = time.time()
closed = 0
class cThread (threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
	def run(self):
		global closed
		print("Starting " + self.name)
		# greet("person " + self.name)
		computation()
		print("Exiting " + self.name)
		closed = closed + 1

def computation():
	for i in range(0, int(1e3)):
		for j in range(0, int(1e4)):
			math.sqrt(i + j)

def greet(name):
	time.sleep(2)
	print("Hello", name)

worker_count = 16
try:
	worker_pool = []
	for i in range(0, worker_count):
		t = cThread(i, "p%d" % i, i)
		worker_pool.append(t)

	for t in worker_pool:
		t.start()
except:
   print("Error: unable to start thread")

while closed < worker_count:
   pass

print("Finished in %.2fs" % (time.time() - start))
