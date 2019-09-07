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

FILENAME = "/mnt/data/twitter/TOTWOL.json"
BIN_SIZE = 60
BINS = 60 * 22./12.
SKIP_BINS = 15

DAY = "4-11-2018"
EVENTS = {
	# "20:34": "Kane miss",
	# "20:40": "Mendy mistake",
	# "21:19": "Fernandinho booked",
}

EVENTS = { int(time.mktime(datetime.datetime.strptime("%s %s" % (DAY, event), "%d-%m-%Y %H:%M").timetuple())): label for event, label in EVENTS.items() }

consumer = ELDConsumer(Queue(), 60) # the consumer, used only for filtering
bin_data = {}  # the data for the visualization - the keys are the timestamps

logger.info("Starting count")
with open(FILENAME, "r") as f:
	bin_data = visysis.count_tweets(f, BIN_SIZE, max_bins=BINS, skip_bins=SKIP_BINS)

logger.info("%d tweets" % sum(bin_data.values()))
