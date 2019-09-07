"""
Functions to process tweets.
"""

from datetime import datetime, timedelta

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

def get_timestamp(tweet):
	"""
	Get the timestamp from the given tweet.

	:param tweet: The tweet being considered.
	:type tweet: dict

	:return: The timestamp of the tweet.
	:rtype: int
	"""

	year = tweet[-4:] # the year is the last four digits
	offset = tweet[-10:-5] # the utc offset

	dt = tweet[:-11] + " " + year # construct the date object

	dt = datetime.strptime(dt, "%a %b %d %H:%M:%S %Y") # parse the date

	"""
	Construct the timezone offset
	"""
	timezone_offset = int(offset[-4:-2]) * 60 + int(offset[-2:])
	timezone_offset = -timezone_offset if (offset[0] == '-') else timezone_offset
	dt -= timedelta(minutes=timezone_offset) # if the offset is positive, make it negative, and vice versa

	"""
	Get the timestamp
	"""
	start = datetime(1970, 1, 1)
	delta = dt - start
	timestamp = int(delta.total_seconds())
	return timestamp
