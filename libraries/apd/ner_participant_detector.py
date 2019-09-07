"""
A participant detector that is based on natural language processing (NLP).
More precisely, it is based on recognizing named entities in the text.
"""

import nltk

from .participant_detector import ParticipantDetector

class NERParticipantDetector(ParticipantDetector):
	"""
	The NER participant detector focuses on named entities.
	Only participants that are named entities are retained.
	"""

	def __init__(self):
		pass

	def detect(self, corpus, threshold=0, max_candidates=-1, text_attribute="text", token_attribute="tokens"):
		"""
		Detect participants from the given corpus.

		:param corpus: The corpus of documents on which the search is based.
		:type corpus: list
		:param threshold: The minimum score to retain a candidate.
		:type threshold: float
		:param max_candidates: The maximum number of candidates to retain.
			Only the top ones should be retained after ranking.
		:type max_candidates: int
		:param text_attribute: The attribute that contains the text.
		:type text_attribute: str
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: The list of participants.
		:rtype: list
		"""

		documents = self._search(corpus, token_attribute)
		candidates = self._score(documents)
		filtered = self._filter(candidates, threshold=threshold, max_candidates=max_candidates)
		return filtered

	def _search(self, corpus, token_attribute="tokens"):
		"""
		Search within the corpus for candidate participants.

		:param corpus: The corpus of documents on which the search is based.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: The list of candidate participants extracted from each document in the corpus.
		:rtype: list
		"""

		documents = []
		for document in corpus:
			"""
			Extract the named entities in the document.
			"""
			pos_tags = nltk.pos_tag(document.get_attribute(token_attribute))
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

			name = ' '.join(current_entity).strip()
			named_entities.append(name.lower())
			named_entities = [entity for entity in named_entities if len(entity) > 0]
			documents.append(named_entities)

		return documents

	def _score(self, documents):
		"""
		Score the given candidates based on their relevance within the corpus.
		The score of the NER-based detector is simply the percentage of times an entity appears in the corpus.

		:param documents: A list of documents and the participants that were found in them earlier.
		:type documents: list

		:return: A dictionary of participants and their associated scores.
		:rtype: dict
		"""

		"""
		The score function assigns a score to each candidate.
		The scores are stored in a dictionary.
		"""
		candidate_scores = {}

		"""
		Go through each document, and then each of its candidates.
		For all of these instances, increment their score.
		"""
		for candidates in documents:
			for candidate in list(set(candidates)):
				candidate_scores[candidate] = candidate_scores.get(candidate, 0) + 1

		"""
		Normalize the scores.
		"""
		candidate_scores = { candidate: score/len(documents) for candidate, score in candidate_scores.items() }
		return candidate_scores

	def _filter(self, candidates, threshold=0, max_candidates=-1):
		"""
		Filter the given candidates and return only the top.

		:param candidates: A dictionary of candidates participants that were found earlier, accompanied with a score.
		:type candidates: dict
		:param threshold: The minimum score to retain a candidate.
		:type threshold: float
		:param max_candidates: The maximum number of candidates to retain.
			Only the top ones should be retained after ranking.
		:type max_candidates: int

		:return: A list of retained candidates.
		:rtype: list
		"""

		candidates = { candidate: score for candidate, score in candidates.items() if score >= threshold }
		candidates = sorted(candidates.items(), key=lambda x: x[1])[::-1]

		if max_candidates > -1:
			return list([ candidate for candidate, _ in candidates ])[:max_candidates]
		else:
			return list([ candidate for candidate, _ in candidates ])
