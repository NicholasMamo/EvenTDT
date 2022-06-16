"""
The event modeling package contains classes and functions that make it easier to formally represent events.
"""

import os
import sys

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from objects import Attributable

class EventModel(Attributable):
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
