"""
The event modeling package contains classes and functions that make it easier to formally represent events.
"""

from abc import ABC, abstractmethod
import copy
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from objects import Attributable, Exportable

class EventModel(Attributable, Exportable):
    """
    The :class:`~modeling.EventModel` represents events using the `five Ws and one H` as attributes.
    The class always initializes the six attributes and does not impose any restrictions on the class.
    Nevertheless, event modelers might impose their own restrictions, such as using :class:`datetime.datetime` instances for the When.
    """

    def __init__(self, who=None, what=None, where=None, when=None, why=None, how=None, *args, **kwargs):
        """
        Create the event model from the `five Ws and one H`.
        The constructor stores the six aspects as attributes.

        :param who: The person or persons involved in the event.
        :type who: Any
        :param what: The subject, action or changes of an event.
        :type what: Any
        :param where: The location where the event is taking place.
        :type where: Any
        :param when: The time or time periods when the event takes place.
        :type when: Any
        :param why: The reasons why an event occurred, which could be another :class:`~modeling.EventModel`.
        :type why: Any
        :param how: The reasons how an event occurred, which could be another :class:`~modeling.EventModel`.
        :type how: Any
        """

        super(EventModel, self).__init__(*args, **kwargs)
        self.attributes.update({ 'who': who, 'what': what, 'where': where,
                                 'when': when, 'why': why, 'how': how })

    def to_array(self):
        """
        Export the :class:`~modeling.EventModel` as ``dict``.
        This ``dict`` has two keys:

            1. The class name, used when re-creating the :class:`~modeling.EventModel`; and
            2. The :class:`~modeling.EventModel`'s attributes as a ``dict``

        :return: The :class:`~modeling.EventModel` as ``dict``.
        :rtype: dict
        """

        return {
            'class': str(EventModel),
            'attributes': copy.deepcopy(self.attributes)
        }

    @staticmethod
    def from_array(array):
        """
        Create an instance of the :class:`~modeling.EventModel` from the given ``dict``.
        This function expects the array to have been generated by the :func:`~Vector.to_array`, and must have two keys:

            1. The class name; and
            2. The :class:`~modeling.EventModel`'s attributes as a ``dict``.

        :param array: The ``dict`` with the attributes to create the :class:`~modeling.EventModel`.
        :type array: dict

        :return: A new instance of the :class:`~modeling.EventModel` with the same attributes stored in the object.
        :rtype: :class:`~modeling.EventModel`
        """

        attributes = array.get('attributes')
        return EventModel(who=attributes.get('who'), what=attributes.get('what'), where=attributes.get('where'),
                          when=attributes.get('when'), why=attributes.get('why'), how=attributes.get('how'),
                          attributes=copy.deepcopy(attributes))

class EventModeler(ABC):
    """
    The :class:`~modeling.EventModeler` receives :class:`~summarization.timeline.Timeline <timelines>` and builds one :class:`~modeling.EventModel` for each node in it.
    """

    def model(self, timeline):
        """
        Convert the given timeline into a list of event models.

        :param timeline: The timeline to convert into event models.
        :type timeline: :class:`~summarization.timeline.Timeline`

        :return: A list of event models, one for each node in the timeline.
        :rtype: List of :class:`~modeling.EventModel`
        """

        models = [ ]

        for node in timeline.nodes:
            who = self.who(node)
            what = self.what(node)
            where = self.where(node)
            when = self.when(node)
            why = self.why(node)
            how = self.how(node)
            models.append(EventModel(who=who, what=what, where=where,
                                     when=when, why=why, how=how))

        return models

    @abstractmethod
    def who(self, node):
        """
        Identify Who is participating in the given event.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of participants, representing Who is participating in the event.
        :rtype: list
        """

        pass

    @abstractmethod
    def what(self, node):
        """
        Identify What subject, action or change the given event represents.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of subjects, actions or changes that the given event represents.
        :rtype: list
        """

        pass

    @abstractmethod
    def where(self, node):
        """
        Identify Where the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of locations, representing Where the event is taking place.
        :rtype: list
        """

        pass

    @abstractmethod
    def when(self, node):
        """
        Identify When the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A time or a list of time periods When the event is taking place.
        :rtype: list
        """

        pass

    @abstractmethod
    def why(self, node):
        """
        Identify the reason Why the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: The reasons Why the given event is taking place.
        :rtype: list
        """

        pass

    @abstractmethod
    def how(self, node):
        """
        Identify How the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: The ways How the event is taking place.
        :rtype: list
        """

        pass

class DummyEventModeler(EventModeler):
    """
    A trivial implementation of the :class:`~modeling.EventModeler` for testing purposes.
    """

    def who(self, node):
        """
        Identify Who is participating in the given event.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of participants, representing Who is participating in the event.
        :rtype: list
        """

        return None

    def what(self, node):
        """
        Identify What subject, action or change the given event represents.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of subjects, actions or changes that the given event represents.
        :rtype: list
        """

        return None

    def where(self, node):
        """
        Identify Where the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of locations, representing Where the event is taking place.
        :rtype: list
        """

        return None

    def when(self, node):
        """
        Identify When the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A time or a list of time periods When the event is taking place.
        :rtype: list
        """

        return None

    def why(self, node):
        """
        Identify the reason Why the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: The reasons Why the given event is taking place.
        :rtype: list
        """

        return None

    def how(self, node):
        """
        Identify How the given event is taking place.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: The ways How the event is taking place.
        :rtype: list
        """

        return None
