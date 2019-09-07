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

FILENAME = "/mnt/data/twitter/VALMUN_FUL.json"
BIN_SIZE = 60
BINS = 60 * 2.5
DISPLAY = int(60 * 3)

DAY = "12-12-2018"
EVENTS = {
	"21:07": "Jones own goal",
}

EVENTS = { int(time.mktime(datetime.datetime.strptime("%s %s" % (DAY, event), "%d-%m-%Y %H:%M").timetuple())): label for event, label in EVENTS.items() }

consumer = ELDConsumer(Queue(), 60) # the consumer, used only for filtering
bin_data = {} # the data for the visualization - the keys are the timestamps

logger.info("Starting count")
with open(FILENAME, "r") as f:
	bin_data = visysis.count_tweets(f, BIN_SIZE, max_bins=BINS)

timestamps = sorted(list(bin_data.keys())) [-DISPLAY:]
timestamps = timestamps[5:-5]
tweets = [ bin_data.get(timestamp, 0) for timestamp in timestamps ]

fill_areas = {}
for event_timestamp in EVENTS.keys():
	shadow_timestamps = [ timestamp for timestamp in timestamps if timestamp > event_timestamp ]
	pre_shadow_timestamps = [ timestamp for timestamp in timestamps if timestamp < event_timestamp ]
	volume_cutoff = max([ bin_data.get(timestamp) for timestamp in pre_shadow_timestamps ])

	shadow_cutoff = event_timestamp
	for timestamp in sorted(shadow_timestamps):
		if bin_data.get(timestamp, 0) <= volume_cutoff:
			shadow_cutoff = timestamp
			break

	fill_timestamps = [event_timestamp] + [ timestamp for timestamp in shadow_timestamps if timestamp <= shadow_cutoff ]
	fill_areas[event_timestamp] = (
		[ i for i in range(0, len(timestamps)) if timestamps[i] in fill_timestamps ],
		[ bin_data.get(timestamp) for timestamp in fill_timestamps ]
	)

	fill_areas[event_timestamp][0].insert(0, fill_areas[event_timestamp][0][0])
	fill_areas[event_timestamp][1].insert(0, 0)
	fill_areas[event_timestamp][0].append(fill_areas[event_timestamp][0][-1])
	fill_areas[event_timestamp][1].append(0)

logger.info("%d total tweets encountered" % sum(bin_data.values()))

plt.figure(figsize=(25,10))
plt.grid()
plt.plot(list(range(0, len(timestamps))), tweets, zorder=11, label="Tweet volume")
for x, y in fill_areas.values():
	plt.fill(x, y, facecolor="none",
		hatch="x", edgecolor=list(plt.rcParams['axes.prop_cycle'])[0]["color"])
plt.legend()

plt.xlabel("Time (GMT)")
tick_timestamps = sorted([ timestamp for timestamp in timestamps if int(timestamp) % (60 * 15) == 0 ] + list(EVENTS.keys()))
tick_labels = { timestamp: EVENTS.get(timestamp, datetime.datetime.utcfromtimestamp(timestamp).strftime("%H:%M")) for timestamp in tick_timestamps }
plt.xticks([ i for i in range(0, len(timestamps)) if timestamps[i] in tick_timestamps ],
	[ tick_labels.get(timestamp) for timestamp in tick_timestamps ],
	rotation=45, ha="right")

plt.ylabel("Tweets")
plt.yticks([ i for i in range(0, max(tweets), 500) ])
plt.title("Event shadow during a football match")
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/event_shadow.png")
