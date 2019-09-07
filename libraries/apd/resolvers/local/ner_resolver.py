"""
A resolver that tries to resolve a participant to a named entity.
"""

import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.append(path)

import nltk

from ..resolver import Resolver

from apd.extractors.local.entity_extractor import NERExtractor
from apd.scorers.local.sum_scorer import SumScorer

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer

class NERResolver(Resolver):
	"""
	The resolver looks for named entities in the text.
	Then, it uses these entities to try and resolve participants.
	"""

	def resolve(self, participants, corpus, text_attribute="text", token_attribute="tokens"):
		"""
		Resolve the given participants by looking for the original word.

		:param participants: The participants to resolve.
		:type participants: list
		:param corpus: The corpus of documents, which helps to resolve the participants.
		:type corpus: list
		:param text_attribute: The attribute that contains the text.
		:type text_attribute: str
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A tuple containing the resolved participants, and unresolved ones.
		:rtype: list
		"""

		tokenizer = Tokenizer()
		ner_extractor = NERExtractor()
		sum_scorer = SumScorer()

		"""
		Fetch the named entities first.
		The named entities are kept as a list and scored.
		This list is sorted, and in this way, the resolution stops at the most significant named entity.
		"""
		entities = NERExtractor.extract(corpus, text_attribute=text_attribute, token_attribute=token_attribute)
		scored_entities = SumScorer.score(entities)

		"""
		First tokenize the corpus in a NER-friendly way.
		"""
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_attribute(text_attribute), case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)
			tokenized_corpus.append(Document(tokens, { "tokens": tokens, "text": document.get_attribute(text_attribute) }))
		tokenized_named_entities = [ tokenizer.tokenize(entity, min_length=1) for entity in named_entities ]

		"""
		Get the named entities' inverted index.
		"""
		inverted_index = {}
		for document in tokenized_corpus:
			for token in document.get_attribute("tokens"):
				"""
				In some cases, the word itself may be split - for example in the case of possessive: `Mourinho's`.
				"""
				token = tokenizer.tokenize(token, min_length=1, stem=False)[0]
				stemmed_tokens = tokenizer.tokenize(token, min_length=1)
				for stemmed_token in stemmed_tokens:
					inverted_index[stemmed_token] = inverted_index.get(stemmed_token, {})
					inverted_index[stemmed_token][token] = inverted_index.get(stemmed_token, {}).get(token, 0) + 1 # create an entry if need be

		"""
		Use majority voting to find the most common word.
		"""
		for stemmed_token in inverted_index:
			inverted_index[stemmed_token] = max(inverted_index[stemmed_token].items(), key=lambda x: x[1])[0]

		"""
		Try to resolve the participants.
		"""
		unresolved_participants, resolved_participants = [], []
		for participant in participants:
			resolved = None
			for i, entity_tokens in enumerate(tokenized_named_entities):
				if participant in entity_tokens:
					resolved = named_entities[i]
					break

			if resolved is not None:
				resolved_participants.append(resolved)
			else:
				unresolved_participants.append(participant)

		return resolved_participants, unresolved_participants
