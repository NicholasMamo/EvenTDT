"""
Collect a dataset for the event, using the list of keywords to track it
"""

FILENAME = "/home/memonick/data/twitter/test.json"
EVENT_DURATION = 60
KEYWORDS = ["aretha"]

from datetime import datetime
import globals
import json
import time
from twevent.listener import *

from tweepy import OAuthHandler
from tweepy import Stream

with open(FILENAME, "w") as f:
	l = FilteredTweetListener(f, ["text"], max_time=EVENT_DURATION, silent=False)
	auth = OAuthHandler(globals.CONSUMER_KEY, globals.CONSUMER_SECRET)
	auth.set_access_token(globals.ACCESS_TOKEN, globals.ACCESS_TOKEN_SECRET)

	stream = Stream(auth, l)
	stream.filter(track=KEYWORDS)
	# stream.sample()
