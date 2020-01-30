"""
A resolver that tokenizes the corpus and uses the tokens as a reverse index.
This reverse index is used to find the word that most likely resulted in a stemmed participant.
"""

import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '../../../')
if path not in sys.path:
	sys.path.append(path)

from ..resolver import Resolver

from vector.nlp.document import Document
from vector.nlp.tokenizer import Tokenizer

class TokenResolver(Resolver):
	"""
	The resolver looks for the words that were most likely to be stemmed to result in the participants.
	"""

	def resolve(self, participants, corpus, token_attribute="tokens", *args, **kwargs):
		"""
		Resolve the given participants by looking for the original words.

		:param participants: The participants to resolve.
		:type participants: list
		:param corpus: The corpus of documents, which helps to resolve the participants.
		:type corpus: list
		:param token_attribute: The attribute that contains the tokens.
		:type token_attribute: str

		:return: A tuple containing the resolved participants, and unresolved ones.
		:rtype: list
		"""

		tokenizer = Tokenizer(min_length=0, stem=False)
		stemmed_tokenizer = Tokenizer(min_length=0, stem=True)

		"""
		Resolve to a single word.
		For each stem, find the most common word.
		"""
		inverted_index = {}
		for document in corpus:
			text = document.get_text()
			tokens = tokenizer.tokenize(text)
			stemmed_tokens = stemmed_tokenizer.tokenize(text)
			for token, stemmed_token in list(zip(tokens, stemmed_tokens)):
				inverted_index[stemmed_token] = inverted_index.get(stemmed_token, {}) # create an entry if need be
				inverted_index[stemmed_token][token] = inverted_index.get(stemmed_token, {}).get(token, 0) + 1

		"""
		Use majority voting to find the most common word.
		"""
		for stemmed_token in inverted_index:
			inverted_index[stemmed_token] = max(inverted_index[stemmed_token].items(), key=lambda x: x[1])[0]

		"""
		Then try to resolve the participants.
		"""
		unresolved_participants, resolved_participants = [], []
		for participant in participants:
			if participant in inverted_index:
				resolved_participants.append(inverted_index.get(participant, participant).lower())
			else:
				unresolved_participants.append(participant)

		return resolved_participants, unresolved_participants
