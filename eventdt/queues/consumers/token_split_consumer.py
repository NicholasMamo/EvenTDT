"""
The :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer` splits tweets into different streams based on what tokens they include.
This means that all splits have a simple, thematic focus.

This split consumer allows the splits to overlap, which means that tweets can be assigned to multiple streams.
However, it discards tweets that do not satisfy any split.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from .split_consumer import SplitConsumer
from nlp import Tokenizer
from nlp.weighting import TF
import twitter

class TokenSplitConsumer(SplitConsumer):
	"""
	The :class:`~queues.consumers.token_split_consumer.TokenSplitConsumer` splits tweets into different streams based on what tokens they include.

	This split consumer uses a :class:`~nlp.tokenizer.Tokenizer` to split the tweets' text into tokens and check if they validate the conditions.
	The class maintains the :class:`~nlp.tokenizer.Tokenizer` in its state.

	This consumer also assumes that its downstream consumers will use :class:`~nlp.document.Document` instances instead of tweets.
	Therefore it converts all tweets into :class:`~nlp.document.Document` instances using the given :class:`~nlp.weighting.TermWeightingScheme`, maintained in its state.
	This is done to improve efficiency.
	Since the split consumer can send one tweet into multiple streams, these streams do not have to tokenize and weight the same tweets again.
	This class tokenizes tweets based on the :func:`full text <twitter.full_text>`.

	.. note::

		The class has to tokenize tweets on behalf of its consumers to decide in which queue to send tweets.
		However, the downstream consumers can tokenize the tweets again themselves.
		All documents have their full text stored in the document's text.
		In addition, the original tweets are stored in the documents' ``tweet`` attribute.


	:ivar includes: The function that is used to check whether a tweet includes the tokens defined in the splits.

					- If ``any`` is provided, the consumer assigns a tweet to a stream if it includes any of the tokens defined in the corresponding split.
					- If ``all`` is provided, the consumer assigns a tweet to a stream if it includes all of the tokens defined in the corresponding split.

					A custom function can be provided.
					For example, a custom function can define that a tweet satisfies the split if it includes at least two tokens in it.
					If one is given, it must receive as input a number of boolean values.
					Its output must be a boolean indicating whether the tweet satisfies the conditions of the split.
	:vartype includes: func
	:ivar ~.tokenizer: The tokenizer to use to tokenize tweets and check if a token is present in the tweets.
	:vartype tokenizer: :class:`~nlp.tokenizer.Tokenizer`
	:ivar scheme: The term-weighting scheme that is used to create documents from tweets.
	:vartype scheme: :class:`~nlp.weighting.TermWeightingScheme`
	"""

	def __init__(self, queue, splits, consumer, includes=any, tokenizer=None, scheme=None, *args, **kwargs):
		"""
		Initialize the consumer with its :class:`~queues.Queue`.

		For each given split, this function creates one :class:`~queues.consumers.Consumer` of the given type.
		This consumer has its own queue, which receive tweets that satisfy the associated condition.

		Any additional arguments or keyword arguments are passed on to the consumer's constructor.

		:param queue: The queue that receives the entire stream.
		:type queue: :class:`~queues.Queue`
		:param splits: A list of splits, or conditions that determine into which queue a tweet goes.
					   The type of the splits depends on what the :func:`~queues.consumers.split_consumer.SplitConsumer._satisfies` function looks for.
		:type splits: list of str or list of list of str or list of tuple of str
		:param consumer: The type of :class:`~queues.consumers.Consumer` to create for each split.
		:type consumer: type
		:param includes: The function that is used to check whether a tweet includes the tokens defined in the splits.

						 - If ``any`` is provided, the consumer assigns a tweet to a stream if it includes any of the tokens defined in the corresponding split.
						 - If ``all`` is provided, the consumer assigns a tweet to a stream if it includes all of the tokens defined in the corresponding split.

						 A custom function can be provided.
						 For example, a custom function can define that a tweet satisfies the split if it includes at least two tokens in it.
						 If one is given, it must receive as input a number of boolean values.
						 Its output must be a boolean indicating whether the tweet satisfies the conditions of the split.
		:type includes: func
		:param tokenizer: The tokenizer to use to tokenize tweets and check if a token is present in the tweets.
						  If one isn't given, the class creates a custom tokenizer.
		:type tokenizer: None or :class:`~nlp.tokenizer.Tokenizer`
		:param scheme: The term-weighting scheme that is used to create documents from tweets.
					   If ``None`` is given, the :class:`~nlp.weighting.tf.TF` term-weighting scheme is used.
		:type scheme: None or :class:`~nlp.weighting.TermWeightingScheme`
		"""

		splits = [ [ split ] if type(split) is str else list(split)
		 					 for split in splits ]

		super(TokenSplitConsumer, self).__init__(queue, splits, consumer)
		self.tokenizer = tokenizer or Tokenizer(normalize_words=True, character_normalization_count=3,
												remove_unicode_entities=True, stem=True)
		self.scheme = scheme or TF()
		self.includes = includes

	def _preprocess(self, tweet):
		"""
		Pre-process the given tweet.

		This function assumes that all of the downstream consumers will work with :class:`~nlp.document.Document` instances.
		Therefore it tokenizes the tweets and uses the scheme to convert them into documents.

		:param tweet: The tweet to pre-process.
		:type tweet: dict

		:return: The tweet as a document.
		:rtype: :class:`~nlp.document.Document`
		"""

		text = twitter.full_text(tweet)
		tokens = self.tokenizer.tokenize(text)
		document = self.scheme.create(tokens, text=text, attributes={ 'tweet': tweet })
		document.normalize()
		return document

	def _satisfies(self, document, tokens):
		"""
		Check whether the given document includes the given tokens.
		The function checks if any of the given tokens are present in the document's dimensions.

		:param document: The document to validate whether it contains the given tokens.
		:type document: :class:`~nlp.document.Document`
		:param tokens: The list of tokens that need to be present in the given document.
		:type tokens: list of str

		:return: A boolean indicating whether the given document contains the tokens.
		:rtype: bool
		"""

		return any( token in document.dimensions for token in tokens )
