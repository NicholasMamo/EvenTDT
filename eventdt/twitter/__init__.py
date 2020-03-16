"""
Functions to process tweets.
"""

def extract_timestamp(tweet):
	"""
	Get the timestamp from the given tweet.

	:param tweet: The tweet being considered.
	:type tweet: dict

	:return: The timestamp of the tweet.
	:rtype: int
	"""

	timestamp_ms = int(tweet["timestamp_ms"])
	timestamp_ms = timestamp_ms - timestamp_ms % 1000
	return timestamp_ms / 1000.
