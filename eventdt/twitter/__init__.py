"""
Functions to process tweets.
"""

from dateutil.parser import parse

def extract_timestamp(tweet):
	"""
	Get the timestamp from the given tweet.
	This function looks for the timestamp in one of two fields:

	1. `timestamp_ms` - present in top-level fields, and
	2. `created_at` - present in `retweeted_status`, for example.

	:param tweet: The tweet being considered.
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

	raise KeyError("Neither 'timestamp_ms' nor 'created_at' could be found in the tweet.")
