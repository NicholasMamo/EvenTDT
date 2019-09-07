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

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.scorers.local.sum_scorer import SumScorer, LogSumScorer

from queues.consumer.eld.eld_consumer import ELDConsumer
from queues.queue.queue import Queue

from vector.nlp.document import Document

plt.style.use(os.path.join(sys.path[0], "ember_pastel.style"))

FILENAME = "/mnt/data/twitter/u_CHECRY_APD.json"
WIDTH = 0.35

consumer = ELDConsumer(Queue(), 60) # the consumer, used only for filtering

logger.info("Building distribution")
with open(FILENAME, "r") as f:
	corpus = list(visysis.aggregate_documents(f).values())[0]

documents = EntityExtractor().extract(corpus)
sum_candidates = SumScorer().score(documents)
sum_scores = sorted(sum_candidates.values())[:-21:-1]

log_sum_candidates = sorted(LogSumScorer().score(documents).items(), key=lambda x: x[1])[::-1]
log_sum_scores = [ score for _, score in log_sum_candidates[:20] ]
log_sum_labels = [ candidate if len(candidate) < 15 else "%s..." % candidate[:15] for candidate, _ in log_sum_candidates[:20] ]

plt.figure(figsize=(20,10))
plt.bar(range(0, len(sum_scores)), log_sum_scores, WIDTH, edgecolor=palette.stroke["red"], zorder=8, label="Log10 Sum")
plt.bar([ i + WIDTH for i in range(0, len(sum_scores)) ], sum_scores, WIDTH, edgecolor=palette.stroke["blue"], zorder=9, label="Sum")
legend = plt.legend()

plt.xticks([ i + WIDTH / 2 for i in range(0, len(sum_scores)) ], log_sum_labels, rotation=45, ha="right")
plt.xlabel("Candidate")
plt.ylabel("Rescaled Score")
plt.title("Popularity of candidate participants")
plt.tight_layout()
plt.savefig("/home/memonick/visualizations/export/participant_distribution.png")
