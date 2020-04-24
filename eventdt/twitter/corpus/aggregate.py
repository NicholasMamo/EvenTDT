"""
Functions to aggregate Twitter corpora.
This can be used to create volume time-series, for example.
Other aggregation functions can be provided.
"""

def aggregate(corpus, bin_size=60, skip_bins=0, track=None, aggregation=volume):
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp.document import Document
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
