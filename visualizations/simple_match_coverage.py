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
BIN_SIZE = 60
BINS = 60 * 2.5
DISPLAY = int(60 * 3)

consumer = ELDConsumer(Queue(), 60) # the consumer, used only for filtering
bin_data = {} # the data for the visualization - the keys are the timestamps

logger.info("Starting APD count")
with open(APD_FILENAME, "r") as f:
	bin_data = visysis.count_tweets(f, BIN_SIZE, max_bins=BINS)

timestamps = sorted(list(bin_data.keys())) [-DISPLAY:]
timestamps = timestamps[1:-1]
tweets = [ bin_data.get(timestamp, 0) for timestamp in timestamps ]

logger.info("%d total tweets encountered with APD" % sum(bin_data.values()))

plt.figure(figsize=(25,10))
plt.grid()
plt.plot(list(range(0, len(timestamps))), tweets, zorder=11, label="Tweets")
legend = plt.legend()

plt.xlabel("Time (GMT)")
tick_timestamps = sorted([ timestamp for timestamp in timestamps if int(timestamp) % (60 * 15) == 0 ])
tick_labels = { timestamp: datetime.datetime.utcfromtimestamp(timestamp).strftime("%H:%M") for timestamp in tick_timestamps }
plt.xticks([ i for i in range(0, len(timestamps)) if timestamps[i] in tick_timestamps ],
	[ tick_labels.get(timestamp) for timestamp in tick_timestamps ])

plt.ylabel("Tweets")
plt.yticks([ i for i in range(0, max(tweets), 500) ])
plt.title("Volume of tweets during an event")
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/simple_match_coverage.png")
