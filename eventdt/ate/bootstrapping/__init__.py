"""
Bootstrapping is a process that can follow ATE.
Starting from a seed set of terms, bootstrapping looks for semantically-similar terms.

This package provides a skeleton structure of what bootstrapping algorithms should be able to do.
"""

from abc import ABC, abstractmethod

class Bootstrapper(ABC):
    """
    A bootstrapper must provide functionality to bootstrap.
    Starting from a seed set and a corpus, or a list of corpora, a bootstrapper looks for semantically-similar terms.

    Bootstrapping is implemented as all possible combinations of a seed set terms and candidate terms.
    Therefore the main :func:`~ate.bootstrapping.Bootstrapper.bootstrap` function returns a dictionary of scores.
    Each score represents a seed set term's score for a candidate.
    """

    @abstractmethod
    def bootstrap(self, corpora, seed=None, candidates=None):
        """
        Using the given seed set of terms, look for semantically-similar terms in the given corpora.

        :param corpora: A corpus, or corpora, of documents.
                        If a string is given, it is assumed to be one corpus.
                        If a list is given, it is assumed to be a list of corpora.

                        .. note::

                            It is assumed that the corpora were extracted using the tokenizer tool.
                            Therefore each line should be a JSON string representing a document.
                            Each document should have a `tokens` attribute.
        :type corpora: str or list of str
        :param seed: The terms for which to compute the probability.
                     These terms are combined as a cross-product with all terms in `candidates`.
                     The terms can be provided as:

                     - A single word,
                     - A list of terms,
                     - A tuple, or
                     - A list of tuples.

                     A tuple translates to joint probabilities.
                     If nothing is given, it is replaced with the corpora's vocabulary.
        :type seed: None or str or list of str or tuple or list of tuple
        :param candidates: The terms for which to compute the probability.
                           These terms are combined as a cross-product with all terms in `seed`.
                           The terms can be provided as:

                           - A single word,
                           - A list of terms,
                           - A tuple, or
                           - A list of tuples.

                           A tuple translates to joint probabilities.
                           If nothing is given, it is replaced with the corpora's vocabulary.
        :type candidates: None or str or list of str or tuple or list of tuple

        :return: The scores of each seed term for each candidate.
                 Bootstrapping computes a score for the cross-product of the seed set and candidates.
                 In other words, there is a score for every possible combination of terms in the seed set, and terms in the candidates.
                 The scores are returned as a dictionary.
                 The keys are these pairs, and the values are their scores.
        :rtype: dict
        """

        pass

    def to_list(self, corpora):
        """
        Convert the given corpora to a list of corpora.
        This function can be invoked when the input is either a list or a single path.
        If a list of corpora is provided, this function returns the original input.

        :param corpora: A path to a corpus or paths to corpora.
        :type corpora: str or list of str

        :return: A list of corpora.
        :rtype: list of str
        """

        return corpora if type(corpora) is list else [ corpora ]

class DummyBootstrapper(Bootstrapper):
    """
    A dummy bootstrapper that does nothing and returns an empty dictionary of bootstrapped terms.
    It is used only for testing purposes.
    """

    def bootstrap(self, corpora, seed=None, candidates=None):
        """
        Using the given seed set of terms, look for semantically-similar terms in the given corpora.

        :param corpora: A corpus, or corpora, of documents.
                        If a string is given, it is assumed to be one corpus.
                        If a list is given, it is assumed to be a list of corpora.

                        .. note::

                            It is assumed that the corpora were extracted using the tokenizer tool.
                            Therefore each line should be a JSON string representing a document.
                            Each document should have a `tokens` attribute.
        :type corpora: str or list of str
        :param seed: The terms for which to compute the probability.
                     These terms are combined as a cross-product with all terms in `candidates`.
                     The terms can be provided as:

                     - A single word,
                     - A list of terms,
                     - A tuple, or
                     - A list of tuples.

                     A tuple translates to joint probabilities.
                     If nothing is given, it is replaced with the corpora's vocabulary.
        :type seed: None or str or list of str or tuple or list of tuple
        :param candidates: The terms for which to compute the probability.
                           These terms are combined as a cross-product with all terms in `seed`.
                           The terms can be provided as:

                           - A single word,
                           - A list of terms,
                           - A tuple, or
                           - A list of tuples.

                           A tuple translates to joint probabilities.
                           If nothing is given, it is replaced with the corpora's vocabulary.
        :type candidates: None or str or list of str or tuple or list of tuple

        :return: The scores of each seed term for each candidate.
                 Bootstrapping computes a score for the cross-product of the seed set and candidates.
                 In other words, there is a score for every possible combination of terms in the seed set, and terms in the candidates.
                 The scores are returned as a dictionary.
                 The keys are these pairs, and the values are their scores.
        :rtype: dict
        """

        return { }
