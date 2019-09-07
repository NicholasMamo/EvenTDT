"""
Collect a dataset for the event, using the list of keywords to track it
"""

BASE_NAME = "midterms_apd"
SEED_SET = ["#MidtermElections2018", "#ElectionDay", "#ElectionNight", "midterm"]

# script output/midterm_election_usa_apd.txt -c 'python3 /home/memonick/data/midterm_election_usa_apd.py'
UNDERSTANDING_FILENAME = "/mnt/data/midterms/apd/u_%s.json" % (BASE_NAME)
FILENAME = "/mnt/data/midterms/apd/%d_%s.json"
PARTICIPANT_OUTPUT = "/mnt/data/midterms/apd/0_%s.txt" % (BASE_NAME)
UNDERSTANDING_PERIOD = 3600 * 2./6.
EVENT_DURATION = 1800
WINDOWS = 36
IDF = "idf.json"

from datetime import datetime
from nltk.corpus import stopwords, words

from collection_functions import *

import json
import time
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))

from logger import logger

from queues.queue.queue import Queue

from twitter import globals
from twitter.twevent.listener import TweetListener
from twitter.twevent.queued_listener import QueuedListener

from vector.nlp.cleaners import tweet_cleaner
from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer
from vector.nlp.term_weighting import TF, TFIDF

from tweepy import OAuthHandler
from tweepy import Stream

auth = OAuthHandler(globals.CONSUMER_KEY, globals.CONSUMER_SECRET)
auth.set_access_token(globals.ACCESS_TOKEN, globals.ACCESS_TOKEN_SECRET)

queue = Queue()
l = QueuedListener(queue, max_time=UNDERSTANDING_PERIOD)
stream = Stream(auth, l)
logger.info("Listening for keywords: %s" % ', '.join(SEED_SET))
stream.filter(track=SEED_SET, languages=["en"])

"""
Create the corpus. It is built with NER in mind.
"""
with open(os.path.join("/home/memonick/data", IDF), "r") as idf_file:
	general_idf = json.loads(idf_file.readline())
	tokenizer = Tokenizer(stopwords=stopwords.words("english"),
		normalize_words=True,
		character_normalization_count=3,
		remove_unicode_entities=True)

	"""
	Save the tweets received for understanding.
	"""
	data = queue.dequeue_all()
	with open(UNDERSTANDING_FILENAME, "w") as understanding_file:
		for tweet in data:
			understanding_file.write("%s\n" % json.dumps(tweet))

	"""
	Create the corpus of documents.
	"""
	logger.info("%d tweets collected" % len(data))
	corpus = [] # the corpus of documents
	term_weighting = TFIDF(general_idf)
	for tweet in data:
		if "retweeted_status" in tweet and "quoted_status" not in tweet:
			text = tweet["retweeted_status"].get("extended_tweet", {}).get("full_text", tweet.get("text", ""))
		else:
			text = tweet.get("text", "")
		tokens = tokenizer.tokenize(text)
		document = Document(text, dimensions=tokens, attributes={ "tokens": tokens, "text": text, "tweet": tweet }, scheme=term_weighting)
		document.normalize()
		corpus.append(document)

	"""
	Find the participants from the stream and extrapolate them.
	These are used to create the new tracking keyword set.
	"""
	resolved, extrapolated = detect_participants(corpus, general_idf, [ keyword for keyword in SEED_SET if all(c.isalpha() or c.isspace() for c in keyword) ])
	keywords = SEED_SET + resolved + extrapolated
	keywords = [ keyword[:59] for keyword in keywords ]

with open(PARTICIPANT_OUTPUT, "w") as f:
	logger.info("Resolved keywords: %s" % ', '.join(resolved))
	f.write("Resolved keywords:\n\t%s\n\n" % '\n\t'.join(resolved))

	logger.info("Extrapolated keywords: %s" % ', '.join(extrapolated))
	f.write("Extrapolated keywords:\n\t%s\n\n" % '\n\t'.join(extrapolated))

	logger.info("Listening for keywords: %s" % ', '.join(keywords))
	f.write("Listening for keywords:\n\t%s\n\n" % '\n\t'.join(keywords))

logger.info("Listening to %d windows" % WINDOWS)

for i in range(0, WINDOWS):
	with open(FILENAME % (i + 1, BASE_NAME), "w") as f:
		"""
		Listen to the new stream and save to file.
		"""
		logger.info("Window %d starting" % (i + 1))
		l = TweetListener(f, max_time=EVENT_DURATION, silent=True)
		stream = Stream(auth, l)
		stream.filter(track=keywords, languages=["en"])
		logger.info("Window %d completed" % (i + 1))
