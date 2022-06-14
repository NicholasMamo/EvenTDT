"""
The term frequency (TF) scorer assigns a score to candidate participants based on the number of times in which they appear.
Unlike the :class:`~apd.scorers.local.df_scorer.DFScorer`, candidates that appear several times in the same document are boosted.
"""

import math

from ..scorer import Scorer

class TFScorer(Scorer):
    """
    The term frequency scorer counts the number of times a candidate participant appears in the event corpus.
    This becomes the candidate participant's score.
    """

    def score(self, candidates, *args, **kwargs):
        """
        Score the given candidates based on their relevan across all documentsce within the corpus.
        The score is normalized using the maximum score

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
        Score the given candidates based on the number of times they appear across all documents—a simple summation.

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
            for candidate in list(candidate_set):
                scores[candidate] = scores.get(candidate, 0) + 1

        return scores
