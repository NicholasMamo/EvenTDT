"""
Functions to aggregate Twitter corpora.
This can be used to create volume time-series, for example.
Other aggregation functions can be provided.
"""

import json
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
from nlp.tokenizer import Tokenizer
import twitter

def aggregate(corpus, agg, bin_size=60, track=None, *args, **kwargs):
	"""
	Aggregate the given corpus.
	The tracking keywords as well as any other arguments or keyword arguments are passed on to the aggregation function.

	The function is data-agnostic in terms of whether it receives tweets or not.
	However in order to bin tweets, the function expects that there is a `timestamp_ms` or `created_at` attribute in each object.

	:param corpus: The file handle containing the data.
    :type corpus: :class:`_io.TextIOWrapper`
	:param agg: The aggregation function to use.
	:type agg: function
	:param bin_size: The length in seconds of each time window.
	:type bin_size: int
    :param track: The keywords to aggregate.
                  If it is not None, only documents containing the keyword are considered in the aggregation.
    :type track: None, str or list of str

	:return: The tweets in the corpus aggregated into time windows.
			 The time windows have keys that correspond to the tracking keywords.
			 Moreover, they have an extra key that corresponds to the aggregation of all tweets, named `*`.
    :rtype: dict
	"""

	bins = { }

	"""
	Convert the tracking keywords into a list.
	"""
	track = [ track ] if type(track) is str else track
	track = track or [ ]

	"""
	Go through each line to aggregate the tweets.
	"""
	bin = []
	current_time_window = None
	for line in corpus:
		tweet = json.loads(line)

		"""
		Find the time window of the document.
		"""
		timestamp = twitter.extract_timestamp(tweet)
		time_window = timestamp - timestamp % bin_size if bin_size > 0 else 0
		current_time_window = current_time_window or time_window

		if time_window != current_time_window:
			"""
			If the time window is over, process the tweets.
			"""
			bins[current_time_window] = bins.get(current_time_window, { })
			bins[current_time_window]['*'] =  bins[current_time_window].get('*', 0) + agg(bin, *args, **kwargs)
			if track:
				for keyword in track:
					bins[current_time_window][keyword] =  bins[current_time_window].get(keyword, 0) + agg(bin, keyword, *args, **kwargs)

			"""
			Finally, reset the records.
			"""
			bin = [ ]
			current_time_window = time_window

		bin.append(tweet)

	"""
	Finalize the aggregation with any last tweets that have not been committed.
	"""
	bins[current_time_window] = bins.get(current_time_window, { })
	bins[current_time_window]['*'] =  bins[current_time_window].get('*', 0) + agg(bin, *args, **kwargs)
	if track:
		for keyword in track:
			bins[current_time_window][keyword] =  bins[current_time_window].get(keyword, 0) + agg(bin, keyword, *args, **kwargs)

	return bins
