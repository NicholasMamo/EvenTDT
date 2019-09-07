"""
Collect a dataset for the event, using the list of keywords to track it
"""

BASE_NAME = "MUNBOU_FUL.json"
SEED_SET = ["#MUNBOU", "Manchester United", "Bournemouth"]

PARTICIPANTS = [
	"Old Trafford", "Ole Gunnar Solskjær", "Eddie Howe",

	'David de Gea', 'Ashley Young', 'Phil Jones (footballer, born 1992)', 'Victor Lindelöf', 'Luke Shaw',
	'Ander Herrera', 'Paul Pogba', 'Nemanja Matić',
	'Jesse Lingard', 'Marcus Rashford', 'Anthony Martial',

	'Lee Grant (footballer, born 1983)', 'Scott McTominay', 'Juan Mata', 'Eric Bailly', 'Marcos Rojo',
	'Marouane Fellaini', 'Fred (footballer, born 1993)', 'Sergio Romero', 'Diogo Dalot', 'Antonio Valencia',
	'Alexis Sánchez', 'Romelu Lukaku',

	'Asmir Begović', 'Steve Cook', 'Tyrone Mings', 'Nathan Aké', 'Charlie Daniels (footballer)',
	'David Brooks (footballer)', 'Andrew Surman', 'Jefferson Lerma', 'Ryan Fraser',
	'Joshua King (footballer)',
	'Callum Wilson (English footballer)',

	'Artur Boruc', 'Aaron Ramsdale', 'Jack Simpson (footballer)', 'Lys Mousset', 'Marc Pugh',
	'Jermain Defoe', 'Kyle Taylor', 'Junior Stanislas', 'Jordon Ibe', 'Diego Rico',

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
PARTICIPANTS = postprocessor.postprocess(PARTICIPANTS, [], postprocessor_surname_only=True, force_retain=True)
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
