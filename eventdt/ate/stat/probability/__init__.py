"""
The probability package includes probability-based ATE approaches.
In addition, the package comes with functions that are likely to be useful to probability-based algorithms.
This includes caching functionality, which collects all documents across all corpora that mention a particular token.
"""

import json

def p(corpora, focus=None, cache=None):
    """
    Calculate the probability of tokens appearing in the corpus.
    The probability is computed in terms of all tokens.

    Apart from calculating the probability of single tokens, the joint probability can be calculated by providing tuples.

    .. note::

        The joint probability is the minimum count of any token in the joint set in each document.

    :param corpora: A corpus, or corpora, of documents.
                    If a string is given, it is assumed to be one corpus.
                    If a list is given, it is assumed to be a list of corpora.

                    .. note::

                        It is assumed that the corpora were extracted using the tokenizer tool.
                        Therefore each line should be a JSON string representing a document.
                        Each document should have a `tokens` attribute.
    :type corpora: str or list of str
    :param focus: The tokens for which to compute the probability.
                 If nothing is given, the probability is calculated for all tokens.
                 The tokens can be provided as:

                 - A single word,
                 - A list of tokens,
                 - A tuple, or
                 - A list of tuples.

                 A tuple can be used to compute joint probabilities.
    :type focus: None or str or list of str or tuple or list of tuple
    :param cache: A list of terms that are re-used often and which should be cached.
                  If an empty list is given, no cache is used.

                  .. note::

                      Cache should be used when there is a lot of repetition.
                      For example, `x` can be used as cache when `x` is small and `y` is large.
                      If the data is small, using cache can be detrimental.
    :type cache: list of str

    :return: A dictionary with tokens as keys and probabilities as values.
    :rtype: dict
    """

    """
    Convert the corpora and tokens into a list if they aren't already.
    The list of tokens is always made into a list, even if it's a list of one string or tuple.
    """
    corpora = [ corpora ] if type(corpora) is str else corpora
    focus = focus or [ ]
    focus = [ focus ] if type(focus) is tuple or type(focus) is str else focus
    focus = [ (itemset, ) if type(itemset) is str else itemset for itemset in focus ]
    cache = cache or [ ]
    cache = [ cache ] if type(cache) is str else cache

    """
    Create the initial counts for all tokens and joint probabilities.
    This avoids returning missing probabilities for tokens or joint tokens that never appear.
    """
    counts = { }
    for itemset in focus:
        counts[itemset if len(itemset) > 1 else itemset[0]] = 0

    """
    If cache is defined, generate a list of documents for each cached token.
    This reduces the number of documents to go over.
    """
    if cache:
        for token in cache:
            """
            If no itemset contains the token, skip the cache.
            """
            if not any( token in itemset for itemset in focus ):
                continue

            """
            Create the cache.
            """
            documents = cached(corpora, token)

            """
            Look for item sets that mention the cached token.
            """
            itemsets = [ tuple for tuple in focus if token in tuple ]
            for document in documents:
                for itemset in itemsets:
                    if not all( item in document['tokens'] for item in itemset ):
                        continue

                    min_count = min( document['tokens'].count(item) for item in itemset )
                    counts[itemset if len(itemset) > 1 else itemset[0]] += min_count

            focus = [ tuple for tuple in focus if token not in tuple ]

    """
    Count the total number of tokens encountered and a separate count for each token.
    """
    tokens = 0
    for corpus in corpora:
        with open(corpus, 'r') as f:
            for line in f:
                document = json.loads(line)

                """
                The number of tokens is always incremented by all the tokens.
                """
                tokens += len(document['tokens'])

                """
                If there is no specification for which tokens to compute probability, compute the prior probability for all tokens.
                """
                if not focus:
                    for token in document['tokens']:
                        counts[token] = counts.get(token, 0) + 1
                else:
                    """
                    Convert each item in the list of tokens for which to compute the probability into a tuple.
                    """
                    for itemset in focus:
                        if not all( item in document['tokens'] for item in itemset ):
                            continue

                        min_count = min( document['tokens'].count(item) for item in itemset )
                        counts[itemset if len(itemset) > 1 else itemset[0]] += min_count

    """
    Compute the probability by dividing the count by the number of tokens.
    """
    if tokens:
        return { token: count / tokens for token, count in counts.items() }

    return { }

def joint_vocabulary(x, y):
    """
    Get the joint vocabulary by creating the cross-product from `x` and `y`.

    :param x: The tokens for which to compute the probability.
              These tokens are combined as a cross-product with all tokens in `y`.
              The tokens can be provided as:

              - A single word,
              - A list of tokens,
              - A tuple, or
              - A list of tuples.

              A tuple translates to joint probabilities.
    :type x: str or list of str or tuple or list of tuple
    :param y: The tokens for which to compute the probability.
              These tokens are combined as a cross-product with all tokens in `x`.
              The tokens can be provided as:

              - A single word,
              - A list of tokens,
              - A tuple, or
              - A list of tuples.

              A tuple translates to joint probabilities.
    :type y: str or list of str or tuple or list of tuple

    :return: The joint vocabulary, which is the cross-product of each item in `x` with each item in `y`.
    :rtype: list of tuple
    """

    vocabulary = [ ]

    """
    The list of tokens in `x` and `y` is always made into a list, even if it's a list of one string or tuple.
    """
    x, y = x or [ ], y or [ ]
    x = [ x ] if type(x) is tuple or type(x) is str else x
    y = [ y ] if type(y) is tuple or type(y) is str else y

    """
    Immediately return if either `x` or `y` are empty.
    """
    if not x:
        return [ tuple(item) if type(item) is not str else (item, ) for item in y ]

    if not y:
        return [ tuple(item) if type(item) is not str else (item, ) for item in x ]

    """
    Create the vocabulary.
    """
    for i in x:
        """
        Always convert the elements into a list, whether they are a string or a tuple.
        """
        i = list([ i ] if type(i) is str else i)
        for j in y:
            j = list([ j ] if type(j) is str else j)
            vocabulary.append(tuple(i + j))

    return vocabulary

def cached(corpora, token):
    """
    Compile all the documents in the given corpora that mention the token.
    These documents can be used as cache.
    In this way, the files do not have to be re-opened and documents without the token do not have to be iterated over.

    :param corpora: A corpus, or corpora, of documents.
                    If a string is given, it is assumed to be one corpus.
                    If a list is given, it is assumed to be a list of corpora.

                    .. note::

                        It is assumed that the corpora were extracted using the tokenizer tool.
                        Therefore each line should be a JSON string representing a document.
                        Each document should have a `tokens` attribute.
    :type corpora: str or list of str
    :param token: The token to look for in the documents.
    :type token: str

    :return: A list of documents, each represented as a dictionary, that contain the given token.
    :rtype: list of dict
    """

    """
    Convert the corpora into a list if they aren't already.
    """
    corpora = [ corpora ] if type(corpora) is str else corpora

    documents = [ ]
    for corpus in corpora:
        with open(corpus, 'r') as f:
            for line in f:
                """
                The check is in two steps:

                    1. Check whether the token appears in the line string; and
                    2. If it appears in the line string, decode the line and double-check that the token is in the document tokens.

                This saves a lot of time from needlessly decoding lines, most of which do not contain the token.
                """
                if token in line:
                    document = json.loads(line)
                    if token in document['tokens']:
                        documents.append(document)

    return documents
