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
    :ivar lemmatizer: The lemmatizer with which to lemmatize attribute names.
                      If lemmatization is disabled, the variable is ``None``.
    :vartype: :class:`nltk.WordNetLemmatizer` or ``None``.
    """

    def __init__(self, grammar=None, lemmatize=False):
        """
        Create the linguistic extractor with an optional grammar.
        If a grammar is not given, a default grammar is used instead:

        **DATE**
        (``DATE: (<CD> <NNP> <CD>|<NNP> <CD> <,> <CD>); <NNP> <,> <DATE>``)

        The grammar assumes that a pattern involving two numbers and a proper noun in various formats represents a date (*14/CD May/NNP 2017/CD*).

        **Modifier** (``MOD: <CD>?<JJ.*|RB.*>+ (<CC|,><CD>?<JJ.*|RB.*>+)*``)

        A modifier is a list of adjectives (*Brazilian/JJ professional/JJ*) or adverbs (*[known] simply/RB [as]*) that modify something else.
        There may be more than one such modifier, all separated by coordinating conjunctions or commas.

        Each modifier may start with a number (*19/CD member/NN states/NNS*), but it may not appear among adjectives or adverbs.
        A modifier may also be a single number.

        **Entity**
        (``ENT: <CD>? <NNP.*> (<IN><NNP.*>|<CD|NNP.*>)*; <MOD>+ <ENT>`` }

        An entity can start with (*1860/CD Munich/NNP*) or end with a number (*Schalke/NNP 04/CD*), but it must always include at least one proper noun.
        Entities may have a preposition (*United/NNP States/NP of/IN America/NP*) but never at the start or at the end.
        Moreover, a preposition can only be followed by a proper noun, not a number, avoiding phrases like *[served as president of] France/NNP from/IN 2012/CD to/TO 2017/CD* being misconstrued as an entity.

        An entity may also have its own modifiers, as in the name *Indian/JJ Oceans/NNP*.

        **Noun phrase**
        (``NP: { <MOD|VBG>* <NN.*>+ }``)

        A noun phrase is a sequence of nouns (*football/NN team/NN*) possibly preceded by modifiers.

        **Attribute name** (``NAME: <VB.*>``)

        An attribute name is formed by any verb (*plays/VBZ*), including past participles (*driven/VBN*).

        **Attribute value** (``VALUE: <NP|ENT|CD|DATE>+; <VALUE> (<POS> <VALUE>)``)

        The attribute value can be either a noun phrase (*Brazilian/JJ professional/JJ footballer/NN*), an entity (*Lyon/ENT*), a number (*since/IN 2012/CD*), or a date (*[born on] October/NNP 28/CD ,/, 1955/CD*).
        It may also be several at once (*(Ligue 1)/ENT (club/NN)/NP Lyon/ENT*).

        A value may also have a possessive, in which case the subject and object are returned together and separately.

        **Value list** (``VALUES: <IN|TO>? (<DT|PRP$>?<VALUE><CC|,>*)+``)

        Each attribute can have several values (*[is an] (VALUE American/JJ business/NN magnate/NN),/, (VALUE software/NN developer/NN) and/CC (VALUE investor/NN)*)
        The attribute value may take a determiner (*is/VBZ a/DT footballer/NN*) or possessive pronoun (*[adopted the euro as] their/PRP$ primary/JJ currency/NN*) just before the value.
        The prepositional attribute accepts several such values as long as they are separated by coordinating conjunctions (*and*, *or*) or commas.

        Before the list of values, there may be a preposition, which modifies the relationship between the attribute and its values; a footballer does not simply play but *plays/VBZ for/IN*.

        **Attribute** (``ATTR: <NAME> (<MOD>? <VALUES>)+``)

        The complete attribute therefore has a name and a list of values, each of which may have modifiers.

        .. warn:

            **Known issues**

            - In order to handle entities with prepositions, such as *United/NNP States/NNPS of/IN America/NNP*, the grammar misses prepositional attributes.
              For example, in the phrase *competing in Formula One with McLaren*, the entity is taken to be Formula One with McLaren.
              The correct parse should be two attributes: the driver competes in Formula 1 and competes with McLaren.
              TODO: Add parse

            - The grammar struggles with sub-clauses because it assumes that verb gerunds are modifiers.
              This means that the grammar correctly extracts the relation ``'plays_as': 'attacking midfielder'`` from phrases such as *plays/VBZ as/IN an/DT attacking/VBG midfielder/NN*.
              However, the grammar does not extract a relation from the phrase *painting/VBG landscapes/NNS or/CC vedute/NN*.

        :param grammar: The grammar with which to extract attributes.
                        The grammar must have a way to extract entities (``ENT``), attributes (``ATTR``) and prepositional attributes (``PPATR``), and attribute names (``NAME``) and values (``VALUE``).
        :type grammar: str
        :param lemmatize: A boolean indicating whether to lemmatize a verb or not.
                          Lemmatization helps reduce the impact of conjugation and sentence structure on the attributes, such as whether the sentence uses the passive or active voice.
                          However, it also eliminates the tense, which means that past attributes have the same name as present or future attributes.
        :type lemmatize: bool
        """

        grammar = grammar or """
                  DATE: { (<CD> <NNP> <CD>|<NNP> <CD> <,> <CD>) }
                  DATE: { <NNP> <,> <DATE> }
                  MOD: { <CD>?<JJ.*|RB.*>+ (<CC|,><CD>?<JJ.*|RB.*>+)* }
                  ENT: { <CD>? <NNP.*> (<IN><NNP.*>|<CD|NNP.*>)* }
                  ENT: { <MOD>+ <ENT> }
                  NP: { <MOD|VBG>* <NN.*>+ }
                  NAME: { <VB.*> }
                  VALUE: { <NP|ENT|CD|DATE>+ }
                  VALUE: { <VALUE> (<POS> <VALUE>) }
                  VALUES: { <IN|TO>? (<DT|PRP$>?<VALUE><CC|,>*)+ }
                  ATTR: { <NAME> (<MOD>? <VALUES>)+ }
        """
        self.parser = nltk.RegexpParser(grammar)
        self.lemmatizer = nltk.WordNetLemmatizer() if lemmatize else None

    def extract(self, text, verbose=False, *args, **kwargs):
        """
        Extract attributes from the given text.
        This function assumes that the text is about a single entity and therefore does not seek to confirm who the attributes are discussing.

        Any additional arguments and keyword arguments are passed on to the :class:`~attributes.profile.Profile` :func:`constructor <~attributes.profile.Profile.__init__>`.

        :param text: The text from where to extract attributes.
        :type text: str
        :param verbose: A boolean indicating whether to print the tree as a way of debugging.
        :type verbose: bool

        :return: A profile of attributes.
                 Each attribute may have a list of values.
        :rtype: :class:`~attributes.profile.Profile`
        """

        profile = Profile(*args, **kwargs)

        sentences = nltk.sent_tokenize(text)
        for sentence in sentences:
            tree = self._parse(sentence)
            if verbose:
                print(tree)
            ATTR = self._attribute_subtrees(tree)
            for _ATTR in ATTR:
                NAME, VALUES = self._to_attributes(_ATTR)
                for _VALUES in VALUES:
                    PP = self._get_preposition(_VALUES)
                    name = f"{NAME}_{ PP }" if PP else NAME
                    profile.attributes[name] = profile.attributes.get(name) or set()
                    attributes = self._get_attribute(_VALUES)
                    for attribute in attributes:
                        # TODO: Extract and split adjectives (first extract the head noun or the head entity).
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
        name = [ self.lemmatizer.lemmatize(text, pos='v') if self.lemmatizer else text
                 for text, pos in name.leaves() ]
        PPATR = [ component for component in ATTR.subtrees() if component.label() == 'VALUES' ]
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
        return text if pos in ('IN', 'TO') else None

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
