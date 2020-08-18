"""
The Twitter package is used to facilitate collecting, reading and processing tweet corpora.
At the package-level there are functions to help with general processing tasks.
"""

from dateutil.parser import parse

def extract_timestamp(tweet):
	"""
	Get the timestamp from the given tweet.
	This function looks for the timestamp in one of two fields:

	1. ``timestamp_ms``: always present in the top-level tweets, and
	2. ``created_at``: present in `retweeted_status`, for example.

	:param tweet: The tweet from which to extract the timestamp.
	:type tweet: dict

	:return: The timestamp of the tweet.
	:rtype: int

	:raises KeyError: When no timestamp field can be found.
	"""

	if 'timestamp_ms' in tweet:
		timestamp_ms = int(tweet["timestamp_ms"])
		timestamp_ms = timestamp_ms - timestamp_ms % 1000
		return timestamp_ms / 1000.
	elif 'created_at' in tweet:
		return parse(tweet['created_at']).timestamp()

	raise KeyError("Neither the 'timestamp_ms' attribute, nor the 'created_at' attribute could be found in the tweet.")
