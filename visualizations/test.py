import json
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os
import palette
import sys

FILENAME = "/mnt/data/twitter/TOTWOL_FUL.json"
TIME_WINDOW = 30
TRACK = [ ("card", "yellow"), ("goal", "red") ]

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
	sys.path.insert(1, path)

from libraries.vector import vector_math
from libraries.vector.nlp.document import Document
from libraries.vector.nlp.tokenizer import Tokenizer

def _tokenize(tweets):
	"""
	Tokenize the given list of tweets
	Return a list of Document instances
	"""

	t = Tokenizer(normalize_words=True,
		character_normalization_count=3)
	documents = []
	for tweet in tweets:
		timestamp_ms = int(tweet["timestamp_ms"])
		timestamp = int(timestamp_ms / 1000)
		tokens = t.tokenize(tweet.get("text", ""))

		document = Document(tokens)
		document.set_attribute("text", tweet.get("text", ""))
		document.set_attribute("tokens", tokens)
		document.set_attribute("timestamp", timestamp)
		document.normalize()
		documents.append(document)

	return documents

def _create_checkpoint(documents):
	"""
	After every time window has elapsed, get all the buffered documents
	These documents are used to create a nutrition set for the nutrition store
	This nutrition set represents a snapshot of the time window
	"""

	"""
	Extract all tweets
	"""
	if len(documents) > 0:
		"""
		Concatenate all the documents in the buffer and normalize the dimensions
		The goal is to get a list of dimensions in the range 0 to 1
		"""
		single_document = vector_math.concatenate(documents)
		single_document = vector_math.augmented_normalize(single_document, a=0)
		return single_document.get_dimensions()


out_of_order = {}
total = 0
with open(FILENAME, "r")  as f:
	last_timestamp = 0
	for line in f:
		tweet = json.loads(line)
		if tweet["lang"] == "en":
			document = _tokenize([tweet])[0]
			total += 1
			if last_timestamp > document.get_attribute("timestamp"):
				diff = last_timestamp - document.get_attribute("timestamp")
				out_of_order[diff] = out_of_order.get(diff, 0)
				out_of_order[diff] += 1

			last_timestamp = document.get_attribute("timestamp")

print(total, "documents")
print(out_of_order)
