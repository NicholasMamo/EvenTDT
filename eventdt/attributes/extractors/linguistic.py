"""
The linguistic extractor extracts attributes based on a few grammatical rules that make up a shallow parser.
As usual, the functionality revolves around the :class:`~attributes.extractors.linguistic.LinguisticExtractor`'s :func:`~attributes.extractors.linguistic.LinguisticExtractor.extract` method.

The default grammar assumes that attributes are defined using verbs, and attribute values are nouns.
However, the default grammar can be overriden in the :func:`constructor <attributes.extractors.linguistic.LinguisticExtractor.__init__>`.

This extractor assumes that the text is about a single entity and therefore does not seek to confirm who the attributes are discussing.
"""

import os
import sys

path = os.path.dirname(__file__)
path = os.path.join(path, '..', '..')
if path not in sys.path:
    sys.path.append(path)

import nltk

from attributes import Profile
from attributes.extractors import Extractor

class LinguisticExtractor(Extractor):
    """
    The linguistic extractor accepts an optional grammar and uses it to extract attributes from text.
    The grammar can either be defined in the constructor or, if not given, it is defined automatically by the class.

    .. note::

        More details about the grammar are available `here <https://www.guru99.com/pos-tagging-chunking-nltk.html>`_.

    :ivar parser: The parser to use to extract attributes.
    :vartype parser: :class:`nltk.RegexpParser`
    """

    def __init__(self, grammar=None):
        """
        Create the linguistic extractor with an optional grammar.
        If a grammar is not given, a default grammar is used instead:

        - :math:`ENT: <CD|NNP.*>*?<NNP.*><CD|NNP.*>*` - An entity can start with (`1860 Munich`) or end with a number (`Schalke 04`), but it must always include at least one proper noun.
        """

        grammar = grammar or """
                  JJMOD: { <JJ.*>(<CC|,><JJ.*>)* }
                  ENT: { <CD|NNP.*>*? <NNP.*> (<IN>? <CD|NNP.*>)* }
                  MOD: { <JJMOD|RB.*>* }
                  NP: { <MOD>?<VBG>?<NN.*>+ }
                  NAME: { <VB.*> }
                  VALUE: { <NP|ENT>+ }
                  PPATTR: { <IN>?(<DT>?<VALUE><CC|,>?)+ }
                  ATTR: { <NAME><MOD>?<PPATTR>+ }
        """
        self.parser = nltk.RegexpParser(grammar)

    def extract(self, text, *args, **kwargs):
        """
        Extract attributes from the given text.
        This function assumes that the text is about a single entity and therefore does not seek to confirm who the attributes are discussing.

        Any additional arguments and keyword arguments are passed on to the :class:`~attributes.profile.Profile` :func:`constructor <~attributes.profile.Profile.__init__>`.

        :param text: The text from where to extract attributes.
        :type text: str

        :return: A profile of attributes.
                 Each attribute may have a list of values.
        :rtype: :class:`~attributes.profile.Profile`
        """

        profile = Profile(*args, **kwargs)

        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            tree = self._parse(sentence)
            ATTR = self._attribute_subtrees(tree)
            for _ATTR in ATTR:
                NAME, PPATTR = self._to_attributes(_ATTR)
                for _PPATTR in PPATTR:
                    IN = self._get_preposition(_PPATTR)
                    name = f"{NAME}_{ IN }" if IN else NAME
                    profile.attributes[name] = profile.attributes.get(name) or set()
                    attributes = self._get_attribute(_PPATTR)
                    for attribute in attributes:
                        profile.attributes[name].add(self._attribute_value(attribute))

        return profile

    def _parse(self, sentence):
        """
        Parse the given sentence, creating a tree.

        :param sentence: The sentence to parse.
        :type sentence: str

        :return: A parsed sentence in the form of a POS tree.
        :rtype: :class:`nltk.tree.Tree`
        """

        tokens = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(tokens)
        return self.parser.parse(tagged)

    def _attribute_subtrees(self, tree):
        """
        Extract the attributes from the given tree.
        At this point, the function only extracts the attributes as defined by the grammar.

        :param tree: The parse tree of a sentence.
        :type tree: :class:`nltk.tree.Tree`

        :return: Subtrees from the tree that correspond to attributes (having the label ``ATTR``).
        :rtype: list of :class:`nltk.tree.Tree`
        """

        subtrees = [ node for node in tree if type(node) is nltk.tree.Tree ]
        ATTR = [ subtree for subtree in subtrees if subtree.label() == 'ATTR' ]
        return ATTR

    def _to_attributes(self, ATTR):
        """
        Convert the given ATTR subtree into a list of attributes.
        One subtree may return multiple ATTR subtrees when it has conjunctions.

        :param ATTR: The subtree which will be split into attributes.
        :type ATTR: :class:`nltk.tree.Tree`

        :return: The attribute as a tuple, with the first value being the name and the second being the value.
                 The attribute values are returned as lists of ``PPATR`` subtrees.
        :rtype: tuple of str and list :class:`nltk.tree.Tree`
        """

        name = [ component for component in ATTR.subtrees() if component.label() == 'NAME' ][0]
        name = [ text for text, pos in name.leaves() ]
        PPATR = [ component for component in ATTR.subtrees() if component.label() == 'PPATTR' ]
        return ('_'.join(name).lower(), PPATR)

    def _get_preposition(self, PPATR):
        """
        Extract the preposition from the given ATTR subtree, or ``None`` if the subtree doesn't have one.

        :param PPATR: The subtree from where to extract the preposition.
        :type PPATR: :class:`nltk.tree.Tree`

        :return: The first preposition (with label ``IN``) in the subtree or ``None`` if there is no preposition.
        :rtype: str or None
        """

        text, pos = PPATR.flatten()[0]
        return text if pos == 'IN' else None

    def _get_attribute(self, PPATR):
        """
        Extract the attribute subtree from the given subtree.

        :param PPATR: The subtree from where to extract the attribute value.
        :type PPATR: :class:`nltk.tree.Tree`

        :return: The attribute value in the subtree.
        :rtype: :class:`nltk.tree.Tree`
        """

        return [ _subtree for _subtree in PPATR.subtrees() if _subtree.label() == 'VALUE' ]

    def _attribute_value(self, VALUE):
        """
        Extract the attribute value from the given value subtree.
        The tree has several components, including adjectives; this function extracts only the value.

        :param VALUE: The subtree from where to extract the attribute value.
        :type VALUE: :class:`nltk.tree.Tree`

        :return: The actual textual value from the attribute value subtree.
        :rtype: str
        """

        value = [ ]
        head = VALUE[-1] if (type(VALUE[-1]) is nltk.tree.Tree and VALUE[-1].label() == 'ENT') else VALUE
        for text, pos in head.leaves():
            value.append(text)
        return (' '.join(value).lower())
