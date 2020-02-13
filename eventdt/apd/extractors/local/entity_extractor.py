"""
The entity extractor considers only named entities to be candidate participants.
This extractor requires `NLTK <http://nltk.org/>`_ to work.
It does not distinguish between named entity types.
"""

import os
import sys

import nltk

from ..extractor import Extractor

class EntityExtractor(Extractor):
	"""
	The entity extractor uses NLTK to extract named entities from a corpus of documents.
	"""

	def extract(self, corpus, binary=True, *args, **kwargs):
		"""
		Extract all the named entities from the corpus.
		The output is a list of lists.
		Each outer list represents a document.
		Each inner list is the candidates in that document.

		:param corpus: The corpus of documents where to extract candidate participants.
		:type corpus: list
		:param binary: A boolean indicating whether named entity extraction should be binary.
					   If true, all named entities have the same type.
					   This is enabled by default to minimize false negatives.
		:type binary: bool

		:return: A list of candidates separated by the document in which they were found.
		:rtype: list
		"""

		candidates = [ ]

		for document in corpus:
			document_entities = []

			"""
			Split the document into sentences, and extract the named entities from each sentence.
			"""
			sentences = nltk.sent_tokenize(document.text)
			for sentence in sentences:
				chunks = self._extract_entities(sentence, binary)
				named_entities = self._combine_adjacent_entities(chunks)
				document_entities.extend(named_entities)

			candidates.append(document_entities)

		return candidates

	def _extract_entities(self, sentence, binary):
		"""
		Extract the named entities from the given sentence.

		:param sentence: The sentence from where to extract named entities.
		:type sentence: str
		:param binary: A boolean indicating whether named entity extraction should be binary.
					   If true, all named entities have the same type.
		:type binary: bool

		:return: A list of chunks, which may be simple strings or named entities.
		:rtype: list of str or nltk.tree.Tree
		"""

		tokens = nltk.word_tokenize(sentence)
		pos_tags = nltk.pos_tag(tokens)
		return [ chunk for chunk in nltk.ne_chunk(pos_tags, binary=binary) ]

	def _combine_adjacent_entities(self, chunks):
		"""
		Combine the chunks appearing in the given list.
		The function assumes that the list represents one sentence.
		If two tokens next to each other have the same type, the function combines them into a single string.
		The function returns only the named entities.

		:param chunks: The list of chunks.
		:type chunks: list of str or nltk.tree.Tree

		:return: A list of named entities.
		:rtype: list of str
		"""

		named_entities = []

		"""
		Iterate over each chunk.
		If a chunk is an entity, then start building a named entity.
		This is interrupted whenever a chunk is not an entity, or if it has a different type.
		"""
		entity, entity_type = [], None
		for chunk in chunks:
			if type(chunk) is nltk.tree.Tree:
				"""
				If the type of named entity has changed, retire it.
				This means adding the sequence to the list of named entities, and resetting the memory.
				"""
				label = chunk.label()
				if label != entity_type:
					named_entities.append(' '.join(entity).strip().lower())
					entity, entity_type = [], None

				"""
				Add the tokens to the named entity sequence.
				"""
				entity_type = label
				named_entity_tokens = [ pair[0].lower() for pair in chunk ]
				entity.extend(named_entity_tokens)
			else:
				named_entities.append(' '.join(entity).strip().lower())
				entity, entity_type = [], None

		"""
		Save the last named entity.
		Filter out named entities that have no length.
		"""
		named_entities.append(' '.join(entity).strip().lower())
		named_entities = [ entity for entity in named_entities if len(entity) ]

		return named_entities
