"""
Functions to aggregate Twitter corpora.
This can be used to create volume time-series, for example.
Other aggregation functions can be provided.
"""

def aggregate(corpus, bin_size=60, skip_bins=0, track=None, aggregation=volume):
	"""

	:param corpus: The file handle containing the data.
    :type corpus: ?
    :param bin_size: The length in seconds of each time window.
    :type bin_size: int
    :param skip_bins: The number of bins to skip.
					  If a negative number is provided, no bins are skipped.
    :type skip_bins: int
    :param track: The keywords to track.
                  If it is not None, only documents mentioning the keyword are counted.
    :type track: None, str or list of str
	:param aggregation: The aggregation function to use.
						Defaults to simple volume.
	:type aggregation: func

	:return: The tweets in the corpus aggregated into bins.
    :rtype: dict
	"""

	pass

def volume(bin):
	"""
	Count the number of documents in the given bin.

	:param bin: A bin containing a list of tweets published at that time.
	:type bin: list of dict

	:return: The number of tweets in the bin.
	:rtype: int
	"""

	return list(bin)
