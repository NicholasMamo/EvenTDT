"""
In addition to the base and simple consumers, EvenTDT includes consumers that replicate methods proposed in literature.
These approaches are as faithful to the original techniques as possible, although they depend a lot on the details available in the respective papers.

You can use these consumers as baselines or to have a working base from where to start implementing your own consumers.
To run these consumers, check out the :mod:`~tools.consume` tool.

.. warning::

    In many cases, these consumers replicate most faithfully the TDT approach, not the summarization approach.
"""

from enum import Enum

class DynamicThreshold(Enum):
    """
    The type of dynamic threshold to use.
    Options:

        - MEAN:        The mean volume observed so far
        - MOVING_MEAN: The mean volume from the previous $n$ windows
        - MEAN_STDEV:  One standard deviation above the mean volume observed so far
    """

    MEAN = 1
    MOVING_MEAN = 2
    MEAN_STDEV = 3

class FilterLevel(Enum):
    """
    The amount of filtering to apply on tweets.
    The actual interpretations, except for `NONE`, depends on the algorithms.
    The `LENIENT` option can be used when it is acceptable for tweets to have URLs; for example, when detecting breaking news in unspecified domains, newsrooms often break the news themselves.
    Options:

        - NONE:     Do not filter any tweets.
        - LENIENT:  Filter tweets leniently.
        - STRICT:   Filter tweets strictly.
    """

    NONE = 1
    LENIENT = 2
    STRICT = 3

from .eld_consumer import ELDConsumer
from .fire_consumer import FIREConsumer
from .fuego_consumer import SEERConsumer, FUEGOConsumer
from .zhao_consumer import ZhaoConsumer
