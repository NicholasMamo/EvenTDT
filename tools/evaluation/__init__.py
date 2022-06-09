"""
The evaluation package includes tools to evaluate different applications.
At the package-level are implementations of common metrics, with a focus on information retrieval.
"""

def unique(items):
    """
    Get a list of unique items in the given list.
    This function returns the items in the same order, but without duplicates.

    :param items: A list of items.
    :type items: list

    :return: A list of items in the same order, but without duplicates.
    :rtype: list
    """

    seen = set()
    return [ item for item in items if not (item in seen or seen.add(item)) ]

def is_precise(item, gold):
    """
    Check whether the given item is precise.
    The item is precise if it is in the gold set.

    :param item: The retrieved item.
    :type item: any
    :param gold: The gold standard items.
    :type gold: list or set

    :return: A boolean indicating whether the retrieved item is correct.
    :rtype: bool
    """

    return item in gold

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

    return { item for item in items if is_precise(item, gold) }

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

    items, gold = unique(items), unique(gold)
    return len(precise(items, gold)) / len(items)

def pk(items, gold, k=None):
    """
    Calculate the Precision at k (P@k) at the given value, calculated as:

    .. math::

        \\text{P@k} = \\frac{1}{k} \\sum_{i=1}^k{p_i}

    where :math:`k` is a parameter.
    :math:`p_i` is 1 if item :math:`i` is precise and 0 otherwise.

    This function assumes that the items are sorted in ascending order of rank.
    So, the first item should be the highest-scoring one.

    .. note::

        If you do not provide :math:`k`, the function calculates the precision at each :math:`k`.
        Use this if you need to calculate the precision at each item.
        This is much more efficient than calling the function for each item.

    :param items: A list of items to evaluate, which must be an ordered ranking.
    :type items: list
    :param gold: The gold standard items.
    :type gold: list or set
    :param k: The rank at which to calculate precision.
              If no rank is given, the function calculates the precision at each :math:`k`.
    :type k: int or None

    :return: The precision value of the top :math:`k` items.
             If no :math:`k` is given, the function returns a dictionary with :math:`k` as the key and the precision at that item as the value.
    :rtype: float or dict

    :raises ValueError: When k is below 1.
    """

    if k is not None and k < 1:
        raise ValueError(f"k must be at least 1; received { k }")

    if k is None:
        if not items:
            return { }

        items = unique(items)
        p = { 1: is_precise(items[0], gold) * 1 }
        for k, item in enumerate(items[1:]):
            p[k + 2] = (p[(k + 1)] * (k + 1) + is_precise(item, gold)) / (k + 2)

        return p
    else:
        return precision(items[:k], gold)

def average_precision(items, gold, ranked_only=True):
    """
    Calculate the average precision of the given items by evaluating the order.
    The higher the relevant items, the higher the average precision.
    The average precision is calculated as:

    .. math::

        \\text{AP} = \\frac{1}{| \\text{captured} |} \\sum_{k=1}^{n} \\text{P@k} \\cdot \\text{rel}_k

    where :math:`\\text{P@k}` is the :func:`Precision at k <tools.evaluation.pk>` and :math:`\\text{rel}_k` is a boolean indicating whether the item at rank :math:`k` is relevant or not.
    :math:`\\text{captured}` is the number of gold standard items that were actually captured in the ranking.

    :param items: A list of items to evaluate, which must be an ordered ranking.
    :type items: list
    :param gold: The gold standard items.
    :type gold: list or set
    :param ranked_only: A boolean indicating whether to take the average precision in the ranking, or whether to divide by the ground truth items.
    :type ranked_only: bool

    :return: The average precision value, bound between 0 and 1.
    :rtype: float
    """

    ap = 0
    items, gold = unique(items), unique(gold)
    if ranked_only:
        captured = set(items).intersection(set(gold)) # the number of gold items that were actually captured in the ranking
    else:
        captured = gold
    _pk = pk(items, gold)
    for k, item in enumerate(items):
        ap += _pk[k + 1] if is_precise(item, gold) else 0

    return ap / len(captured) if len(captured) else 0

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

    items, gold = unique(items), unique(gold)
    return len(recalled(items, gold)) / len(gold)

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
