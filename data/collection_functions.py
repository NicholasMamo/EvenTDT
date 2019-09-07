import os
import sys

from nltk.corpus import words

sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))

from apd.participant_detector import ParticipantDetector
from apd.extractors.local.entity_extractor import EntityExtractor
from apd.extrapolators.external.wikipedia_extrapolator import LinkExtrapolator, WikipediaExtrapolator
from apd.postprocessors.external.wikipedia_postprocessor import WikipediaPostprocessor
from apd.resolvers.local.entity_resolver import EntityResolver
from apd.resolvers.external.wikipedia_resolver import SearchResolver, WikipediaResolver
from apd.scorers.local.sum_scorer import SumScorer, LogSumScorer

from queues.consumer.filter import filter
from queues.consumer.filter.filter import Filter

from summarization.scorers import tweet_scorer

from vector.nlp.cleaners import tweet_cleaner
from vector.nlp.term_weighting import TF, TFIDF

def filter_tweets(tweets):
	"""
	Filter the given tweets, largely based on FIRE's filtering rules.
	Tweets are removed if:

	#. They are not in English - an extra check, just in case;

	#. There are too many hashtags, indicating that the user is desperate for attention;

	#. The user has never favorited a tweet, indicative of bot-like behavior.;

	#. The user has fewer than one follower for every thousand tweets published. \
		These users are usually not only incredibly unpopular, but bots. \
		Their goal is to create trends;

	#. There is more than one URL. Too many URLs are indicative of pre-planned content. \
		For this reason alone, they may be removed. \
		If a development is breaking, many people post immediately, with minimal media; and

	#. The biography is empty. \
		Most users have a biography. Spam accounts do not bother.

	:param tweets: A list of tweets.
	:type tweets: list of dictionaries

	:return: A list of filtered tweets.
	:type tweets: list of dictionaries
	"""

	"""
	Remove objects that are not really tweets
	"""
	retained_tweets = []
	for tweet in tweets:
		if ("entities" in tweet):
			retained_tweets.append(tweet)

	for tweet in retained_tweets:
		"""
		Calculate some scores that are not provided by Twitter's API
		"""
		tweet["num_hashtags"] = len(tweet["entities"]["hashtags"])
		tweet["num_urls"] = len(tweet["entities"]["urls"])
		tweet["follower_per_tweet"] = tweet["user"]["followers_count"] / tweet["user"]["statuses_count"]
		tweet["bio_length"] = len(tweet["user"]["description"]) if tweet["user"]["description"] is not None else 0

	rules = [
		("lang", filter.equal, "en"),
		("num_hashtags", filter.lte, 2),
		("user:favourites_count", filter.gt, 0),
		("follower_per_tweet", filter.gte, 1./1000.)
	]

	# Rules that are new in ELD
	rules.append(("num_urls", filter.lt, 2))
	rules.append(("bio_length", filter.gt, 0))

	f = Filter(rules)
	return [ tweet for tweet in retained_tweets if f.filter(tweet) ]

def detect_participants(documents, general_idf, known_participants):
	"""
	Detect participants from the given list of documents.

	:param documents: The list of documents where to look.
	:type documents: list
	:param general_idf: The IDF table, used in the term weighting schemes.
	:type general_idf: dict
	:param known_participants: A list of participants that are known.
		These are used to boost extrapolation.
	:type known_participants: dict
	"""

	cleaner = tweet_cleaner.TweetCleaner()
	scorer = tweet_scorer.TweetScorer()

	rules = [
		("score", filter.gte, 0.9)
	]
	f = Filter(rules)

	corpus = []
	for document in documents:
		document.set_text(cleaner.clean(document.get_text()))

		tweet = {
			"score": scorer.score(document),
		}

		if f.filter(tweet):
			corpus.append(document)

	participant_detector = ParticipantDetector(corpus, EntityExtractor, LogSumScorer, SearchResolver, LinkExtrapolator, WikipediaPostprocessor)
	resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.2, max_candidates=20, known_participants=known_participants,
		resolver_scheme=TFIDF(general_idf), resolver_threshold=0.05,
		extrapolator_scheme=TFIDF(general_idf), extrapolator_participants=30, extrapolator_threshold=0.05,
		postprocessor_surname_only=True)
	return resolved, extrapolated
