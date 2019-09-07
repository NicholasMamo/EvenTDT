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

plt.style.use(os.path.join(sys.path[0], "ember_pastel.style"))

APD_FILENAME = "/mnt/data/twitter/ARSLIV_APD.json"
FILENAME = "/mnt/data/twitter/ARSLIV.json"
BIN_SIZE = 60 * 5
SKIP_BINS = 2
BINS = (60 / 5) * 2
DISPLAY = int(60 * 3)
N = 0.2

logger.info("Starting APD count")
with open(APD_FILENAME, "r") as f:
	apd_bin_data = visysis.count_tweets(f, BIN_SIZE, max_bins=BINS, skip_bins=SKIP_BINS)

timestamps = sorted(list(apd_bin_data.keys()))[-DISPLAY:]
n_len = round(len(timestamps) * N)

apd_tweets = sorted([ apd_bin_data.get(timestamp, 0) for timestamp in timestamps ])[::-1]
cumulative_steps = [ sum(apd_tweets[:n])/sum(apd_tweets) for n in range(1, len(timestamps) + 1) ]
n_cover = round(cumulative_steps[n_len], 4)

logger.info("%d total tweets encountered" % sum(apd_bin_data.values()))
logger.info("Top %d%% bins have %.2f%% of tweet volume" % (
	round((n_len + 1) / len(cumulative_steps) * 100),
	n_cover * 100
))

plt.figure(figsize=(25,10))
plt.grid()
plt.bar(list(range(0, len(cumulative_steps))), cumulative_steps, color=palette.primary["red"], edgecolor=palette.stroke["red"], zorder=11)

"""
plt.bar(list(range(0, n_len)), apd_tweets[:n_len], edgecolor=palette.stroke["red"], zorder=11, label="Top %d%%" % (N * 100))
plt.bar(list(range(n_len, len(timestamps))), apd_tweets[n_len:], edgecolor=palette.stroke["blue"], zorder=10, label="Bottom %d%%" % ((1 - N) * 100))
legend = plt.legend()
"""

plt.xlabel("Top Percentage of Time Windows")
x_ticks = sorted([ i for i in range(0, len(cumulative_steps), 4) ] + [ n_len ] )
x_tick_labels = [ "%d%%" % round((x + 1) / len(cumulative_steps) * 100) for x in x_ticks ]
plt.xticks(x_ticks, x_tick_labels)

plt.ylabel("Percentage of all tweets")
y_ticks = sorted([ i / 100. for i in range(0, 101, 20) if abs(i / 100. - n_cover) > 0.05 ] + [ n_cover ])
y_tick_labels = [ ("%d%%" if (i % 100) % 1 == 0 else "%.2f%%") % (i * 100) for i in y_ticks ]
plt.yticks(y_ticks, y_tick_labels)

plt.title("Emotional charge in tweet volume")
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/top_n.png")
