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

class UnderstandingModeler(EventModeler):
    """
    The :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` receives understanding and uses it to model events.
    """

    def who(self, node):
        """
        Identify Who is participating in the given event.

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of participants, representing Who is participating in the event.
        :rtype: list
        """

        return [ ]

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

        :param node: A node on the timeline.
        :type node: :class:`~summarization.timeline.nodes.Node`

        :return: A list of locations, representing Where the event is taking place.
        :rtype: list
        """

        return [ ]

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
