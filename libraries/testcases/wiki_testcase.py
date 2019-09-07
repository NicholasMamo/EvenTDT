import json
import os
import re
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../'))

from nltk.corpus import stopwords

from vector import vector_math
from vector.nlp.document import Document
from vector.nlp.term_weighting import TFIDF
from vector.nlp.tokenizer import Tokenizer

from wikinterface.textcollector import TextCollector

with open(os.path.join("/home/memonick/data/idf.json"), "r") as idf_file:
	general_idf = json.loads(idf_file.readline())

	delimiter_pattern = re.compile("^(.+?)\.[\s\n][A-Z0-9]")
	tokenizer = Tokenizer(stopwords=stopwords.words("english"))
	pages = ["Washington (state)", "New Mexico"]

	text_collector = TextCollector()
	text_content = text_collector.get_plain_text(pages, introduction_only=True)

	documents = []
	for text in text_content.values():
		matches = delimiter_pattern.findall(text)
		text = text if len(matches) == 0 else matches[0]
		documents.append(Document(text, tokenizer.tokenize(text), scheme=TFIDF(general_idf)))

	print(vector_math.cosine(documents[0], documents[1]))
