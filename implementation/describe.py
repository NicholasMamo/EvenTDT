import json
import os
import re
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, "../libraries")
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

"""
The name of the file to summarize.
"""
NAME = "PSGLIV_APD"
MODE = "ELD"
EVENT_IDF_FILENAME = "/mnt/data/idf/%s.json" % (NAME if NAME.endswith("_APD") else "%s_APD" % NAME)

if True and os.path.isfile(EVENT_IDF_FILENAME):
	with open(EVENT_IDF_FILENAME, "r") as f:
		idf = json.loads(f.readline())
	logger.info("IDF loaded with %d documents" % idf["DOCUMENTS"])

tokenizer = Tokenizer(stopwords=stopwords.words("english"), normalize_words=True, character_normalization_count=3, remove_unicode_entities=True)
summarizer = mamo_graph.DocumentGraphSummarizer(scorer=tweet_scorer.TweetScorer, tokenizer=tokenizer, scheme=TFIDF(idf))
with open("/home/memonick/output/temp/%s_%s_timeline.json" % (NAME, MODE), "r") as f:
	last_timestamp = 0
	for line in f:
		if len(summarizer._frozen_summaries) < 28:
			data = json.loads(line)
			terms, timestamp = data["terms"], data["timestamp"]
			cluster = Cluster.from_array(data["cluster"])

			summarizer.add_cluster(cluster, terms, timestamp)

	# summarizer.ping(last_timestamp)


for f in os.listdir("/home/memonick/output/process"):
    os.remove("/home/memonick/output/process/%s" % f)

cleaner = tweet_cleaner.TweetCleaner()
summary = summarizer._frozen_summaries[19]
i = 0

clusters = summary[0]
clusters = clusters if type(clusters) == list else [clusters]
for _, cluster in clusters:
	for document in cluster.get_vectors():
		with open("/home/memonick/output/process/%d" % (i), "w") as f:
			f.write(cleaner.clean(document.get_text()))
			i += 1
