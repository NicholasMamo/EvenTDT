import datetime
import json
import os
import sys
import time

path = os.path.dirname(__file__)
path = os.path.join(path, "../libraries")
if path not in sys.path:
	sys.path.append(path)

import analysis as visysis
import palette

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from logger import logger

from queues.consumer.eld.eld_consumer import ELDConsumer
from queues.queue.queue import Queue

from vector.nlp.term_weighting import TF
from vector.nlp.tokenizer import Tokenizer

plt.style.use(os.path.join(sys.path[0], "ember_pastel.style"))

APD_FILENAME = "/mnt/data/twitter/VALMUN_FUL.json"
FILENAME = "/mnt/data/twitter/VALMUN.json"
BIN_SIZE = 60
BINS = 60 * 2.5
DISPLAY = int(60 * 3)

DAY = "4-11-2018"
EVENTS = {
	# "20:34": "Kane miss",
	# "20:40": "Mendy mistake",
	# "21:19": "Fernandinho booked",
}

EVENTS = { int(time.mktime(datetime.datetime.strptime("%s %s" % (DAY, event), "%d-%m-%Y %H:%M").timetuple())): label for event, label in EVENTS.items() }

consumer = ELDConsumer(Queue(), 60) # the consumer, used only for filtering
bin_data, apd_bin_data = {}, {} # the data for the visualization - the keys are the timestamps

logger.info("Starting APD count")
with open(APD_FILENAME, "r") as f:
	apd_bin_data = visysis.count_tweets(f, BIN_SIZE, max_bins=BINS)

logger.info("Starting count")
with open(FILENAME, "r") as f:
	bin_data = visysis.count_tweets(f, BIN_SIZE, max_bins=BINS)

timestamps = sorted(list(set(list(bin_data.keys()) + list(apd_bin_data.keys())))) [-DISPLAY:]
timestamps = timestamps[5:-5]
base_tweets = [ bin_data.get(timestamp, 0) for timestamp in timestamps ]
apd_tweets = [ apd_bin_data.get(timestamp, 0) for timestamp in timestamps ]

from statistics import median, stdev
slopes = { timestamps[i + 1]: apd_bin_data.get(timestamps[i + 1], 0) - apd_bin_data.get(timestamps[i], 0) for i in range(0, len(timestamps) - 1) }
slopes = { timestamp: slope for timestamp, slope in slopes.items() if slope > 0 }
apd_median = median(slopes.values())
apd_stdev = stdev(slopes.values())
for bin in sorted(list(slopes.keys())):
	if slopes[bin] >= 2 * apd_median:
		print(datetime.datetime.utcfromtimestamp(bin).strftime("%H:%M"))

logger.info("%d total tweets encountered without APD" % sum(bin_data.values()))
logger.info("%d total tweets encountered with APD" % sum(apd_bin_data.values()))

plt.figure(figsize=(25,10))
plt.grid()
plt.plot(list(range(0, len(timestamps))), apd_tweets, zorder=11, label="Tweets with APD")
plt.plot(list(range(0, len(timestamps))), base_tweets, zorder=10, label="Tweets without APD")
plt.legend()

plt.xlabel("Time (GMT)")
tick_timestamps = sorted([ timestamp for timestamp in timestamps if int(timestamp) % (60 * 15) == 0 ] + list(EVENTS.keys()))
tick_labels = { timestamp: datetime.datetime.utcfromtimestamp(timestamp).strftime("%H:%M") for timestamp in tick_timestamps }
plt.xticks([ i for i in range(0, len(timestamps)) if timestamps[i] in tick_timestamps ],
	[ tick_labels.get(timestamp) for timestamp in tick_timestamps ])

plt.ylabel("Tweets")
plt.yticks([ i for i in range(0, max(apd_tweets), 500) ])
plt.title("Effect of APD on event coverage")
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/match_coverage.png")
