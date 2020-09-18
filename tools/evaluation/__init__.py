"""
The evaluation package includes tools to evaluate different applications.
At the package-level are implementations of common metrics, with a focus on information retrieval.
"""

def precise(items, gold):
    """
    Get a set of items that are in the gold set.
    This function automatically removes duplicates.

    :param items: A list of retrieved items.
    :type items: list or set
    :param gold: The gold standard items.
    :type gold: list or set

    :return: A set of items that are in the gold standard.
    :rtype: set
    """

    return { item for item in items if item in gold }

def recalled(items, gold):
    """
    Get a set of items that were recalled from the gold set.
    This function automatically removes duplicates.

    :param items: A list of retrieved items.
    :type items: list or set
    :param gold: The gold standard items.
    :type gold: list or set

    :return: A set of items recalled from the gold standard.
    :rtype: set
    """

    return { item for item in gold if item in items }

def precision(items, gold):
    """
    Calculate the precision of the given items by evaluating how many of them are in the gold standard.
    Precision is calculated as:

    .. math::

        \\text{precision} = \\frac{|{ \\text{{gold}} } \\cap \\text{{items}}|}{|{ \\text{{items}} }|}

    This function automatically removes duplicates.

    :param items: A list of items to evaluate.
    :type items: list or set
    :param gold: The gold standard items.
    :type gold: list or set

    :return: The precision value, bound between 0 and 1.
    :rtype: float
    """

    if not items:
        return 0

    items, gold = set(items), set(gold)
    correct = { item for item in items if item in gold }
    return len(precise(items, gold)) / len(items)

def recall(items, gold):
    """
    Calculate the recall of the given items by evaluating how many of the items in the gold standard they contain.
    Recall is calculated as:

    .. math::

        \\text{recall} = \\frac{|{ \\text{{gold}} } \\cap \\text{{items}}|}{|{ \\text{{gold}} }|}

    This function automatically removes duplicates.

    :param items: A list of items to evaluate.
    :type items: list or set
    :param gold: The gold standard items.
    :type gold: list or set

    :return: The recall value, bound between 0 and 1.
    :rtype: float
    """

    if not gold:
        return 0

    items, gold = set(items), set(gold)
    correct = { item for item in gold if item in items }
    return len(correct) / len(gold)

def f1(precision, recall):
    """
    Calculate the harmonic mean of the precision and recall, bounded between 0 and 1:

    .. math::

        \\text{F1} = 2 \\cdot \\frac{\\text{precision} \\cdot \\text{recall}}{\\text{precision} + \\text{recall}}

    :param precision: The precision of the item set, see :func:`~tools.evaluation.precision`.
    :type precision: float
    :param recall: The recall of the item set, see :func:`~tools.evaluation.recall`.
    :type recall: float

    :return: The harmonic mean of the precision and recall, bounded between 0 and 1.
    :rtype: float

    :raises ValueError: When the precision is not between 0 and 1.
    :raises ValueError: When the recall is not between 0 and 1.
    """

    if not 0 <= precision <= 1:
        raise ValueError(f"Precision should be between 0 and 1; received { precision }")

    if not 0 <= recall <= 1:
        raise ValueError(f"Recall should be between 0 and 1; received { recall }")

    if precision == recall == 0:
        return 0

    return 2 * (precision * recall) / (precision + recall)
