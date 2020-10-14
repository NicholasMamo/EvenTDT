"""
A scorer is used to test the quality, or otherwise quantitatively evaluate the score of a :class:`~vector.nlp.document.Document`.
The most basic type of scorer.
"""

class Scorer(object):
    """
    The simplest scorer simply returns a non-zero positive constant.
    In this way, the scorer does not discriminate between different objects.
    """

    def score(self, document, token_attribute="tokens"):
        """
        Evaluate the score of the given document.
        This is the function that is usually overridden by more specific classes.

        :param document: The document that will be scored.
        :type document: :class:`~vector.nlp.document.Document`
        :param token_attribute: The attribute that contains the tokens.
        :type token_attribute: str

        :return: The document's score.
            In the most basic scorer, this is a non-zero positive constant.
        :rtype: int
        """

        return 1
