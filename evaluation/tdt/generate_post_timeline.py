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
	RAW_DIR = "/mnt/evaluation/tdt/raw"
	OUT_DIR = "/home/memonick/evaluation/tdt"
	NAME = sys.argv[1:]

	count = 0
	with open(os.path.join(OUT_DIR, "temp.txt"), "w") as o:
		with open("%s/%s_raw.json" % (RAW_DIR, '_'.join(NAME)), "r") as f:
			for development, line in enumerate(f):

				"""
				Load the documents.
				"""
				data = json.loads(line)
				terms = [ cluster["terms"] for cluster in data["clusters"] ]
				clusters = [ Cluster.from_array(cluster["cluster"]) for cluster in data["clusters"] ]
				documents = [ document for cluster in clusters for document in cluster.get_vectors() ]

				if any("Graph" in component for component in NAME):
					summarizer = mamo_graph.DocumentGraphSummarizer(scorer=tweet_scorer.TweetScorer)
				elif any("FMMR" in component for component in NAME):
					summarizer = mamo_mmr.FragmentedMMR(scorer=tweet_scorer.TweetScorer)

				for term_set, cluster in zip(terms, clusters):
					summarizer.add_cluster(cluster, term_set, 0)

				summary = summarizer.create_summary()
				print(summary.generate_summary(tweet_cleaner.TweetCleaner))
				o.write(summary.generate_summary(tweet_cleaner.TweetCleaner))
				o.write("\n")
				count += 1
				if count == 3:
					pass
					# break
