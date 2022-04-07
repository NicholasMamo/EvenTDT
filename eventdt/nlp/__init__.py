"""
Text mining tasks generally depend a lot on the document representation.
EvenTDT provides functionality to make it easier to work with documents:

1. The :class:`~nlp.document.Document` class, based on the :class:`~vsm.vector.Vector` class, but with text-specific functionality;
2. The :class:`~nlp.tokenizer.Tokenizer` class to split a piece of text into tokens; and
3. The :class:`~nlp.weighting.TermWeightingScheme` abstract class, as well as different term-weighting schemes, to assign weight to terms.
"""

import re

from .document import Document
from .tokenizer import Tokenizer

def remove_parentheses(text):
    """
    Remove parentheses from the given text.

    .. note::

        The function does not use a regular expression since parentheses can be—and often are—nested.
        The complexity remains :math:`O(n)`, where :math:`n` is the number of characters in the text

    :param text: The text to clean.
    :type text: str

    :return: The cleaned text.
    :rtype: str
    """

    clean = ""

    parenthesis = "" # the current parenthesis container
    depth = 0 # the parenthesis depth (for nested parentheses)
    for char in text:
        if char == '(':
            depth += 1

        if not depth:
            clean += char

        if char == ')':
            depth -= 1

    # collapse multiple spaces into one
    pattern = re.compile('\s+')
    clean = pattern.sub(' ', clean)

    # remove spaces before punctuation
    pattern = re.compile('\s([.,\/!\^\*;:}_~)])')
    clean = pattern.sub('\g<1>', clean)

    return clean

def has_year(text):
    """
    Check whether the given text has a year in it.

    :param text: The text of the article.
    :type text: str

    :return: A boolean indicating whether the text includes a year in it.
    :rtype: bool
    """

    year_pattern = re.compile("\\b[0-9]{4}\\b")
    return len(year_pattern.findall(text)) > 0
