"""
Event-based ATE approaches use either event corpora or the output timelines to score and rank domain terms.
"""

import json
import math
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ate.bootstrapping import probability
from ate.extractor import Extractor
from objects.exportable import Exportable

class EF(Extractor):
    """
    The Event Frequency (EF) extractor looks for terms in timelines.
    The scoring is based on simple frequency.
    """

    def extract(self, timelines, candidates=None):
        """
        Calculate the event frequency of terms from the given timelines.
        The event frequency is simply the number of events in which term appears in a development.

        :param timelines: The path to a timeline or a list of paths to timelines.
                          If a string is given, it is assumed to be one event timeline.
                          If a list is given, it is assumed to be a list of event timelines.
                          The timelines can also be provided loaded already.

                          .. note::

                              It is assumed that the event timelines were extracted using the collection tool.
                              Therefore each file should be a JSON string representing a :class:`~summarization.timeline.Timeline`.
        :type timelines: str or list of str or :class:`~summarization.timeline.Timeline` or list of :class:`~summarization.timeline.Timeline`
        :param candidates: A list of terms for which to calculate a score.
                           If `None` is given, all words are considered to be candidates.
        :type candidates: None or list of str

        :return: A dictionary with terms as keys and their event frequency as the values.
        :rtype: dict

        :raises ValueError: When the given data is are not timelines.
        """

        ef = { } if not candidates else dict.fromkeys(candidates, 0)

        timelines = self.to_list(timelines)
        timelines = self._load_timelines(timelines)

        for timeline in timelines:
            """
            Extract all the topical terms from the timeline.
            """
            terms = set( term for node in timeline.nodes
                              for topic in node.topics
                              for term in topic.dimensions )

            """
            Increment the event frequency of all the candidates terms—if any—in the timeline.
            """
            terms = terms if not candidates else [ term for term in terms
                                                         if term in candidates ]
            for term in terms:
                ef[term] = ef.get(term, 0) + 1

        return ef

    def _load_timelines(self, timelines):
        """
        Load the timelines if paths to files are given.

        :param timelines: A list of timelines, one for each event, or paths to timelines.
        :type timelines: list of str or list of :class:`~summarization.timeline.Timeline`

        :return: A list of timelines, loaded from files where necessary.
        :rtype: list of :class:`~summarization.timeline.Timeline`

        :raises ValueError: When the given file does not contain a timeline.
        """

        _timelines = [ ]

        for timeline in timelines:
            if type(timeline) is str:
                with open(timeline, 'r') as f:
                    data = json.loads(''.join(f.readlines()))

                    """
                    Decode the timeline.
                    """
                    data = Exportable.decode(data)
                    if 'timeline' not in data:
                        raise ValueError(f"The event frequency extractor requires a timeline file, received { ', '.join(list(data.keys())) }")
                    _timelines.append(data['timeline'])
            else:
                _timelines.append(timeline)

        return _timelines

class LogEF(EF):
    """
    The logarithmic Event Frequency (EF) extractor looks for terms in timelines.
    The scoring is the logarithm of the simple frequency, as calculated in :class:`~ate.application.event.EF`.

    .. note::

        The logarithmic base is only used to scale the ranking—it does not affect the order.
        This is because changing the logarithmic base is the same as multiplying all scores by a constant.
        Changing the base from :math:`a` to :math:`b` essentially means dividing the scores of all terms by the constant :math:`log_ba`.

    :ivar base: The logarithmic base.
    :vartype base: float
    """

    def __init__(self, base=2):
        """
        Create the logarithmic EF extractor with the logarithmic base.

        .. note::

            The logarithmic base is only used to scale the ranking—it does not affect the order.
            This is because changing the logarithmic base is the same as multiplying all scores by a constant.
            Changing the base from :math:`a` to :math:`b` essentially means dividing the scores of all terms by the constant :math:`log_ba`.

        :param base: The logarithmic base.
        :type base: float
        """

        super().__init__()
        self.base = base

    def extract(self, timelines, candidates=None):
        """
        Calculate the logarithmic event frequency of terms from the given timelines.
        The event frequency is simply the number of events in which term appears in a development.

        This weighting scheme is based on the :func:`~ate.application.event.EF` weighting scheme.

        :param timelines: The path to a timeline or a list of paths to timelines.
                          If a string is given, it is assumed to be one event timeline.
                          If a list is given, it is assumed to be a list of event timelines.

                          .. note::

                              It is assumed that the event timelines were extracted using the collection tool.
                              Therefore each file should be a JSON string representing a :class:`~summarization.timeline.Timeline`.
        :type timelines: str or list of str
        :param candidates: A list of terms for which to calculate a score.
                           If `None` is given, all words are considered to be candidates.
        :type candidates: None or list of str

        :return: A dictionary with terms as keys and their logarithmic event frequency as the values.
        :rtype: dict
        """

        timelines = self.to_list(timelines)

        extractor = EF()
        terms = extractor.extract(timelines, candidates=candidates)
        terms = { term: (math.log(value, self.base) if value else value) for term, value in terms.items() }

        return terms

class EFIDF(Extractor):
    """
    The EF-IDF extractor combines the event frequency with the inverse document frequency.
    The algorithm can be made to work with the :class:`~ate.application.event.LogEF` class instead of the :class:`~ate.application.event.EF` class by providing a logarithmic base.

    .. note::

        The logarithmic base is only used to scale the ranking—it does not affect the order.
        This is because changing the logarithmic base is the same as multiplying all scores by a constant.
        Changing the base from :math:`a` to :math:`b` essentially means dividing the scores of all terms by the constant :math:`log_ba`.

    :ivar ~.scheme: The IDF table to use to score terms.
    :vartype scheme: :class:`~nlp.weighting.global_schemes.tfidf.TFIDF`
    :ivar base: The logarithmic base.
                If it is given, the :class:`~ate.application.event.LogEF` class is used.
                Otherwise, the :class:`~ate.application.event.EF` class is used.
    :vartype base: None or float
    """

    def __init__(self, scheme, base=None):
        """
        Create the EF-IDF extractor with the scheme used to score terms and the logarithmic base.

        .. note::

            The logarithmic base is only used to scale the ranking—it does not affect the order.
            This is because changing the logarithmic base is the same as multiplying all scores by a constant.
            Changing the base from :math:`a` to :math:`b` essentially means dividing the scores of all terms by the constant :math:`log_ba`.

        :param idf: The IDF table to use to score terms.
        :type idf: :class:`~nlp.weighting.global_schemes.tfidf.TFIDF`
        :param base: The logarithmic base.
                    If it is given, the :class:`~ate.application.event.LogEF` class is used.
                    Otherwise, the :class:`~ate.application.event.EF` class is used.
        :type base: None or float
        """

        super().__init__()
        self.scheme = scheme
        self.base = base

    def extract(self, timelines, candidates=None):
        """
        Calculate the event-frequency-inverse-document-frequency metric for terms.
        This is a local-global weighting scheme.
        The local scheme is the event frequency, and the global scheme is the inverse-document-frequency.
        If a logarithmic base is provided, the logarithmic event frequency is used instead.

        :param timelines: The path to a timeline or a list of paths to timelines.
                          If a string is given, it is assumed to be one event timeline.
                          If a list is given, it is assumed to be a list of event timelines.

                          .. note::

                              It is assumed that the event timelines were extracted using the collection tool.
                              Therefore each file should be a JSON string representing a :class:`~summarization.timeline.Timeline`.
        :type timelines: str or list of str
        :param candidates: A list of terms for which to calculate a score.
                           If `None` is given, all words are considered to be candidates.
        :type candidates: None or list of str

        :return: A dictionary with terms as keys and their EF-IDF scores as the values.
        :rtype: dict
        """

        efidf = { }

        timelines = self.to_list(timelines)

        extractor = EF() if not self.base else LogEF(base=self.base)
        terms = extractor.extract(timelines, candidates=candidates)
        efidf = { term: terms[term] * self.scheme.create([ term ]).dimensions[term] for term in terms }

        return efidf

class Variability(Extractor):
    """
    Variability is a metric that measures the consistency of appearance of a term across different events.
    The variability metric is based on the number of documents in which a term appears.

    To compute variability, this class uses the chi-square statistic.
    The intuition is that terms that appear more consistently in different events are more likely to belong to the domain.

    Variability is bound between 0 and 1.
    1 is when the chi-square is 0.
    That is, 1 is when the term appears perfectly consistently across all event corpora.
    Variability tends to 0 when the chi-square tends to infinity.

    :ivar base: The logarithmic base.
    :vartype base: float
    """

    def __init__(self, base=10):
        """
        Create the variability extractor with a logarithmic base.
        This base is used because the variability score is the inverse of the chi-square.
        Therefore scores end up being very close to each other without a logarithm.

        :param base: The logarithmic base.
        :type base: float
        """

        super().__init__()

        self.base = base

    def extract(self, idfs, candidates=None):
        """
        Calculate how variable the term is across events.
        A term is highly-variable if it appears disproportionately in one or a few events.
        A low variability indicates that the term appears consistently across all events.
        To reflect this behavior in the score, the inverse of the variability is returned.

        The method follows the leave-one-out principle: each event is compared against all other events.

        :param idfs: A list of IDFs, one for each event, or paths to where they are stored.
        :type idfs: str or list of :class:`~nlp.weighting.tfidf.TFIDF`
        :param candidates: A list of terms for which to calculate a score.
                           If `None` is given, all words are considered to be candidates.
        :type candidates: None or list of str

        :return: A dictionary with terms as keys and their inverse variability score as the values.
                 A term is highly-variable if it appears disproportionately in one or a few events.
                 A low variability indicates that the term appears consistently across all events.
                 To reflect this behavior in the score, the inverse of the variability is returned.
        :rtype: dict

        :raises ValueError: When only one or no IDFs are given.
        """

        variability = { }
        idfs = self._load_idfs(idfs)

        if len(idfs) < 2:
            raise ValueError(f"Variability expects 2 or more TF-IDF schemes; received { len(idfs) }")

        """
        Calculate the number of documents across all events.
        This is the size of the contingency table.
        """
        all_documents = sum(idf.global_scheme.documents for idf in idfs)

        """
        Go through each term and compute the variability.
        For each event, compare the appearance of the term in the event with its appearance in other events.
        """
        vocabulary = candidates or self._vocabulary(idfs)
        for term in vocabulary:
            v = 0
            for idf in idfs:
                """
                Create the contingency table and compute the chi-square value.
                """
                comparison = [ other for other in idfs if other is not idf ]
                table = self._contingency_table(term, idf, comparison)
                chi = self._chi(table)
                v += chi

            variability[term] = 1./math.log(v + self.base, self.base)

        return variability

    def _load_idfs(self, idfs):
        """
        Load the IDFs if paths to files are given.

        :param idfs: A list of IDFs, one for each event, or paths to IDFs.
        :type idfs: list of str or list of :class:`~nlp.weighting.tfidf.TFIDF`

        :return: A list of TF-IDF schemes, loaded from files where necessary.
        :rtype: list of :class:`~nlp.weighting.tfidf.TFIDF`

        :raises ValueError: When the given file does not contain a TF-IDF scheme.
        """

        _idfs = [ ]

        for idf in idfs:
            if type(idf) is str:
                with open(idf, 'r') as f:
                    data = json.loads(''.join(f.readlines()))

                    """
                    Decode the TF-IDF scheme.
                    """
                    data = Exportable.decode(data)
                    if 'tfidf' not in data:
                        raise ValueError(f"The variability extractor requires a TF-IDF file, received { ', '.join(list(data.keys())) }")
                    _idfs.append(data['tfidf'])
            else:
                _idfs.append(idf)

        return _idfs

    def _vocabulary(self, idfs):
        """
        Extract the vocabulary from the given IDFs.

        :param idfs: A list of IDFs, one for each event.
        :type idfs: list of :class:`~nlp.weighting.tfidf.TFIDF`

        :return: A list of terms in the given IDFs.
        :rtype: list of str
        """

        vocabulary = [ ]
        for idf in idfs:
            vocabulary.extend(list(idf.global_scheme.idf.keys()))

        return list(set(vocabulary))

    def _contingency_table(self, term, current, comparison):
        """
        Create the contingency table comparing the term's appearance in the current event versus other events.

        :param term: The term for which to create the contingency table.
        :type term: str
        :param current: The current event's IDF table.
        :type current: :class:`~nlp.weighting.tfidf.TFIDF`
        :param comparison: A list of IDFs, one for each event.
        :type comparison: list of :class:`~nlp.weighting.tfidf.TFIDF`

        :return: The contingency table for the term, contrasting the current event with all other events.
                 The first row is the total number of documents in the current event.
                 The second row is the total number of documents in the comparison events.
                 The totals of both rows sum up to the total number of documents.
                 The contingency table is returned as a tuple with four floats.
                 These correspond to the first and second rows respectively.
        :rtype: tuple of float
        """

        current_documents = current.global_scheme.documents
        comparison_documents = sum(idf.global_scheme.documents for idf in comparison)

        """
        `A` is the number of current event documents in which the term appears.
        """
        A = current.global_scheme.idf.get(term, 0)

        """
        `B` is the number of current event documents in which the term does not appear
        """
        B = current_documents - A

        """
        `C` is the number of other events in which the term appears.
        It is computed as the number of times the term appears in all events minus `A`.
        """
        C = sum(idf.global_scheme.idf.get(term, 0) for idf in comparison)

        """
        `D` is the number of other events in which the term does not appear.
        """
        D = comparison_documents - C

        return (A, B, C, D)

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

class Entropy(Extractor):
    """
    Entropy is a metric that measures the consistence of appearance of a term across different events.
    The entropy metric is based on the number of documents in which a term appears.

    Information entropy measures 'surprise'.
    If a variable's possible outcomes are all equally-positive, then entropy is at its maximum.
    If one of the outcomes is more possible than any other outcome, then the variable is not as surprising, and therefore has a lower entropy.

    This class' intuition is that if a term is equally-distributed across events (and thus has a high entropy), it belongs to the domain.
    Therefore the higher the entropy, the better.

    The entropy of a term :math:`s` is calculated as following:

    .. math::

        H_b(s) = - \\sum_{i=1}^{n} p_i log_bp_i

    where :math:`b` is the logarithmic base.
    :math:`n` is the number of possible outcomes of the term.
    In this case, :math:`n` is the number of events, so the entropy is the term's distribution across events.

    :ivar base: The logarithmic base.
    :vartype base: float
    """

    def __init__(self, base=10):
        """
        Create the entropy extractor with a logarithmic base.
        This base is used to calculate the information entropy score.

        :param base: The logarithmic base.
        :type base: float
        """

        super().__init__()

        self.base = base

    def extract(self, idfs, candidates=None):
        """
        Calculate the entropy score for the given candidate terms.

        :param idfs: A list of IDFs, one for each event.
        :type idfs: list of :class:`~nlp.weighting.tfidf.TFIDF`
        :param candidates: A list of terms for which to calculate a score.
                           If `None` is given, all words are considered to be candidates.
        :type candidates: None or list of str

        :return: A dictionary with terms as keys and their entropy score as the values.
                 A term that has a high entropy is equally common across all events.
                 A term that has a low entropy indicates that the term appears inconsistently across events.
        :rtype: dict

        :raises ValueError: When only one or no IDFs are given.
        """

        entropy = { }
        idfs = self._load_idfs(idfs)
        if len(idfs) < 2:
            raise ValueError(f"Variability expects 2 or more TF-IDF schemes; received { len(idfs) }")

        """
        Go through each term and compute the entropy.
        For each event, compare the appearance of the term in the event with its appearance in other events.
        """
        vocabulary = candidates or self._vocabulary(idfs)
        entropy = dict.fromkeys(vocabulary, 0)
        for term in vocabulary:
            p = self._probabilities(idfs, term)
            entropy[term] = self._entropy(p)

        return entropy

    def _load_idfs(self, idfs):
        """
        Load the IDFs if paths to files are given.

        :param idfs: A list of IDFs, one for each event, or paths to IDFs.
        :type idfs: list of str or list of :class:`~nlp.weighting.tfidf.TFIDF`

        :return: A list of TF-IDF schemes, loaded from files where necessary.
        :rtype: list of :class:`~nlp.weighting.tfidf.TFIDF`

        :raises ValueError: When the given file does not contain a TF-IDF scheme.
        """

        _idfs = [ ]

        for idf in idfs:
            if type(idf) is str:
                with open(idf, 'r') as f:
                    data = json.loads(''.join(f.readlines()))

                    """
                    Decode the TF-IDF scheme.
                    """
                    data = Exportable.decode(data)
                    if 'tfidf' not in data:
                        raise ValueError(f"The entropy extractor requires a TF-IDF file, received { ', '.join(list(data.keys())) }")
                    _idfs.append(data['tfidf'])
            else:
                _idfs.append(idf)

        return _idfs

    def _vocabulary(self, idfs):
        """
        Extract the vocabulary from the given IDFs.

        :param idfs: A list of IDFs, one for each event.
        :type idfs: list of :class:`~nlp.weighting.tfidf.TFIDF`

        :return: A list of terms in the given IDFs.
        :rtype: list of str
        """

        vocabulary = [ ]
        for idf in idfs:
            vocabulary.extend(list(idf.global_scheme.idf.keys()))

        return list(set(vocabulary))

    def _probabilities(self, idfs, term):
        """
        Calculate the probability distribution of the term across all events.

        :param idfs: A list of IDFs, one for each event.
        :type idfs: list of :class:`~nlp.weighting.tfidf.TFIDF`
        :param term: The candidate term for which to calculate the total number off mentions.
        :type term: str

        :return: A list of probabilities of the term across all events.
        :rtype: list of float
        """

        p = [ ]

        total = self._total(idfs, term)
        if not total:
            return [ 0 ] * len(idfs)

        p = [ idf.global_scheme.idf.get(term, 0) / total for idf in idfs]
        return p

    def _total(self, idfs, term):
        """
        Get the total number of mentions of the term across all events.

        :param idfs: A list of IDFs, one for each event.
        :type idfs: list of :class:`~nlp.weighting.tfidf.TFIDF`
        :param term: The candidate term for which to calculate the total number off mentions.
        :type term: str

        :return: The total number of mentions of the term across all events.
        :rtype: float
        """

        return sum(idf.global_scheme.idf.get(term, 0) for idf in idfs)

    def _entropy(self, probabilities):
        """
        Calculate the entropy of the given probabilities.
        The entropy of a term :math:`s` is calculated as following:

        .. math::

            H_b(s) = - \\sum_{i=1}^{n} p_i log_bp_i

        where :math:`b` is the logarithmic base.
        :math:`n` is the number of possible outcomes of the term.
        In this case, :math:`n` is the number of events, so the entropy is the term's distribution across events.

        :param probabilities: A list of probabilities.
        :type probabilities: list of float

        :return: The entropy of the given probabilities.
        :rtype: float
        """

        probabilities = [ p for p in probabilities if p ]

        return - sum( p * math.log(p, self.base) for p in probabilities )
