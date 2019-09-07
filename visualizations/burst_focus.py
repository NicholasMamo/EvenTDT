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

from topic_detection.algorithms import mamo_eld
from topic_detection.nutrition_store.memory_nutrition_store import MemoryNutritionStore

from vector import vector_math
from vector.nlp.term_weighting import TF
from vector.nlp.tokenizer import Tokenizer

consumer = ELDConsumer(Queue(), 60) # the consumer, used only for filtering

plt.style.use(os.path.join(sys.path[0], "ember_pastel.style"))

FILENAME = "/mnt/data/twitter/TOTMCI_APD.json"
BIN_SIZE = 60
SKIP_BINS, BINS = 5, 60
TRACK = "Mahrez"
TRACK = list(consumer._tokenize([{"text": TRACK, "timestamp_ms": 0}])[0].get_dimensions().keys())[0]

logger.info("Starting count")
nutrition_store = MemoryNutritionStore()
consumer = ELDConsumer(Queue(), 60)
with open(FILENAME, "r") as f:
	nutrition_sets = visysis.calculate_nutrition(f, BIN_SIZE, max_bins=BINS, skip_bins=SKIP_BINS)
	for timestamp, nutrition_set in nutrition_sets.items():
		nutrition_store.add_nutrition_set(timestamp, nutrition_set)

nutrition_sets = nutrition_store.get_all_nutrition_sets()
timestamps = sorted(nutrition_sets.keys())
timestamps = [ min(timestamps) + i * BIN_SIZE for i in range(0, int((max(timestamps) - min(timestamps))/BIN_SIZE) + 1) ]

burst_values = [ 0 ] * 5
for timestamp in timestamps[5:]:
	burst = mamo_eld.detect_topics(nutrition_store,
		nutrition_sets[timestamp],
		threshold=-1, sets=5, timestamp=timestamp,
		decay_rate=1./5., term_only=False)
	burst = dict(burst)
	burst_values.append(burst.get(TRACK, 0))

fig, ax1 = plt.subplots(figsize=(23,10))
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
ax1.set_title("Burst variation based on nutrition")
ax1.grid()

nutrition_line = ax1.plot(list(range(0, len(timestamps))), [ nutrition_sets[timestamp].get(TRACK, 0) for timestamp in timestamps ], color=palette.primary["blue"], zorder=10, label="Nutrition of '%s'" % TRACK.title())
ax1.set_yticks([ i * .25 for i in range(-4, 5) ])

burst_line = ax2.plot(list(range(0, len(timestamps))), burst_values, color=palette.primary["red"], zorder=10, label="Burst of '%s'" % TRACK.title())
ax2.set_yticks([ i * .25 for i in range(-4, 5) ])
ax2.yaxis.label.set_rotation(270)

components = [ nutrition_line[0], burst_line[0] ]
labels = [ nutrition_line[0].get_label(), burst_line[0].get_label() ]
legend = plt.legend(components, labels)
legend.set_zorder(12)

plt.sca(ax1)
plt.xlabel("Time (GMT)")
tick_timestamps = sorted([ timestamp for timestamp in timestamps if int(timestamp) % (60 * 15) == 0 ])
tick_labels = { timestamp: datetime.datetime.utcfromtimestamp(timestamp).strftime("%H:%M") for timestamp in tick_timestamps }
plt.xticks([ i for i in range(0, len(timestamps)) if timestamps[i] in tick_timestamps ],
	[ tick_labels.get(timestamp) for timestamp in tick_timestamps ],
	rotation=45, ha="right")

ax1.set_ylabel("Nutrition")
ax2.set_ylabel("Burst")
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/burst_focus.png")
