from datetime import datetime

import json
import os
import re
import shutil
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

if len(sys.argv) == 2:
	"""
	The name of the file to summarize.
	"""
	OUT_DIR = "/mnt/evaluation/summarization/mead_files"
	NAME = sys.argv[1]
	TDT = "ELD"

	with open(os.path.join(OUT_DIR, "temp.txt"), "w") as o:
		summary_dir = os.path.join(OUT_DIR, "%s" % (NAME))
		summaries = sorted([ int(dir) for dir in os.listdir(summary_dir) ])
		for summary in summaries:
			with open(os.path.join(summary_dir, str(summary), "clean_summary.txt"), "r") as f:
				lines = [ line.replace("\n", "") for line in f.readlines() ]
				o.write(' '.join(lines))
				o.write("\n")
