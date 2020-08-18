"""
Aggregation functions are quick solutions to group tweets.
These can be used to create tweet volume time-series quickly, for example.
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
	Aggregate the given corpus, binning the tweets according to the when they were published.
	The tracking keywords as well as any other arguments or keyword arguments are passed on to the aggregation function.

	The function is data-agnostic in terms of whether it receives tweets or not.
	However in order to bin tweets, the function expects that there is a ``timestamp_ms`` or ``created_at`` attribute in each object.

	In addition, the aggregation function needs to be specified using the ``agg`` parameter.
	Aggregation functions receive as input:

	- A list of tweets as dictionaries, and
	- The keyword which is being aggregated.

	They return a value, or a score for the keyword's bin at a particular timestamp.
	For example, a simple volume-based aggregation function could look like the following:

	.. code-block:: python

		def volume(tweets, keyword=None, *args, **kwargs):
		  \"""
		  Count the number of tweets that mention the given keyword.
		  If no keyword is given, all tweets are counted.

		  :param tweets: The list of tweets in the bin.
		  :type tweets: list of dict
		  :param keyword: The keyword to consider.
		  				  The function looks for the keyword in the text.
						  If no keyword is given, the number of tweets is returned.
		  :type keyword: str or None

		  :return: The number of tweets that mention the given keyword.
		           If no keyword is given, the number of tweets is returned.
		  :rtype: int
		  \"""

		  if keyword:
		    return len([ tweet for tweet in tweets
		                       if keyword in tweet['text'] ])
		    else:
		      return len(tweets)

	The aggregation function vary depending on the application.
	However, the return value must always be a float or an integer.

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
