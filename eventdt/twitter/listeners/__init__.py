"""
Listeners are used to download corpora in real-time.
These classes automatically connect to the APIs to fetch tweets based on a number of parameters.
"""

from .tweet_listener import TweetListener
from .queued_tweet_listener import QueuedTweetListener
