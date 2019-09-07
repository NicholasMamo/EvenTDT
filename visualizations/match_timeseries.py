import json
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os
import palette
import sys

FILENAME = "/mnt/data/twitter/BELENG.json"
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

	t = Tokenizer()
	documents = []
	for tweet in tweets:
		timestamp_ms = int(tweet["timestamp_ms"])
		timestamp = int(timestamp_ms / 1000)
		tokens = t.tokenize(tweet.get("text", ""),
			normalize_words=True,
			character_normalization_count=3)

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

with open(FILENAME, "r")  as f:
	timestamp = None
	documents = []
	track = []
	for line in f:
		tweet = json.loads(line)
		if tweet["lang"] == "en":
			document = _tokenize([tweet])[0]
			documents.append(document)
			last_timestamp = document.get_attribute("timestamp")
			timestamp = timestamp if timestamp is not None else last_timestamp

			if last_timestamp - timestamp > TIME_WINDOW:
				checkpoint = _create_checkpoint(documents)
				timestamp = last_timestamp
				track.append([ checkpoint.get(keyword, 0) for keyword, _ in TRACK ])

				if len(track) % (600/TIME_WINDOW) == 0:
					print("10 minutes finished")

	for i, (keyword, color) in enumerate(TRACK):
		plt.plot(range(0, len(track)), [ track_set[i] for track_set in track ], color=palette.primary[color])
		plt.savefig("visualizations/export/timeseries.png")
