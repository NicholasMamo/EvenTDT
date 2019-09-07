"""
Collect a dataset for the event, using the list of keywords to track it
"""

BASE_NAME = "RiverBoca_FUL.json"
SEED_SET = ["#RiverBoca", "Libertadores", "River", "Boca"]

PARTICIPANTS = ["Santiago Bernabéu Stadium", "Marcelo Gallardo", "Guillermo Barros Schelotto",
	'Franco Armani', 'Gonzalo Montiel', 'Jonatan Maidana', 'Javier Pinola', 'Milton Casco',
	'Leonardo Ponzio',
	'Ignacio Fernández (footballer)', 'Enzo Pérez', 'Exequiel Palacios', 'Gonzalo Nicolás Martínez',
	'Lucas Pratto',
	'Julián Álvarez (footballer)', 'Lucas Martínez Quarta', 'Bruno Zuculini', 'Juan Fernando Quintero', 'Camilo Mayada', 'Rodrigo Mora', 'Germán Lux',

	'Esteban Andrada', 'Julio Buffarini', 'Carlos Izquierdoz', 'Lisandro Magallán', 'Lucas Olaza',
	'Nahitan Nández', 'Pablo Pérez', 'Wilmar Barrios', 'Cristian Pavón',
	'Sebastián Villa Cano', 'Darío Benedetto',
	'Leonardo Jara', 'Agustín Rossi (footballer)', 'Ramón Ábila', 'Paolo Goltz', 'Mauro Zárate', 'Fernando Gago', 'Carlos Tevez',
]

FILENAME = "/mnt/data/twitter/%s" % (BASE_NAME)
EVENT_DURATION = 3600 * 3.5
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
