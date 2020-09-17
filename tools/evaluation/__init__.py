"""
The evaluation package includes tools to evaluate different applications.
At the package-level are implementations of common metrics, with a focus on information retrieval.
"""

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
    return len(correct) / len(items)
