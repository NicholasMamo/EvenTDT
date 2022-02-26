"""
The rank filter extracts the top _k_ candidates.
Anything else is filtered out.
"""

import math

from ..filter import Filter

class RankFilter(Filter):
    """
    The rank filter is used to extract the top _k_ candidates.
    The _k_ parameter is passed on to the constructor and stored as an instance variable.
    It is then re-used by the :func:`~apd.filters.local.rank_filter.RankFilter.filter` method.

    :vartype keep: The number of candidates to retain.
    :vartype keep: int
    """

    def __init__(self, keep=10, *args, **kwargs):
        """
        Create the filter with the keep that will decide whether candidate participants will be retained.

        :param keep: The number of candidates to retain.
        :type keep: int

        :raises ValueError: When _k_ is not an integer.
        :raises ValueError: When _k_ is not positive.
        """

        if type(keep) is not int:
            raise ValueError(f"keep must be an integer; received {keep} ({ type(keep) })")

        if keep <= 0:
            raise ValueError(f"keep must be a positive integer; received {keep}")

        self.keep = keep

    def filter(self, candidates, *args, **kwargs):
        """
        Filter candidate participants that are not credible.
        The function sorts the candidates by score and then retains only the top _k_ candidates.

        :param candidates: A dictionary of candidate participants and their scores.
                           The keys are the candidate names, and the values are their scores.
                           The input candidates should be the product of a :class:`~apd.scorers.scorer.Scorer` process.
        :type candidates: dict

        :return: A dictionary of filtered candidate participants and their associated scores.
        :rtype: dict
        """

        retain = sorted(candidates, key=candidates.get, reverse=True)[:self.keep]
        return { candidate: candidates.get(candidate) for candidate in retain }
