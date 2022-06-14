"""
The document frequency (DF) scorer assigns a score to candidate participants based on the number of documents in which they appear.
This approach does not favor candidates if they appear multiple times in the same document.
"""

import math

from ..scorer import Scorer

class DFScorer(Scorer):
    """
    The document frequency scorer counts the number of documents in which each candidate participant appears.
    This becomes the candidate participant's score.
    """

    def score(self, candidates, *args, **kwargs):
        """
        Score the given candidates based on their relevance within the corpus.
        The score is normalized using the maximum score.

        :param candidates: A list of candidates participants that were found earlier.
        :type candidates: list

        :return: A dictionary of participants and their associated scores.
        :rtype: dict
        """

        candidates = self._fold(candidates)
        scores = self._sum(candidates, *args, **kwargs)
        return self._normalize(scores) if self.normalize_scores else scores

    def _sum(self, candidates, *args, **kwargs):
        """
        Score the given candidates based on the number of times they appear—a simple summation.

        :param candidates: A list of candidates participants that were found earlier.
        :type candidates: list

        :return: A dictionary of candidate participants and their scores.
        :rtype: dict
        """

        scores = {}

        """
        Go through each document, and then each of its candidate participants.
        For all of these instances, increment their score.
        """
        for candidate_set in candidates:
            for candidate in list(set(candidate_set)):
                scores[candidate] = scores.get(candidate, 0) + 1

        return scores
