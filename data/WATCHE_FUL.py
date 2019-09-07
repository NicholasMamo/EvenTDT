"""
Collect a dataset for the event, using the list of keywords to track it
"""

BASE_NAME = "WATCHE_FUL.json"
SEED_SET = ["#WATCHE", "Watford", "Chelsea"]

PARTICIPANTS = ["Vicarage Road", "Javi Garcia", "Maurizio Sarri",
	'Kepa Arrizabalaga', 'César Azpilicueta', 'Antonio Rüdiger', 'David Luiz', 'Marcos Alonso Mendoza',
	'N\'Golo Kanté', 'Jorginho (footballer, born 1991)', 'Mateo Kovačić',
	'Willian (footballer, born 1988)', 'Eden Hazard', 'Pedro (footballer, born 1987)',
	'Cesc Fàbregas', 'Ross Barkley', 'Willy Caballero', 'Olivier Giroud', 'Callum Hudson-Odoi', 'Gary Cahill', 'Emerson Palmieri',

	'Ben Foster (footballer)', 'Kiko Femenía', 'Christian Kabasele', 'Craig Cathcart', 'José Holebas',
	'Abdoulaye Doucouré', 'Étienne Capoue',
	'Ken Sema', 'Roberto Pereyra',
	'Gerard Deulofeu', 'Troy Deeney',
	'Heurelho Gomes', 'Adrian Mariappa', 'Tom Cleverley', 'Isaac Success', 'Adam Masina', 'Domingos Quina', 'Stefano Okaka',
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
