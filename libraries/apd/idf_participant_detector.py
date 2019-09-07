"""
A participant detector that is based on the significance of keywords.
"""

import math
import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
	sys.path.append(path)

from .participant_detector import ParticipantDetector
from .ner_participant_detector import NERParticipantDetector

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer

class IDFParticipantDetector(ParticipantDetector):
	"""
	The IDF participant detector focuses on extracting keywords that appear significantly in the corpus.
	This is contrasted with their appearance in normal discourse.
	"""

	def detect(self, corpus, idf, resolve_names=True, threshold=0, max_candidates=-1, text_attribute="text", token_attribute="tokens"):
		"""
		Detect participants from the given corpus.

		:param corpus: The corpus of documents on which the search is based.
		:type corpus: list
		:param idf: The IDF table, represented as a dictionary.
			It is assumed that the number of documents is stored in the key 'DOCUMENTS.'
		:type idf: dict
		:param resolve_names: A boolean indicating whether the participant detector should transform the candidates into named entities.
		:type resolve_names: bool
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
		candidates = self._score(documents, idf)
		filtered = self._filter(candidates, threshold=threshold, max_candidates=max_candidates)
		if resolve_names:
			filtered = self._resolve(corpus, filtered, text_attribute)
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

		return [ [ token for token in document.get_attribute(token_attribute) ] for document in corpus ]

	def _score(self, documents, idf):
		"""
		Score the given candidates based on their relevance within the corpus.

		:param documents: A list of documents and the participants that were found in them earlier.
		:type documents: list
		:param idf: The IDF table, represented as a dictionary.
			It is assumed that the number of documents is stored in the key 'DOCUMENTS.'
		:type idf: dict

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
				idf_score = candidates.count(candidate) * math.log(max(idf.get("DOCUMENTS"), 1) / idf.get(candidate, 1), 10)
				candidate_scores[candidate] = candidate_scores.get(candidate, 0) + idf_score

		"""
		Normalize the scores.
		"""
		max_score = max(candidate_scores.values())
		candidate_scores = { candidate: score/max_score for candidate, score in candidate_scores.items() }
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

		candidates = { candidate: score for candidate, score in candidates.items() if score > threshold }
		candidates = sorted(candidates.items(), key=lambda x: x[1])[::-1]

		if max_candidates > -1:
			return list([ candidate for candidate, _ in candidates ])[:max_candidates]
		else:
			return list([ candidate for candidate, _ in candidates ])

	def _resolve(self, corpus, candidates, text_attribute):
		"""
		Resolve the tokens, transforming them into named entities, if they exist.
		If they do not exist, resolve them into tokens.

		:param corpus: The corpus of documents on which the search is based.
		:type corpus: list
		:param candidates: The list of retained candidates.
		:type candidates: list
		:param text_attribute: The attribute that contains the text.
		:type text_attribute: str

		:return: A list of resolved candidates, if possible.
		:rtype: list
		"""

		"""
		Fetch the named entities first.
		The named entities are kept as a list.
		This list is sorted, and in this way, the resolution stops at the most significant named entity.
		"""
		ner_detector = NERParticipantDetector()
		tokenizer = Tokenizer()

		"""
		First tokenize the corpus in a NER-friendly way.
		"""
		tokenized_corpus = []
		for document in corpus:
			tokens = tokenizer.tokenize(document.get_attribute(text_attribute), case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)
			tokenized_corpus.append(Document(tokens, { "tokens": tokens, "text": document.get_attribute(text_attribute) }))

		named_entities = ner_detector.detect(tokenized_corpus)
		tokenized_named_entities = [ tokenizer.tokenize(entity, min_length=1) for entity in named_entities ]

		"""
		The backup is resolution to a single word.
		For each stem, find the most common word.
		"""
		reverse_index = {}
		for document in tokenized_corpus:
			for token in document.get_attribute("tokens"):
				"""
				In some cases, the word itself may be split - for example in the case of possessive: `Mourinho's`.
				"""
				token = tokenizer.tokenize(token, min_length=1, stem=False)[0]
				stemmed_tokens = tokenizer.tokenize(token, min_length=1)
				for stemmed_token in stemmed_tokens:
					reverse_index[stemmed_token] = reverse_index.get(stemmed_token, {})
					reverse_index[stemmed_token][token] = reverse_index.get(stemmed_token, {}).get(token, 0) + 1 # create an entry if need be

		"""
		Use majority voting to find the most common word.
		"""
		for stemmed_token in reverse_index:
			reverse_index[stemmed_token] = max(reverse_index[stemmed_token].items(), key=lambda x: x[1])[0]

		"""
		Then try to resolve the candidates.
		"""
		resolved_candidates = []
		for candidate in candidates:
			"""
			Try to resolve entities using named entities first.
			"""
			for i, entity_tokens in enumerate(tokenized_named_entities):
				if candidate in entity_tokens:
					resolved = named_entities[i]
					break

			"""
			If this fails, resolve to the most common word.
			"""
			if resolved is not None:
				resolved_candidates.append(resolved)
			else:
				resolved_candidates.append(reverse_index.get(candidate, candidate).lower())

		return resolved_candidates
