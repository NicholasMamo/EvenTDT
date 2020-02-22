"""
The Named Entity Recognition (NER) participant detector is one that assumes that all participants are named entities.
This participant detector does not seek to resolve named entities or extrapolate.
It simply extracts named entities and ranks them based on frequency.
Due to its simplicity, the NER participant detector is also a baseline for APD.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.append(path)

from participant_detector import ParticipantDetector
from extractors.local.entity_extractor import EntityExtractor
from scorers.local.tf_scorer import TFScorer

class NERParticipantDetector(ParticipantDetector):
	"""
	The Named Entity Recognition (NER) participant detector extracts named entities from the corpus.
	The NER participant detector is based on a normal participant detector.
	It uses the :class:`apd.extractors.local.entity_extractor.EntityExtractor` to extract named entities.
	The frequency is computed using the :class:`apd.scorers.local.tf_scorer.TFScorer`
	"""

	def __init__(self):
		"""
		Create the NER participant detector.
		"""

		super().__init__(EntityExtractor(), TFScorer())
