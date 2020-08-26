"""
FUEGO (codename that means absolutely nothing) is a feature-pivot consumer built on the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`'s own feature-pivot method.
Differently from the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`, FUEGO uses a sliding time-window instead of checkpoints.
This allows for more accurate results in real-time.

.. note::

	Since FUEGO uses only a feature-pivot method, it is not very granular on its own.
	Therefore this consumer can only extract granular developments when combined with a :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer`.
	For a combination of document-pivot and feature-pivot approaches, see the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`.
"""

import os
import sys

from nltk.corpus import stopwords

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from nlp import Document, Tokenizer
from nlp.weighting import TF, TFIDF
from nlp.weighting.global_schemes import IDF
from queues.consumers import Consumer
from summarization.timeline import Timeline
from summarization.timeline.nodes import DocumentNode
import twitter

class FUEGOConsumer(Consumer):
	"""
	The :class:`~queues.consumers.fuego_consumer.FUEGOConsumer` is a real-time consumer with a custom algorithm to detect topics.
	Unlike other :ref:`consumers <consumers>`, the consumer has both a :func:`~queues.consumers.Consumer.ELDConsumer.run` and a :func:`~queues.consumers.fuego_consumer.FUEGOConsumer.understand` functions.
	The former is the normal processing step, whereas the :func:`~queues.consumers.fuego_consumer.FUEGOConsumer.understand` function precedes the event and builds a TF-IDF scheme for the event.

	In additional to the :class:`~queues.Queue`, the consumer maintains in its state one object to transform tweets into :class:`~nlp.document.Document` instances:

	- ``tokenizer``: used to tokenize the text in tweets.
	- ``scheme``: used to weight the tokens and create :class:`~nlp.document.Document` instances.

	:ivar ~.tokenizer: The tokenizer used to tokenize tweets.
	:vartype tokenizer: :class:`~nlp.tokenizer.Tokenizer`
	:ivar scheme: The term-weighting scheme used to create documents from tweets.
	:vartype scheme: :class:`~nlp.weighting.TermWeightingScheme`
	"""

	def __init__(self, queue, scheme=None, *args, **kwargs):
		"""
		Create the consumer with a queue.

		:param queue: The queue that will be receiving tweets.
					  The consumer reads tweets from this queue and processes them.
		:type queue: :class:`~queues.Queue`
		:param scheme: The term-weighting scheme used to create documents from tweets.
		:type scheme: :class:`~nlp.weighting.TermWeightingScheme`
		"""

		super(FUEGOConsumer, self).__init__(queue, *args, **kwargs)

		self.tokenizer = Tokenizer(stopwords=stopwords.words('english'),
								   normalize_words=True, character_normalization_count=3,
								   remove_unicode_entities=True)
		self.scheme = scheme or TF()

	async def understand(self, max_inactivity=-1, *args, **kwargs):
		"""
		Understanding precedes the event and is tasked with generating knowledge automatically.

		During understanding, the :class:`~queues.consumers.fuego_consumer.FUEGOConsumer` creates a :class:`~nlp.weighting.TermWeightingScheme` with an :class:`~nlp.weighting.global_schemes.idf.IDF` table based on the pre-event discussion.
		The consumer uses the :class:`~nlp.weighting.TermWeightingScheme` while processing tweets in real-time.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, it is ignored.
		:type max_inactivity: int

		:return: The :class:`~nlp.weighting.tfidf.TFIDF` scheme built from the documents from the pre-event tweets.
		:rtype: :class:`~nlp.weighting.tfidf.TFIDF`
		"""

		self._started()
		tfidf = await self._construct_idf(max_inactivity=max_inactivity)
		logger.info(f"TF-IDF constructed with { tfidf.global_scheme.documents } documents", process=str(self))
		self._stopped()
		return tfidf

	async def _construct_idf(self, max_inactivity):
		"""
		Construct the TF-IDF table from the pre-event discussion.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, it is ignored.
		:type max_inactivity: int

		:return: The constructed TF-IDF scheme.
		:rtype: :class:`~nlp.weighting.tfidf.TFIDF`
		"""

		idf = { }
		size = 0

		"""
		Understanding keeps working until it is stopped.
		"""
		while self.active:
			active = await self._wait_for_input(max_inactivity)
			if not active:
				break

			"""
			After it is stopped, construct the IDF.
			Get all the tweets in the queue and convert them to documents.
			"""
			tweets = self.queue.dequeue_all()
			documents = self._to_documents(tweets)
			size += len(documents)

			"""
			If there are documents, update the IDF with the consumed documents.
			These documents are also added to the buffer so they can be used by the APD process.
			"""
			if documents:
				subset = IDF.from_documents(documents)
				idf = { term: idf.get(term, 0) + subset.get(term, 0)
						for term in subset.keys() | idf.keys() }

		return TFIDF(idf, size)

	async def _consume(self, max_inactivity, *args, **kwargs):
		"""
		Consume and process the documents in the queue.

		:param max_inactivity: The maximum time in seconds to wait idly without input before stopping.
							   If it is negative, the consumer keeps waiting for input until the maximum time expires.
		:type max_inactivity: int

		:return: The constructed timeline.
		:rtype: :class:`~summarization.timeline.Timeline`
		"""

		timeline = Timeline(DocumentNode, expiry=90, min_similarity=0.6)

		return timeline

	def _filter_tweets(self, tweets):
		"""
		Filter the given tweets.
		The rules are based on :class:`~queues.consumers.algorithms.fire_consumer.FIREConsumer`'s and :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`'s filtering rules.

		:param tweets: A list of tweets to filter.
					   The tweets can either be tweet dictionaries or documents.
					   If they are documents, this function looks for the tweet in the ``tweet`` attribute.
		:type tweets: list of dict or list of :class:`~nlp.document.Document`

		:return: A list of filtered tweets.
		:type tweets: list of dict or list of :class:`~nlp.document.Document`
		"""

		filtered = [ ]

		for item in tweets:
			tweet = item.attributes['tweet'] if type(item) is Document else item
			if self._validate_tweet(tweet):
				filtered.append(item)

		return filtered

	def _validate_tweet(self, tweet):
		"""
		Filter the given tweet based on :class:`~.queues.consumers.fire_consumer.FIREConsumer`'s and :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`'s filtering rules.

		FIRE's rules are:

			#. The tweet has to be in English,

			#. The tweet must contain no more than 2 hashtags,

			#. The tweet's author must have favorited at least one tweet, and

			#. The tweet's author must have at least one follower for every thousand tweets they've published.

		ELD's rules are:

			#. The tweet cannot have more than one URL because too many URLs are indicative of pre-planned content, and

			#. The biography of the tweet's author cannot be empty because that is indicative of bots.

		:param tweet: The tweet to validate.
		:type tweet: dict

		:return: A boolean indicating whether the tweet passed the filtering test.
		:rtype: str
		"""

		if not tweet['lang'] == 'en':
			return False

		if len(tweet['entities']['hashtags']) > 2:
			return False

		if tweet['user']['favourites_count'] == 0:
			return False

		if tweet['user']['followers_count'] / tweet['user']['statuses_count'] < 1e-3:
			return False

		if len(tweet['entities']['urls']) > 1:
			return False

		if not tweet['user']['description']:
			return False

		return True

	def _to_documents(self, tweets):
		"""
		Convert the given tweets into documents.
		If the input is made up of documents, these are not changed, but the function adds additional attributes to them.

		:param tweets: A list of tweets.
		:type tweets: list of dict or list of :class:`~nlp.document.Document`

		:return: A list of documents created from the tweets in the same order as the given tweets.
				 Documents are normalized and contain the original tweet in the ``tweet`` attribute.
		:rtype: list of :class:`~nlp.document.Document`
		"""

		documents = [ ]

		"""
		The text used for the document depend on what kind of tweet it is.
		If the tweet is too long to fit in the tweet, the full text is used;

		Retain the comment of a quoted status.
		However, if the tweet is a plain retweet, get the full text.
		"""
		for item in tweets:
			tweet = item.attributes['tweet'] if type(item) is Document else item
			text = twitter.full_text(tweet)

			"""
			Create the document and save the tweet in it.
			"""
			tokens = self.tokenizer.tokenize(text)
			document = item if type(item) is Document else self.scheme.create(tokens, text=text)
			document.attributes['id'] = tweet.get('id')
			document.attributes['timestamp'] = twitter.extract_timestamp(tweet)
			document.attributes['tweet'] = tweet
			document.normalize()
			documents.append(document)

		return documents
