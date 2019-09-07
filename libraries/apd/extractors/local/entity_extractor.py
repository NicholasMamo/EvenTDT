"""
An extractor that only considers named entities to be potential candidates.
"""

import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.append(path)

import nltk

from ..extractor import Extractor

from vector.nlp.tokenizer import Tokenizer
from vector.nlp.document import Document

class EntityExtractor(Extractor):
	"""
	The entity extractor uses NLP techniques to only extract named entities from the stream of documents.
	"""

	def extract(self, corpus, token_attribute="tokens", *args, **kwargs):
		"""
		Extract all the named entities from the corpus.
		The output is a list of lists.
		It should be noted that zipping together this list and the corpus should return a list of documents and associated candidates.

		:param corpus: The corpus of documents where to extract participants.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A list of candidates separated by the document in which they were found.
		:rtype: list
		"""

		"""
		First tokenize the corpus in a NER-friendly way.
		"""
		tokenizer = Tokenizer(case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_text())
			tokenized_corpus.append(Document(document.get_text(), tokens, { "tokens": tokens }))

		documents = []
		for document in tokenized_corpus:
			"""
			Extract the named entities in the document.
			"""
			pos_tags = nltk.pos_tag(document.get_attribute("tokens"))
			entities = [ entity for entity in nltk.ne_chunk(pos_tags) ]

			"""
			Find the named entities and concatenate consecutive ones.
			"""
			named_entities = []
			current_entity, current_entity_type = [], None
			for entity in entities:
				"""
				If the entity is an actual named entity, try to connect it to previous entities.
				If it is not an entity, add the current named entity sequence to the list of found ones.
				Finally, reset the current entity memory.
				"""
				if type(entity) == nltk.tree.Tree:
					"""
					If the type of named entity has changed, retire it.
					This means adding the sequence to the list of named entities, and resetting the memory.
					"""
					label = entity.label()
					if label != current_entity_type:
						name = ' '.join(current_entity).strip()
						named_entities.append(name.lower())
						current_entity, current_entity_type = [], None

					"""
					Then, update the label - or leave it unchanged, if this is a sequence.
					The tokens are added to the sequence.
					"""
					current_entity_type = label
					named_entity_tokens = [pair[0].lower() for pair in entity]
					current_entity.extend(named_entity_tokens)
				else:
					name = ' '.join(current_entity).strip()
					named_entities.append(name.lower())
					current_entity, current_entity_type = [], None

			"""
			Wrap up in the end by saving the named entity.
			"""
			name = ' '.join(current_entity).strip()
			named_entities.append(name.lower())
			named_entities = [entity for entity in named_entities if len(entity) > 0]
			documents.append(named_entities)

		return documents
