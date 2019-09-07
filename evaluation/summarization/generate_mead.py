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
	RAW_DIR = "/mnt/evaluation/tdt/raw"
	OUT_DIR = "/mnt/evaluation/summarization/mead_files"
	NAME = sys.argv[1]
	TDT = "ELD"

	with open("%s/%s_raw.json" % (RAW_DIR, NAME), "r") as f:
		"""
		Prepare the output directory.
		"""
		if os.path.isdir("%s/%s" % (OUT_DIR, NAME)):
			shutil.rmtree("%s/%s" % (OUT_DIR, NAME))
		os.mkdir("%s/%s" % (OUT_DIR, NAME))

		for development, line in enumerate(f):
			"""
			Load the documents.
			"""
			data = json.loads(line)
			clusters = [ Cluster.from_array(cluster["cluster"]) for cluster in data["clusters"] ]
			documents = [ document for cluster in clusters for document in cluster.get_vectors() ]
			documents = sorted(documents, key = lambda x: int(x.get_attribute("timestamp")))

			os.mkdir("%s/%s/%d" % (OUT_DIR, NAME, development + 1))
			for i, document in enumerate(documents):
				if len(document.get_text()) > 0:
					with open("%s/%s/%d/%d.txt" % (OUT_DIR, NAME, development + 1, i + 1), "w") as df:
						df.write(document.get_text())
