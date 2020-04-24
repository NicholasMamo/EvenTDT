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

def volume(bin, track=None, *args, **kwargs):
	"""
	Count the number of documents in the given bin.
	If a tracking keyword is given, the function returns the number of documents in which the keyword appears.
	The function looks for the keyword in the dimensions.

	:param bin: A bin containing a list of documents to count.
	:type bin: list of :class:`~nlp.document.Document`
	:param track: The keyword to track.
	:type track: None or str

	:return: The number of documents in the bin.
			 If a tracking keyword is given, the function counts the number of documents in the bin that contain the keyword.
	:rtype: int
	"""

	if track:
		return len([ document for document in bin if track.lower() in document.dimensions ])
	else:
		return len(bin)

def to_documents(tweets, tokenizer, scheme=None):
	"""
	Convert the given tweets into documents.

	:param tweets: A list of tweets.
	:type tweets: list of dict
	:param tokenizer: The tokenizer used to create documents from tweets.
	:type tokenizer: :class:`~nlp.tokenizer.Tokenizer`
	:param scheme: The term-weighting scheme that is used to create dimensions.
				   If `None` is given, the :class:`~nlp.term_weighting.tf.TF` term-weighting scheme is used.
	:type scheme: None or :class:`~nlp.term_weighting.scheme.TermWeightingScheme`

	:return: A list of documents created from the tweets in the same order as the given tweets.
			 Documents are normalized and store the original tweet in the `tweet` attribute.
	:rtype: list of :class:`~nlp.document.Document`
	"""

	documents = [ ]

	"""
	The text used for the document depend on what kind of tweet it is.
	If the tweet is too long to fit in the tweet, the full text is used;

	Retain the comment of a quoted status.
	However, if the tweet is a plain retweet, get the full text.
	"""
	for tweet in tweets:
		original = tweet
		while "retweeted_status" in tweet:
			tweet = tweet["retweeted_status"]

		if "extended_tweet" in tweet:
			text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
		else:
			text = tweet.get("text", "")

		"""
		Create the document and save the tweet in it.
		"""
		tokens = tokenizer.tokenize(text)
		document = Document(text, tokens, scheme=scheme)
		document.attributes['tweet'] = original
		document.normalize()
		documents.append(document)

	return documents

def aggregate(corpus, bin_size=60, aggregation=volume, track=None, tokenizer=None, scheme=None, *args, **kwargs):
	"""
	Aggregate the given corpus.
	The tracking keywords as well as any other arguments or keyword arguments are passed on to the aggregation function.

	:param corpus: The file handle containing the data.
    :type corpus: :class:`_io.TextIOWrapper`
    :param bin_size: The length in seconds of each time window.
    :type bin_size: int
	:param aggregation: The aggregation function to use.
						Defaults to simple volume.
	:type aggregation: func
    :param track: The keywords to aggregate.
                  If it is not None, only documents containing the keyword are considered in the aggregation.
    :type track: None, str or list of str
	:param tokenizer: The tokenizer used to create documents from tweets.
	:type tokenizer: :class:`~nlp.tokenizer.Tokenizer`
	:param scheme: The term-weighting scheme that is used to create dimensions.
				   If `None` is given, the :class:`~nlp.term_weighting.tf.TF` term-weighting scheme is used.
	:type scheme: None or :class:`~nlp.term_weighting.scheme.TermWeightingScheme`

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
	tokenizer = tokenizer or Tokenizer()

	"""
	Go through each line to count the documents.
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
			documents = to_documents(bin, tokenizer)
			for tweet, document in zip(bin, documents):
				document.attributes['tweet'] = tweet

			bins[current_time_window] = bins.get(current_time_window, { })
			bins[current_time_window]['*'] =  bins[current_time_window].get('*', 0) + aggregation(documents, *args, **kwargs)
			if track:
				for keyword in track:
					bins[current_time_window][keyword] =  bins[current_time_window].get(keyword, 0) + aggregation(documents, keyword, *args, **kwargs)

			"""
			Finally, reset the records.
			"""
			bin = [ ]
			current_time_window = time_window

		bin.append(tweet)

	"""
	Finalize the aggregation with any last tweets that have not been committed.
	"""
	documents = to_documents(bin, tokenizer)
	for tweet, document in zip(bin, documents):
		document.attributes['tweet'] = tweet
	
	bins[current_time_window] = bins.get(current_time_window, { })
	bins[current_time_window]['*'] =  bins[current_time_window].get('*', 0) + aggregation(documents, *args, **kwargs)
	if track:
		for keyword in track:
			bins[current_time_window][keyword] =  bins[current_time_window].get(keyword, 0) + aggregation(documents, keyword, *args, **kwargs)

	return bins
