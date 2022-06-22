"""
Text mining tasks generally depend a lot on the document representation.
EvenTDT provides functionality to make it easier to work with documents:

1. The :class:`~nlp.document.Document` class, based on the :class:`~vsm.vector.Vector` class, but with text-specific functionality;
2. The :class:`~nlp.tokenizer.Tokenizer` class to split a piece of text into tokens; and
3. The :class:`~nlp.weighting.TermWeightingScheme` abstract class, as well as different term-weighting schemes, to assign weight to terms.
"""

import nltk
import re

from .document import Document
from .tokenizer import Tokenizer

def entities(text, entity_type=None):
    """
    Extract the named entities from the given text.
    The function uses NLTK to extract entities.

    :param text: The text from which to extract named entities.
    :type text: str
    :param entity_type: The type of named entity to extract.
                        The function accepts the same types as NLTK, namely _PERSON_, _GPE_ or _ORGANIZATION_.
                        If no type is given, the function returns all named entities irrespective of type.
    :type entity_type: str

    :return: A list of named entities and their types.
    :rtype: list of tuple
    """

    entities = [ ]

    # split the text into sentences, and extract the named entities from each sentence
    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        tokens = nltk.word_tokenize(sentence)
        pos_tags = nltk.pos_tag(tokens)
        chunks = nltk.ne_chunk(pos_tags, binary=False)
        entities.extend(_combine_adjacent_entities(chunks))

    if not entity_type:
        return entities

    return [ (entity, _type) for entity, _type in entities
                             if _type == entity_type.upper() ]

def _combine_adjacent_entities(chunks):
    """
    Combine the chunks appearing in the given list.
    The function assumes that the list represents one sentence.
    If two tokens next to each other have the same type, the function combines them into a single string.
    The function returns only the named entities.

    :param chunks: The list of chunks.
    :type chunks: list of str or nltk.tree.Tree

    :return: A list of named entities and their types.
    :rtype: list of tuple
    """

    named_entities = [ ]

    """
    Iterate over each chunk.
    If a chunk is an entity, then start building a named entity.
    This is interrupted whenever a chunk is not an entity, or if it has a different type.
    """
    entity, entity_type = [ ], None
    for chunk in chunks:
        if type(chunk) is nltk.tree.Tree:
            """
            If the type of named entity has changed, retire it.
            This means adding the sequence to the list of named entities, and resetting the memory.
            """
            label = chunk.label()
            if label != entity_type:
                named_entities.append((' '.join(entity).strip(), entity_type))
                entity, entity_type = [], None

            # add the tokens to the named entity sequence
            entity_type = label
            named_entity_tokens = [ pair[0] for pair in chunk ]
            entity.extend(named_entity_tokens)
        else:
            named_entities.append((' '.join(entity).strip(), entity_type))
            entity, entity_type = [], None

    """
    Save the last named entity.
    Filter out named entities that have no length.
    """
    named_entities.append((' '.join(entity).strip(), entity_type))
    named_entities = [ (entity, entity_type) for (entity, entity_type) in named_entities if len(entity) ]

    return named_entities

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
