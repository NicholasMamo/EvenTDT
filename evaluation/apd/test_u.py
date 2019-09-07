"""
Parse the squad list and print out player names as a list that can be copy-pasted into a Python script.

Requires one argument to function - the name of the source in the 'original' folder.
"""

import json
import os
import re
import sys
import urllib.parse

path = os.path.dirname(__file__)
path = os.path.join(path, "../../libraries")
if path not in sys.path:
	sys.path.insert(1, path)

from nltk.corpus import stopwords, words

from apd.participant_detector import ParticipantDetector
from apd.extractors.local.token_extractor import TokenExtractor
from apd.extrapolators.extrapolator import Extrapolator
from apd.postprocessors.postprocessor import Postprocessor
from apd.resolvers.local.entity_resolver import EntityResolver
from apd.resolvers.local.token_resolver import TokenResolver
from apd.scorers.local.idf_scorer import IDFScorer
from apd.scorers.local.sum_scorer import LogSumScorer, SumScorer

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer
from vector.nlp.term_weighting import TF, TFIDF
from vector.nlp.cleaners import tweet_cleaner

from logger import logger

if len(sys.argv) == 3:
	"""
	Load the text.
	"""
	filename, limit = sys.argv[1:3]
	limit = int(limit)

	cleaner = tweet_cleaner.TweetCleaner()
	with open(os.path.join("/home/memonick/data/idf.json"), "r") as idf_file:
		general_idf = json.loads(idf_file.readline())
		tokenizer = Tokenizer(stopwords=stopwords.words("english"),
			normalize_words=True,
			character_normalization_count=3,
			remove_unicode_entities=True)
		term_weighting = TFIDF(general_idf)

		corpus = []
		with open("/mnt/data/twitter/%s" % filename, "r") as f:
			count = 0
			for tweet in f:
				tweet = json.loads(tweet)
				if "retweeted_status" in tweet and "quoted_status" not in tweet:
					text = tweet["retweeted_status"].get("extended_tweet", {}).get("full_text", tweet.get("text", ""))
				else:
					text = tweet.get("text", "")

				print(cleaner.clean(text))

				count = count + 1
				if count > limit:
					break

else:
	logger.error("File name or limit not specified")
