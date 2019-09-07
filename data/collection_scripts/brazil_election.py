"""
Collect a dataset for the event, using the list of keywords to track it
"""

BASE_NAME = "brazil_election.json"
SEED_SET = ["brazil election", "brasil election"]

# script output/brazil_election.txt -c 'python3 /home/memonick/data/brazil_election.py'
FILENAME = "/mnt/data/brazil/normal/%d_%s"
EVENT_DURATION = 3600
WINDOWS = 18
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

logger.info("Listening for keywords: %s" % ', '.join(SEED_SET))
for i in range(0, WINDOWS):
	with open(FILENAME % (i + 1, BASE_NAME), "w") as f:
		"""
		Listen to the new stream and save to file.
		"""
		l = TweetListener(f, max_time=EVENT_DURATION, silent=True)
		stream = Stream(auth, l)
		stream.filter(track=SEED_SET, languages=["en"])
