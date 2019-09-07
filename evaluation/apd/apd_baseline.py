"""
Parse the squad list and print out player names as a list that can be copy-pasted into a Python script.

Requires one argument to function - the name of the source in the 'original' folder.
"""

import json
import os
import re
import sys
import urllib.parse

path = os.path.dirname(__file__)
path = os.path.join(path, "../../libraries")
if path not in sys.path:
	sys.path.insert(1, path)

from nltk.corpus import stopwords, words

from apd.participant_detector import ParticipantDetector
from apd.extrapolators.external.wikipedia_extrapolator import LinkExtrapolator, WikipediaExtrapolator
from apd.extractors.local.entity_extractor import EntityExtractor
from apd.extractors.local.token_extractor import TokenExtractor
from apd.extrapolators.extrapolator import Extrapolator
from apd.postprocessors.postprocessor import Postprocessor
from apd.postprocessors.external.wikipedia_postprocessor import WikipediaPostprocessor
from apd.resolvers.resolver import Resolver
from apd.resolvers.external.wikipedia_resolver import SearchResolver, WikipediaResolver
from apd.resolvers.local.entity_resolver import EntityResolver
from apd.resolvers.local.token_resolver import TokenResolver
from apd.scorers.local.idf_scorer import IDFScorer
from apd.scorers.local.sum_scorer import LogSumScorer, SumScorer

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer
from vector.nlp.term_weighting import TF, TFIDF

from logger import logger

if len(sys.argv) > 1:
	"""
	Load the text.
	"""
	filename = sys.argv[1]

	with open(os.path.join("/home/memonick/data/idf.json"), "r") as idf_file:
		general_idf = json.loads(idf_file.readline())
		tokenizer = Tokenizer(stopwords=stopwords.words("english"),
			normalize_words=True,
			character_normalization_count=3,
			remove_unicode_entities=True)
		term_weighting = TFIDF(general_idf)

		corpus = []
		with open("/mnt/data/twitter/%s" % filename, "r") as f:
			for tweet in f:
				tweet = json.loads(tweet)
				if "retweeted_status" in tweet and "quoted_status" not in tweet:
					text = tweet["retweeted_status"].get("extended_tweet", {}).get("full_text", tweet.get("text", ""))
				else:
					text = tweet.get("text", "")
				tokens = tokenizer.tokenize(text)
				document = Document(text, tokens, attributes={ "tokens": tokens, "tweet": tweet }, scheme=term_weighting)
				document.normalize()
				corpus.append(document)

		participant_detector = ParticipantDetector(corpus, EntityExtractor, LogSumScorer, Resolver, Extrapolator, Postprocessor)
		resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.2, max_candidates=50, combine=False)
		# participant_detector = ParticipantDetector(corpus, EntityExtractor, LogSumScorer, SearchResolver, LinkExtrapolator, WikipediaPostprocessor)
		# resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.2, max_candidates=30, combine=True,
		# 	resolver_scheme=TFIDF(general_idf), resolver_threshold=0.05,
		# 	extrapolator_scheme=TFIDF(general_idf), extrapolator_participants=30, extrapolator_threshold=0.05,
		# 	postprocessor_surname_only=True)

		# NOTE: Original
		# participant_detector = ParticipantDetector(corpus, TokenExtractor, IDFScorer, TokenResolver, Extrapolator, Postprocessor)
		# resolved, unresolved, extrapolated = participant_detector.detect(threshold=0.025, max_candidates=50, scorer_idf=general_idf)
		print(resolved)
		print(unresolved)
		print(extrapolated)


else:
	logger.error("File name not specified")
