"""
Collect a dataset for the event, using the list of keywords to track it
"""

BASE_NAME = "LIVMUN_FUL.json"
SEED_SET = ["#LIVMUN", "Liverpool", "Manchester United"]

PARTICIPANTS = ["Anfield", "Jürgen Klopp", "José Mourinho",
	'Alisson (footballer, born 1992)', 'Nathaniel Clyne', 'Dejan Lovren', 'Virgil van Dijk', 'Andrew Robertson (footballer)',
	'Fabinho (footballer, born 1993)', 'Georginio Wijnaldum', 'Naby Keïta',
	'Mohamed Salah', 'Roberto Firmino', 'Sadio Mané',
	'Simon Mignolet', 'Jordan Henderson', 'Daniel Sturridge', 'Alberto Moreno', 'Adam Lallana', 'Xherdan Shaqiri', 'Rafael Camacho',

	'David de Gea', 'Diogo Dalot', 'Chris Smalling', 'Victor Lindelöf', 'Matteo Darmian',
	'Ander Herrera', 'Nemanja Matic',
	'Marcus Rashford', 'Jesse Lingard', 'Ashley Young', 'Romelu Lukaku',
	'Sergio Romero', 'Eric Bailly', 'Antonio Valencia', 'Marouane Fellaini', 'Juan Mata', 'Paul Pogba', 'Anthony Martial',
	]

FILENAME = "/mnt/data/twitter/%s" % (BASE_NAME)
EVENT_DURATION = 3600 * 2.5
IDF = "idf.json"

from datetime import datetime
from nltk.corpus import stopwords, words

from collection_functions import *

import json
import time
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))

from apd.postprocessors.external.wikipedia_postprocessor import WikipediaPostprocessor

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

postprocessor = WikipediaPostprocessor()
PARTICIPANTS = postprocessor.postprocess(PARTICIPANTS, [], postprocessor_surname_only=True)
print(PARTICIPANTS)
SEED_SET = SEED_SET + PARTICIPANTS

with open(FILENAME, "w") as f:
	auth = OAuthHandler(globals.ALT_CONSUMER_KEY, globals.ALT_CONSUMER_SECRET)
	auth.set_access_token(globals.ALT_ACCESS_TOKEN, globals.ALT_ACCESS_TOKEN_SECRET)

	"""
	Listen to the new stream and save to file.
	"""
	l = TweetListener(f, max_time=EVENT_DURATION, silent=True)
	stream = Stream(auth, l)
	logger.info("Listening for keywords: %s" % ', '.join(SEED_SET))
	stream.filter(track=SEED_SET, languages=["en"])
