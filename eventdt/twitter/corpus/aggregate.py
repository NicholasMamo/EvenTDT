"""
Functions to aggregate Twitter corpora.
This can be used to create volume time-series, for example.
Other aggregation functions can be provided.
"""

def aggregate(corpus, bin_size=60, skip_bins=0, track=None):
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

	:return: The tweets in the corpus aggregated into bins.
    :rtype: dict
	"""

	pass
