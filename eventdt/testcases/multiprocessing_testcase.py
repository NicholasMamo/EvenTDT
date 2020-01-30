import math
import time
from multiprocessing import Process

# compare difference with threading_testcase.py using top -u memonick
# press 1 to see CPU usage per core
# when timed, this takes 18.46s

start = time.time()
def greet(name):
	time.sleep(10)
	print("Hello", name)

def computation():
	for i in range(0, int(1e3)):
		for j in range(0, int(1e4)):
			math.sqrt(i + j)

worker_count = 16
worker_pool = []
for i in range(0, worker_count):
	p = Process(target=computation)
	# p = Process(target=greet, args=("person %d" % i, ))
	worker_pool.append(p)
	p.start()

for p in worker_pool:
	p.join()

print("Finished in %.2fs" % (time.time() - start))
