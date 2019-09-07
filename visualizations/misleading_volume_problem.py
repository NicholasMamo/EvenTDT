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

APD_FILENAME = "/mnt/data/twitter/TOTMCI_APD.json"
FILENAME = "/mnt/data/twitter/TOTMCI.json"
BIN_SIZE = 30
BINS = 35 * 60 / BIN_SIZE
DISPLAY = int(25 * 60 / BIN_SIZE )
HIGHLIGHT = "Kane"

DAY = "29-10-2018"
EVENTS = {
	"20:06:00": "Mahrez goal",
	"20:08:30": "Kane miss",
}

EVENTS = { int(time.mktime(datetime.datetime.strptime("%s %s" % (DAY, event), "%d-%m-%Y %H:%M:%S").timetuple())): label for event, label in EVENTS.items() }

consumer = ELDConsumer(Queue(), 60) # the consumer, used only for filtering
bin_data = {} # the data for the visualization - the keys are the timestamps
highlight_data = {} # the data for the highlighted keyword - the keys are the timestamps

logger.info("Starting APD count")
with open(APD_FILENAME, "r") as f:
	bin_data = visysis.count_tweets(f, BIN_SIZE, max_bins=BINS)
	highlight_data = visysis.count_tweets(f, BIN_SIZE, max_bins=BINS, track=HIGHLIGHT)

timestamps = sorted(list(bin_data.keys()))[-DISPLAY:]
apd_tweets = [ bin_data.get(timestamp, 0) for timestamp in timestamps ]
highlight_tweets = [ highlight_data.get(timestamp, 0) for timestamp in timestamps ]

logger.info("%d total tweets encountered" % sum(bin_data.values()))
logger.info("%d total tweets that include %s" % (sum(highlight_data.values()), HIGHLIGHT.title()))

plt.figure(figsize=(25,10))
plt.grid()
plt.plot(list(range(0, len(timestamps))), apd_tweets, color=palette.primary["red"], zorder=11, label="Tweet volume")
plt.plot(list(range(0, len(timestamps))), highlight_tweets, linestyle="dashed", zorder=11, label="Mentions of %s" % HIGHLIGHT.title())

legend = plt.legend(loc="upper right")

plt.xlabel("Time (GMT)")
tick_timestamps = sorted([ timestamp for timestamp in timestamps if int(timestamp) % (60 * 5) == 0 ] + list(EVENTS.keys()))
tick_labels = { timestamp: datetime.datetime.utcfromtimestamp(timestamp).strftime("%H:%M") for timestamp in tick_timestamps }
plt.xticks([ i for i in range(0, len(timestamps)) if timestamps[i] in tick_timestamps ],
	[ EVENTS.get(timestamp, tick_labels.get(timestamp)) for timestamp in tick_timestamps ],
	rotation=45, ha="right")

plt.ylabel("Tweets")
plt.title("Misleading tweet volume and slopes")
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/misleading_volume_problem.png")
