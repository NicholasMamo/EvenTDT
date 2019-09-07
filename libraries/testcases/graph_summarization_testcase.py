import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
	sys.path.insert(1, path)

from graph.graph import Graph, Node

from summarization.algorithms import mamo_graph
from summarization.cleaners import tweet_cleaner

from vector import vector_math
from vector.cluster.cluster import Cluster
from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer

tokenizer = Tokenizer()
summarizer = mamo_graph.DocumentGraphSummarizer()

posts = [
	("Manchester United falter against Tottenham Hotspur", 5),
	("United unable to avoid defeat to Tottenham", 6),
	("Manchester United lost to Tottenham Hotspur", 7),
	("Emery confident of Arsenal win", 8),
	("Mourinho under pressure as Manchester United follow with a loss", 9),
	("Manchester United powerless in loss to Tottenham", 9),
	("Arsenal hold out for a win against Cardiff", 11),
	("Arsenal narrowly see out Cardiff", 12),
	("Lacazette shines in Arsenal win", 13),
	("Aubameyang and Lacazette combine for Arsenal", 18)
]

documents = [ Document(tokenizer.tokenize(post), { "text": post, "timestamp": timestamp }) for post, timestamp in posts ]
united_cluster = Cluster(documents[:4])
arsenal_cluster = Cluster(documents[4:])

summary1 = summarizer.add_cluster(united_cluster, [(tokenizer.tokenize("manchester")[0], 0.9), (tokenizer.tokenize("united")[0], 0.8), (tokenizer.tokenize("tottenham")[0], 0.5)], 10)
print(summary1.generate_summary(cleaner=tweet_cleaner.TweetCleaner))
summary2 = summarizer.add_cluster(arsenal_cluster, [(tokenizer.tokenize("arsenal")[0], 0.85), (tokenizer.tokenize("lacazette")[0], 0.6)], 20)
print(summary2.generate_summary(cleaner=tweet_cleaner.TweetCleaner))
