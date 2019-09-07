"""
Collect a dataset for the event, using the list of keywords to track it
"""

FILENAME = "/home/memonick/data/twitter/ARSEVE.json"
EVENT_DURATION = 60*60*3.25
KEYWORDS = ["#ARSEVE", "#EVEARS", "#ARS", "#EVE", "Arsenal", "Everton"]

from datetime import datetime
import json
import time
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))

from twitter import globals
from twitter.twevent.listener import *

from tweepy import OAuthHandler
from tweepy import Stream

with open(FILENAME, "w") as f:
	l = TweetListener(f, max_time=EVENT_DURATION)
	auth = OAuthHandler(globals.CONSUMER_KEY, globals.CONSUMER_SECRET)
	auth.set_access_token(globals.ACCESS_TOKEN, globals.ACCESS_TOKEN_SECRET)

	stream = Stream(auth, l)
	stream.filter(track=KEYWORDS, languages=["en"])
	# stream.sample()
