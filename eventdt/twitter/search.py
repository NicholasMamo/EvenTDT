"""
Collect a dataset for the event, using the list of keywords to track it
"""

KEYWORDS = ["from:@AshaRangappa_"]

from datetime import datetime
import globals
import json
import time

from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

ids = []
auth = OAuthHandler(globals.CONSUMER_KEY, globals.CONSUMER_SECRET)
auth.set_access_token(globals.ACCESS_TOKEN, globals.ACCESS_TOKEN_SECRET)

api_obj = API(auth)

tweets = api_obj.search(' '.join(KEYWORDS))
for tweet in tweets[:100]:
	print(tweet.text)
