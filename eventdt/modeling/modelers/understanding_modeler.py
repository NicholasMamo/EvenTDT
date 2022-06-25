"""
The :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` is a reversal of the traditional event modeling task.
Instead of understanding topics retrospectively to model them, the :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` depends on the provided understanding about the event.
The class applies that understanding to model events.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from modeling.modelers import EventModeler
import nlp

class UnderstandingModeler(EventModeler):
    """
    The :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` receives understanding and uses it to model events.

    .. note::

        The class uses NLTK's NLP module, which often confuses persons with organizations.
        In reality, the distinction does not matter much as the class accepts both as the Who.

    :ivar participants: The participants that are used to understand the Who and the Where.
                        The class expects participants to be :class:`~attributes.profile.Profile` instances.
                        Internally, participants are stored as a dictionary, with the name as the key and the profile as the value.
                        This allows the :func:`~modeling.modelers.understanding_modeler.UnderstandingModeler.who` and :func:`~modeling.modelers.understanding_modeler.UnderstandingModeler.where` functions to return full profiles, not just names.
    :vartype participants: dict
    """

    def __init__(self, participants=None):
        """
        Initialize the :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` with understanding.

        :param participants: The participants that are used to understand the Who and the Where.
                             The class expects participants to be :class:`~attributes.profile.Profile` instances.
        :type participants: list of :class:`attributes.profile.Profile`
        """

        self.participants = self._preprocess_participants(participants)

    def _preprocess_participants(self, participants):
        """
        Pre-process the participants, which includes removing parentheses from their names to facilitate matching later on.

        :param participants: The participants that are used to understand the Who and the Where.
        :type participants: list of :class:`attributes.profile.Profile`

        :return: A copy of the participants, with parentheses removed from their names.
                 The function stores the participants as a dictionary with the names as keys and the profiles as values.
        :rtype: dict
        """

        participants = participants or [ ]
        participants = [ participant.copy() for participant in participants ]
        for participant in participants:
            participant.name = nlp.remove_parentheses(participant.name).strip()
        return { participant.name: participant for participant in participants }

    def who(self, node):
        """
        Identify Who is participating in the given event.

        A participant is a person or an organization that appears in at least half of the documents in the node.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of participants, representing Who is participating in the event.
        :rtype: list
        """

        _who = { } # the document frequency of each participant

        for document in node.get_all_documents():
            found = [ ] # the list of participants found in this document's text
            entities = [ entity for entity, _ in nlp.entities(document.text, netype=[ "PERSON", "ORGANIZATION", "FACILITY" ]) ]
            for participant, profile in self.participants.items():
                if profile.is_location():
                    continue

                # check for the participant's name or aliases in the text
                if (profile.name.lower() in document.text.lower() or
                    any( reference.lower() in document.text.lower() for reference in profile.attributes.get('known_as', [ ]) )):
                    found.append(participant)

                # check for entities that are subsets of the entity or its aliases
                for entity in entities:
                    if (entity.lower() in profile.name.lower() or
                        any( entity.lower() in reference for reference in profile.attributes.get('known_as', [ ]) )):
                        found.append(participant)

                # TODO: handle other common named entities that match nothing else

            # increment each found participant's document frequency
            for participant in set(found):
                _who[participant] = _who.get(participant, 0) + 1

        _who = [ participant for participant, frequency in _who.items()
                             if frequency >= (len(node.get_all_documents()) / 2) ]
        return [ self.participants[participant] for participant in _who ]

    def what(self, node):
        """
        Identify What subject, action or change the given event represents.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of subjects, actions or changes that the given event represents.
        :rtype: list
        """

        return [ ]

    def where(self, node):
        """
        Identify Where the given event is taking place.

        A participant is a location that appears in at least half of the documents in the node.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of locations, representing Where the event is taking place.
        :rtype: list
        """

        _where = { } # the document frequency of each participant

        for document in node.get_all_documents():
            found = [ ] # the list of participants found in this document's text
            for participant, profile in self.participants.items():
                if not profile.is_location():
                    continue

                if profile.name.lower() in document.text.lower():
                    found.append(participant)

            # increment each found participant's document frequency
            for participant in set(found):
                _where[participant] = _where.get(participant, 0) + 1

            # TODO: check for entities that are subsets of the entity or its aliases
            # TODO: handle other common named entities that match nothing else

        _where = [ participant for participant, frequency in _where.items()
                             if frequency >= (len(node.get_all_documents()) / 2) ]
        return [ self.participants[participant] for participant in _where ]

    def when(self, node):
        """
        Identify When the given event is taking place.
        The function simply reuses the node's `created_at` attribute.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A time or a list of time periods When the event is taking place.
        :rtype: list
        """

        return [ node.created_at ]

    def why(self, node):
        """
        Identify the reason Why the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: The reasons Why the given event is taking place.
        :rtype: list
        """

        return [ ]

    def how(self, node):
        """
        Identify How the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: The ways How the event is taking place.
        :rtype: list
        """

        return [ ]
