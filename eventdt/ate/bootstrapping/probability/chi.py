"""
The chi-square statistic measures how often two variables appear in together.
It is calculated using a two-by-two contingency table as:

.. math::

    CHI(x, y) = \\frac{(A + B + C + D) \\times (A \\times D - C \\times B)^2}{(A + C) \\times (B + D) \\times (A + B) \\times (C + D) )}

To calculate the chi-square statistic, this algorithm uses a contingency table:

+-------------------------+-------------------------+-------------------------+
|                         || :math:`t_1`            | :math:`\\overline{t_1}`  |
+=========================+=========================+=========================+
| :math:`t_2`             || A                      | B                       |
+-------------------------+-------------------------+-------------------------+
| :math:`\\overline{t_2}`  || C                      | D                       |
+-------------------------+-------------------------+-------------------------+

In this table, the cells represent the following:

- `A`: terms :math:`t_1` and :math:`t_2` co-occur;
- `B`: terms :math:`t_2` appears, but :math:`t_1` doesn't;
- `C`: terms :math:`t_1` appears, but :math:`t_2` doesn't; and
- `D`: neither terms :math:`t_1` nor :math:`t_2` appear.
"""

import json
import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

import ate
from ate import linguistic
from ate.bootstrapping import Bootstrapper
from ate.stat import probability
from nlp import Document
from objects.exportable import Exportable
from summarization.timeline import Timeline

class ChiBootstrapper(Bootstrapper):
    """
    The chi-square bootstrapper scores candidate terms based on how often they appear with seed terms.
    """

    def bootstrap(self, corpora, seed=None, candidates=None, cache=None):
        """
        Calculate the chi-square statistic of co-occurrence for the seed set terms and the candidate terms.

        :param corpora: A corpus, or corpora, of documents.
                        If a string is given, it is assumed to be one corpus.
                        If a list is given, it is assumed to be a list of corpora.

                        .. note::

                            It is assumed that the corpora were extracted using the tokenizer tool.
                            Therefore each line should be a JSON string representing a document.
                            Each document should have a `tokens` attribute.
        :type corpora: str or list of str
        :param seed: The terms for which to compute the chi-square statistic.
                     These terms are combined as a cross-product with all terms in ``candidates``.
                     The terms can be provided as:

                     - A single word,
                     - A list of terms,
                     - A tuple, or
                     - A list of tuples.

                     A tuple translates to joint probabilities.
                     If nothing is given, it is replaced with the corpora's vocabulary.
        :type seed: None or str or list of str or tuple or list of tuple
        :param candidates: The terms for which to compute the chi-square statistic.
                           These terms are combined as a cross-product with all terms in ``seed``.
                           The terms can be provided as:

                           - A single word,
                           - A list of terms,
                           - A tuple, or
                           - A list of tuples.

                           A tuple translates to joint probabilities.
                           If nothing is given, it is replaced with the corpora's vocabulary.
        :type candidates: None or str or list of str or tuple or list of tuple
        :param cache: A list of terms that are re-used often and which should be cached.
                      If an empty list or ``None`` is given, no cache is used.

                      .. note::

                          Cache should be used when there is a lot of repetition.
                          For example, ``seed`` can be used as cache when ``seed`` is small and ``candidates`` is large.
                          If the data is small, using cache can be detrimental.
        :type cache: None or list of str

        :return: The scores of each seed term for each candidate.
                 Bootstrapping computes a score for the cross-product of the seed set and candidates.
                 In other words, there is a score for every possible combination of terms in the seed set, and terms in the candidates.
                 The chi-square statistic scores are returned as a dictionary.
                 The keys are these pairs, and their chi-square statistics are the values.
        :rtype: dict
        """

        chi = { }

        """
        Convert the corpora and tokens into a list if they aren't already.
        The list of seed terms and candidates is always made into a list, even if it's a list of one string.
        """
        corpora = self.to_list(corpora)
        seed = [ seed ] if type(seed) is str else seed
        candidates = [ candidates ] if type(candidates) is str else candidates

        """
        Create the contingency tables and calculate the chi-square statistic for each pair.
        """
        tables = self._contingency_table(corpora, seed, candidates, cache=cache)
        chi = { pair: self._chi(table) for pair, table in tables.items() }

        return chi

    def _contingency_table(self, corpora, seed, candidates, cache=None):
        """
        Create the contingency tables for all the pairs of terms in ``seed`` and ``candidates``.
        All the terms in ``seed`` are matched with all terms in ``candidates`` in a cross-product fashion.

        :param corpora: A corpus, or corpora, of documents.
                        If a string is given, it is assumed to be one corpus.
                        If a list is given, it is assumed to be a list of corpora.

                        .. note::

                            It is assumed that the corpora were extracted using the tokenizer tool.
                            Therefore each line should be a JSON string representing a document.
                            Each document should have a `tokens` attribute.
        :type corpora: str or list of str
        :param seed: The terms for which to compute the chi-square statistic.
                     These terms are combined as a cross-product with all terms in ``candidates``.
                     The terms can be provided as:

                     - A single word,
                     - A list of terms,
                     - A tuple, or
                     - A list of tuples.

                     A tuple translates to joint probabilities.
                     If nothing is given, it is replaced with the corpora's vocabulary.
        :type seed: None or str or list of str or tuple or list of tuple
        :param candidates: The terms for which to compute the chi-square statistic.
                           These terms are combined as a cross-product with all terms in ``seed``.
                           The terms can be provided as:

                           - A single word,
                           - A list of terms,
                           - A tuple, or
                           - A list of tuples.

                           A tuple translates to joint probabilities.
                           If nothing is given, it is replaced with the corpora's vocabulary.
        :type candidates: None or str or list of str or tuple or list of tuple
        :param cache: A list of terms that are re-used often and which should be cached.
                      If an empty list or ``None`` is given, no cache is used.

                      .. note::

                          Cache should be used when there is a lot of repetition.
                          For example, ``seed`` can be used as cache when ``seed`` is small and ``candidates`` is large.
                          If the data is small, using cache can be detrimental.
        :type cache: None or list of str

        :return: A dictionary of contingency tables.
                 The keys are the pairs of the terms.
                 The values are four-tuples representing the values of cells in the order:

                     1. Top-left,
                    2. Top-right,
                    3. Bottom-left, and
                    4. Bottom-right.
        :rtype: dict
        """

        tables = { }

        """
        Convert the corpora and terms into a list if they aren't already.
        """
        corpora = [ corpora ] if type(corpora) is str else corpora
        seed = [ seed ] if type(seed) is str else seed
        candidates = [ candidates ] if type(candidates) is str else candidates
        cache = cache or [ ]
        cache = [ cache ] if type(cache) is str else cache

        """
        Get the total number of documents in the corpora.
        Initially, the term counts will be calculated only for terms that are not cached.
        The term counts for terms that are cached can be calculated in the cache routine.
        """
        total = ate.total_documents(corpora)
        counts = ate.total_documents(corpora, focus=list(set(seed + candidates)))

        """
        Generate the pairs for which the chi-square statistic will be computed.
        Then, initialize the contingency table for each pair.
        """
        pairs = probability.joint_vocabulary(seed, candidates)
        tables = { pair: (0, 0, 0, 0) for pair in pairs }

        """
        If cache is defined, generate a list of documents for each cached term.
        This reduces the number of documents to go over.
        """
        if cache:
            for term in cache:
                """
                Look for pairs that mention the cached term.
                """
                cached_pairs = [ pair for pair in pairs if term in pair ]

                """
                Create the cache.
                Update the A in the tables for the cached term.
                This value represents the number of documents in which both the cached term and the other term appear.
                """
                documents = probability.cached(corpora, term)
                for document in documents:
                    is_document = type(document) is Document
                    for a, b in cached_pairs:
                        if ((not is_document and a in document['tokens'] and b in document['tokens']) or
                            (is_document and a in document.dimensions and b in document.dimensions)):
                            A, B, C, D = tables[(a, b)]
                            A += 1
                            tables[(a, b)] = (A, B, C, D)

                """
                Complete the contingency tables.
                """
                for (a, b) in cached_pairs:
                     A, B, C, D = tables[(a, b)]
                     B = counts[a] - A # documents in which the first term appears without the second term
                     C = counts[b] - A # documents in which the second term appears without the first term
                     D = total - (A + B + C) # documents in which neither the first nor the second term appears
                     tables[(a, b)] = (A, B, C, D)

                """
                Remove the already-created contingency tables from the pairs.
                """
                pairs = [ pair for pair in pairs if term not in pair ]

        """
        Create any remaining contingency tables.
        """
        if pairs:
            for corpus in corpora:
                with open(corpus, 'r') as f:
                    if ate.datatype(corpus) is Timeline:
                        timeline = Exportable.decode(json.loads(f.readline()))['timeline'] # load the timeline
                        for document in [ document for node in timeline.nodes for document in node.get_all_documents() ]:
                            for a, b in pairs:
                                if a in document.dimensions and b in document.dimensions:
                                    A, B, C, D = tables[(a, b)]
                                    A += 1
                                    tables[(a, b)] = (A, B, C, D)
                    else:
                        for line in f:
                            document = json.loads(line)
                            for a, b in pairs:
                                if a in document['tokens'] and b in document['tokens']:
                                    A, B, C, D = tables[(a, b)]
                                    A += 1
                                    tables[(a, b)] = (A, B, C, D)

            """
            Complete the contingency tables.
            """
            for (a, b) in pairs:
                 A, B, C, D = tables[(a, b)]
                 B = counts[a] - A # documents in which the first term appears without the second term
                 C = counts[b] - A # documents in which the second term appears without the first term
                 D = total - (A + B + C) # documents in which neither the first nor the second term appears
                 tables[(a, b)] = (A, B, C, D)

        return tables

    def _chi(self, table):
        """
        Calculate the chi-square statistic from the given table.
        The chi-square statistic is 0 if the two variables are independent.
        The higher the statistic, the more dependent the two variables are.

        :param table: The contingency table as a four-tuple.
                      The values are four-tuples representing the values of cells in the order:

                          1. Top-left,
                         2. Top-right,
                         3. Bottom-left, and
                         4. Bottom-right.
        :type table: tuple of int

        :return: The chi-square statistic.
        :rtype: float
        """

        N = sum(table)
        A, B, C, D = table

        """
        If any value in the denominator is 0, return 0.
        This is an unspecified case that results in division by 0.
        """
        if not all([ A + C, B + D, A + B, C + D ]):
            return 0

        return ((N * (A * D - C * B) ** 2) /
                ( (A + C) * (B + D) * (A + B) * (C + D) ))
