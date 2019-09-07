"""
Collect a dataset for the event, using the list of keywords to track it
"""

BASE_NAME = "JuventusInter_FUL.json"
SEED_SET = ["#JuveInter", "Juventus", "Inter"]

PARTICIPANTS = ["Juventus Stadium", "Massimiliano Allegri", "Luciano Spalletti",
	'Wojciech Szczęsny', 'Mattia De Sciglio', 'Leonardo Bonucci', 'Giorgio Chiellini', 'João Cancelo',
	'Rodrigo Bentancur', 'Miralem Pjanić', 'Blaise Matuidi',
	'Paulo Dybala', 'Mario Mandžukić', 'Cristiano Ronaldo',
	'Mehdi Benatia', 'Douglas Costa', 'Juan Cuadrado', 'Carlo Pinsoglio', 'Mattia Perin', 'Emre Can', 'Daniele Rugani', 'Federico Bernardeschi', 'Leonardo Spinazzola',

	'Samir Handanović', 'Šime Vrsaljko', 'Milan Škriniar', 'Miranda (footballer)', 'Kwadwo Asamoah',
	'Roberto Gagliardini', 'Marcelo Brozović', 'João Mário (Portuguese footballer)',
	'Matteo Politano', 'Mauro Icardi', 'Ivan Perišić',
	'Stefan de Vrij', 'Matías Vecino', 'Lautaro Martinez',  'Keita Baldé', 'Andrea Ranocchia', 'Borja Valero', 'Daniele Padelli', 'Danilo D\'Ambrosio', 'Antonio Candreva',
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
