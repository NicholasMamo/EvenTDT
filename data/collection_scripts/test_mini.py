"""
Collect a dataset for the event, using the list of keywords to track it
"""

BASE_NAME = "test_apd_collector.json"
SEED_SET = ["manchester united"]

UNDERSTANDING_FILENAME = "/home/memonick/data/twitter/u_%s" % (BASE_NAME)
FILENAME = "/home/memonick/data/twitter/%s" % (BASE_NAME)
UNDERSTANDING_PERIOD = 60
EVENT_DURATION = 120
IDF = "idf.json"

from datetime import datetime
from nltk.corpus import words

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

with open(FILENAME, "w") as f:
	auth = OAuthHandler(globals.CONSUMER_KEY, globals.CONSUMER_SECRET)
	auth.set_access_token(globals.ACCESS_TOKEN, globals.ACCESS_TOKEN_SECRET)

	l = TweetListener(f, max_time=EVENT_DURATION, silent=True)
	stream = Stream(auth, l)

	keywords = [
		'List of European Cup and UEFA Champions League winning some']
	print(keywords)
	stream.filter(track=keywords, languages=["en"])
