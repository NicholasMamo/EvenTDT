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
BASE_BIN_SIZE = 30
BASE_SKIP_BINS, BASE_BINS = 0, 60
TRACK = "Mahrez"
TRACK = list(consumer._tokenize([{"text": TRACK, "timestamp_ms": 0}])[0].get_dimensions().keys())[0]

COMPARE_BINS = [ 10, BASE_BIN_SIZE, 60 ]
SKIP_BINS = [ BASE_BIN_SIZE / bin * BASE_SKIP_BINS for bin in COMPARE_BINS ]
BINS = [ BASE_BIN_SIZE / bin * BASE_BINS for bin in COMPARE_BINS ]

burst_data = {}
for (bin_size, skip_bins, bins) in zip(COMPARE_BINS, SKIP_BINS, BINS):
	logger.info("Starting count with a time window of %ds" % bin_size)
	nutrition_store = MemoryNutritionStore()
	consumer = ELDConsumer(Queue(), 60)
	with open(FILENAME, "r") as f:
		nutrition_sets = visysis.calculate_nutrition(f, bin_size, max_bins=bins, skip_bins=skip_bins)
		for timestamp, nutrition_set in nutrition_sets.items():
			nutrition_store.add_nutrition_set(timestamp, nutrition_set)

	nutrition_sets = nutrition_store.get_all_nutrition_sets()
	timestamps = sorted([ int(timestamp) for timestamp in nutrition_sets.keys() ])
	timestamps = [ min(timestamps) + i * bin_size for i in range(0, int((max(timestamps) - min(timestamps))/bin_size) + 1) ]

	burst_values = { timestamp: 0 for timestamp in timestamps[:5] }
	for timestamp in timestamps[5:]:
		burst = mamo_eld.detect_topics(nutrition_store,
			nutrition_sets.get(timestamp, {}),
			threshold=-1, sets=5, timestamp=timestamp,
			decay_rate=1./5., term_only=False)
		burst = dict(burst)
		burst_values[timestamp] = burst.get(TRACK, 0)
	burst_data[bin_size] = burst_values

timestamps = sorted(list(set([ int(timestamp) for burst_values in burst_data.values() for timestamp in burst_values.keys() ])))

"""
Adding missing timestmaps at either end.
"""
for burst_values in burst_data.values():
	for timestamp in timestamps:
		if timestamp in burst_values:
			break
		else:
			burst_values[timestamp] = 0

	for timestamp in timestamps[::-1]:
		if timestamp in burst_values:
			break
		else:
			burst_values[timestamp] = 0

figure, ax = plt.subplots(len(burst_data) - 1, 1, figsize=(25, 10 * (len(burst_data) - 1)))
ax = (ax, ) if len(ax) == 1 else ax
for i, (time_window, burst_values) in enumerate(sorted([ (time_window, burst_values) for time_window, burst_values in burst_data.items() if time_window != BASE_BIN_SIZE ], key=lambda x: x[0])):
	axis = ax[i]
	axis.grid()

	axis.plot(sorted(burst_data[BASE_BIN_SIZE].keys()),
		[ burst for _, burst in sorted(burst_data[BASE_BIN_SIZE].items(), key=lambda x: x[0]) ],
		"--", label="%d second time window" % BASE_BIN_SIZE)

	axis.plot(sorted(burst_values.keys()),
		[ burst for _, burst in sorted(burst_values.items(), key=lambda x: x[0]) ],
		label="%d second time window" % time_window)

	legend = axis.legend()

	axis.set_xlabel("Time (GMT)")
	tick_timestamps = sorted([ timestamp for timestamp in timestamps if int(timestamp) % (60 * 5) == 0 ])
	tick_labels = [ datetime.datetime.utcfromtimestamp(timestamp).strftime("%H:%M") for timestamp in tick_timestamps ]
	axis.set_xticks(tick_timestamps)
	axis.set_xticklabels(tick_labels)

	axis.set_ylabel("Burst")

figure.suptitle("The smoothing effect of time window length on burst")
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("/home/memonick/visualizations/export/burst_window.png")
