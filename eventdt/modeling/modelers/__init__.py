"""
The modelers package contains algorithms that are capable of creating :class:`~modeling.EventModel`.
All modelers must derive from and implement the functions of the :class:`~modeling.modelers.EventModeler`.
"""

from abc import ABC, abstractmethod

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from modeling import EventModel

class EventModeler(ABC):
    """
    The :class:`~modeling.modelers.EventModeler` receives :class:`~summarization.timeline.Timeline <timelines>` and builds one :class:`~modeling.EventModel` for each node in it.
    The class expects nodes because normally, the When is extracted from their creation time.
    If only nodes are available, and not a timeline, the :func:`~modeling.modelers.EventModeler.model` function can be byassed and the other functions, such as :func:`~modeling.modelers.EventModeler.who`, called directly with the node.
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
            model = EventModel(who=who, what=what, where=where, when=when, why=why, how=how)
            model.attributes['node_id'] = node.attributes['id']
            models.append(model)
            print('.', end='', flush=True)

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
    A trivial implementation of the :class:`~modeling.modelers.EventModeler` for testing purposes.
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

from .understanding_modeler import UnderstandingModeler
