from datetime import datetime, timedelta

import json
import os

FILENAME = "GERSWE.json"
WINDOW_LENGTH = 60 * 15

def get_timestamp(t):
	year = t[-4:]
	offset = t[-10:-5]

	dt = t[:-11] + " " + year

	dt = datetime.strptime(dt, "%a %b %d %H:%M:%S %Y")

	timezone_offset = int(offset[-4:-2]) * 60 + int(offset[-2:])
	timezone_offset = -timezone_offset if (offset[0] == '-') else timezone_offset

	dt -= timedelta(minutes=timezone_offset) # if the offset is positive, make it negative, and vice versa

	start = datetime(1970, 1, 1)
	delta = dt - start
	timestamp = int(delta.total_seconds())
	return timestamp

def get_minute(utc):
	return utc - (utc % WINDOW_LENGTH)

counter = {}
path = os.path.join(os.path.dirname(__file__), "twitter/%s" % FILENAME)
lines = 0
with open(path, "r") as f:
	for line in f:
		tweet = json.loads(line)
		if "created_at" in tweet:
			timestamp = get_timestamp(tweet["created_at"])
			time_window = get_minute(timestamp)
			counter[time_window] = counter.get(time_window, 0) + 1
		
		lines += 1
		if lines % 100000 == 0:
			print("%d lines read" % lines)

for time_window in sorted(counter):
	print("%s\t%d tweets/second\t%d total tweets" % (time_window, counter[time_window]/WINDOW_LENGTH, counter[time_window]))
