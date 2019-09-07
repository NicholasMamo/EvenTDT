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

from apd.extractors.local.entity_extractor import EntityExtractor
from apd.scorers.local.sum_scorer import SumScorer

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer

class EntityResolver(Resolver):
	"""
	The resolver looks for named entities in the text.
	Then, it uses these entities to try and resolve participants.
	"""

	def resolve(self, participants, corpus, token_attribute="tokens", *args, **kwargs):
		"""
		Resolve the given participants by looking for the original word.

		:param participants: The participants to resolve.
		:type participants: list
		:param corpus: The corpus of documents, which helps to resolve the participants.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A tuple containing the resolved participants, and unresolved ones.
		:rtype: list
		"""

		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)
		ner_extractor = EntityExtractor()
		sum_scorer = SumScorer()

		"""
		Fetch the named entities first.
		The named entities are kept as a list and scored.
		This list is sorted, and in this way, the resolution stops at the most significant named entity.
		"""
		entities = ner_extractor.extract(corpus, token_attribute=token_attribute)
		scored_entities = list(sum_scorer.score(entities).keys())

		"""
		First tokenize the corpus in a NER-friendly way.
		"""
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_text())
			tokenized_corpus.append(Document(document.get_text(), tokens, { "tokens": tokens, "text": document.get_text() }))

		tokenizer = Tokenizer(min_length=1, stem=False)
		tokenized_named_entities = [ tokenizer.tokenize(entity) for entity in scored_entities ]

		"""
		Try to resolve the participants.
		"""
		unresolved_participants, resolved_participants = [], []
		for participant in participants:
			resolved = None
			if participant in scored_entities:
				resolved_participants.append(participant)
			else:
				for i, entity_tokens in enumerate(tokenized_named_entities):
					"""
					First try to check if the participant is part of a named entity.
					If that fails, look for the participant is a stemmed version of any token.
					"""
					if participant in entity_tokens:
						resolved = scored_entities[i]
						break

				if resolved is not None:
					resolved_participants.append(resolved)
				else:
					unresolved_participants.append(participant)

		return resolved_participants, unresolved_participants
