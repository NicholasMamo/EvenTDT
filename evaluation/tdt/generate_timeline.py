from datetime import datetime

import json
import os
import re
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, "../../libraries")
if path not in sys.path:
	sys.path.insert(1, path)

path = os.path.join(path, "..")
if path not in sys.path:
	sys.path.insert(1, path)

from nltk.corpus import stopwords

from logger import logger

from vector.cluster.cluster import Cluster
from vector.nlp.cleaners import tweet_cleaner
from vector.nlp.term_weighting import TF, TFIDF
from vector.nlp.tokenizer import Tokenizer

from summarization.algorithms.update import baseline_mmr, mamo_graph, mamo_mmr
from summarization.scorers import tweet_scorer
from summarization.summary import Summary

"""
The name of the file to summarize.
"""
if len(sys.argv) >= 2:
	OUT_DIR = "/home/memonick/evaluation/tdt"
	NAME = sys.argv[1:]

	with open(os.path.join(OUT_DIR, "temp.txt"), "w") as o:
		o.write("%s\n" % '_'.join(NAME))
		with open("/mnt/evaluation/tdt/timeline/%s_timeline.json" % ('_'.join(NAME)), "r") as f:
			for line in f:
				data = json.loads(line)
				summary = Summary.from_array(data)
				o.write(summary.generate_summary(tweet_cleaner.TweetCleaner))
				o.write("\n")
