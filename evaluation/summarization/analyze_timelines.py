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
	NAME = sys.argv[1]
	TDT = "ELD"

	with open("%s/%s_raw.json" % (RAW_DIR, NAME), "r") as f:
		"""
		Prepare the output directory.
		"""

		for development, line in enumerate(f):
			"""
			Load the documents.
			"""
			data = json.loads(line)
			clusters = [ Cluster.from_array(cluster["cluster"]) for cluster in data["clusters"] ]
			documents = [ document for cluster in clusters for document in cluster.get_vectors() ]
			first_document = clusters[0].get_vectors()[1]
			documents = sorted(documents, key = lambda x: int(x.get_attribute("timestamp")))
			average_publication_time = sum([ document.get_attribute("timestamp") for document in documents ])/len(documents)
			extremes = (average_publication_time - documents[0].get_attribute("timestamp"), documents[-1].get_attribute("timestamp") - average_publication_time)
			extremes = (extremes[0]/60., extremes[1]/60.)

			far_documents = [ document for document in documents if (document.get_attribute("timestamp") - average_publication_time)/60. > 5 ]
			distances = [ (document.get_attribute("timestamp") - average_publication_time)/60. for document in far_documents]
			if len(distances) > 5:
				average_distance = sum(distances)/len(distances)
				if average_distance > 5:
					print("%s: %.4f %.4f" % (
					datetime.fromtimestamp(int(first_document.get_attribute("timestamp"))).strftime('%Y-%m-%d %H:%M:%S'),
					len(far_documents)/len(documents), average_distance))

			# difference = (documents[-1].get_attribute("timestamp") - first_document.get_attribute("timestamp"))/60.
			# differences_from_first = [ (document.get_attribute("timestamp") - first_document.get_attribute("timestamp"))/60. for document in documents[1:] ]
			# average_difference = sum(differences_from_first)/len(differences_from_first)
			# if difference > 3:
			# 	pass
			# 	# print("Max difference in %d: %.2f minutes" % (development + 1, difference))
			#
			# diff = 5
			# if average_difference > diff:
			# 	# print("Avg difference in %d: %.2f minutes" % (development + 1, average_difference))
			# 	# print(first_document.get_text().replace("\n", " "))
			# 	# print(documents[-1].get_text().replace("\n", " "))
			# 	offending = [ difference for difference in differences_from_first if difference > diff ]
			# 	print("%s: %d/%d offending documents" % (
			# 		datetime.fromtimestamp(documents[0].get_attribute("timestamp")).strftime('%Y-%m-%d %H:%M:%S'),
			# 		len(offending), len(documents)))
			# 	# print()
