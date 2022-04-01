"""
The Twitter package is used to facilitate collecting, reading and processing tweet corpora.
At the package-level there are functions to help with general processing tasks.
"""

from dateutil.parser import parse
import re

def version(tweet):
    """
    Get the version with which the tweet was collected.

    :param tweet: The tweet from which to extract the API version.
    :type tweet: dict

    :return: The version of the API with which the tweet was collected.
    :rtype: int
    """

    if 'data' in tweet:
        return 2

    return 1

def timestamp(tweet):
    """
    An alias to the :func:`~twitter.extract_timestamp` function.

    :param tweet: The tweet from which to extract the timestamp.
    :type tweet: dict
    """

    return extract_timestamp(tweet)

def extract_timestamp(tweet):
    """
    Get the timestamp from the given tweet.
    This function looks for the timestamp in one of two fields:

    1. ``timestamp_ms``: always present in the top-level tweets, and
    2. ``created_at``: present in ``retweeted_status``, for example.

    :param tweet: The tweet from which to extract the timestamp.
    :type tweet: dict

    :return: The timestamp of the tweet.
    :rtype: int

    :raises KeyError: When no timestamp field can be found.
    """

    if version(tweet) == 1:
        if 'timestamp_ms' in tweet:
            timestamp_ms = int(tweet["timestamp_ms"])
            timestamp_ms = timestamp_ms - timestamp_ms % 1000
            return timestamp_ms / 1000.
        elif 'created_at' in tweet:
            return parse(tweet['created_at']).timestamp()
    else:
        return parse(tweet['data']['created_at']).timestamp()

    raise KeyError("Neither the 'timestamp_ms' attribute, nor the 'created_at' attribute could be found in the tweet.")

def full_text(tweet):
    """
    Extract the full text from the tweet.

    Normally, long tweets are truncated (they end with a `…`).
    This function looks for the original full text.
    If it's a retweet, the text is somewhere in the ``retweeted_status``.
    If the tweet has an ``extended_tweet`` attribute, then the ``full_text`` may be set there.
    Otherwise, the function defaults to using the ``text``.

    :param tweet: The tweet from which to extract the timestamp.
    :type tweet: dict

    :return: The full text of the tweet.
    :rtype: str
    """

    while is_retweet(tweet):
        tweet = tweet["retweeted_status"]

    if "extended_tweet" in tweet:
        text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
    else:
        text = tweet.get("text", "")

    return text

def is_retweet(tweet):
    """
    Check whether the given tweet is a retweet.

    :param tweet: The tweet to check.
    :type tweet: dict

    :return: A boolean indicating whether the tweet is a retweet.
    :rtype: bool
    """

    if version(tweet) == 1:
        return 'retweeted_status' in tweet
    else:
        return any( referenced['type'] == 'retweeted' for referenced in tweet['data'].get('referenced_tweets', [ ]) )

def original(tweet):
    """
    Get the original tweet (the one that was retweeted).

    :param tweet: The tweet to check.
    :type tweet: dict

    :return: The original tweet.
    :rtype: dict
    """

    if version(tweet) == 1:
        while is_retweet(tweet):
            tweet = tweet["retweeted_status"]
        return tweet
    else:
        if is_retweet(tweet):
            referenced = [ referenced for referenced in tweet['data']['referenced_tweets']
                                      if referenced['type'] == 'retweeted' ][0]
            return [ _tweet for _tweet in tweet['includes']['tweets']
                            if _tweet['id'] == referenced['id'] ][0]
        else:
            return tweet['data']

def is_quote(tweet):
    """
    Check whether the given tweet is a quoted status.

    :param tweet: The tweet to check.
    :type tweet: dict

    :return: A boolean indicating whether the tweet is a quote.
    :rtype: bool
    """

    if version(tweet) == 1:
        return 'quoted_status' in tweet
    else:
        tweet = original(tweet) if is_retweet(tweet) else tweet
        return any( referenced['type'] == 'quoted' for referenced in tweet.get('data', tweet)
                   .get('referenced_tweets', [ ]) )

def quoted(tweet):
    """
    Get the original, quoted status.

    :param tweet: The tweet to check.
    :type tweet: dict

    :return: The quoted status.
    :rtype: dict

    :raises KeyError: If the tweet contains no quoted status.
    :raises KeyError: If the quoted tweet is retweeted, and thus only a reference to it exists.
    """

    if version(tweet) == 1:
        return tweet['quoted_status']
    else:
        if is_retweet(tweet):
            raise KeyError("The quoted tweet is retweeted and thus only a reference to it exists.")

        references = [ referenced['id'] for referenced in tweet.get('data', tweet).get('referenced_tweets')
                                        if referenced['type'] == 'quoted' ][0]
        referenced = [ included for included in tweet['includes']['tweets']
                                if included['id'] == references ][0]
        return referenced

def is_reply(tweet):
    """
    Check whether the given tweet is a reply to another tweet.
    A tweet is a reply if it has a non-null ``in_reply_to_status_id_str`` (or any other attribute that starts with ``in_reply_to_``).

    :param tweet: The tweet to check.
    :type tweet: dict

    :return: A boolean indicating whether the tweet is a retweet.
    :rtype: bool
    """

    if version(tweet) == 1:
        return tweet['in_reply_to_status_id_str'] is not None
    else:
        tweet = original(tweet) if is_retweet(tweet) else tweet
        return any( referenced['type'] == 'replied_to' for referenced in tweet.get('data', tweet)
                   .get('referenced_tweets', [ ]) )

def author(tweet, user_id=None):
    """
    Get the author object of the given tweet.
    If a user ID is given, the function returns the corresponding author; otherwise, it returns the author of the top-level tweet.

    :raises KeyError: If there is no user with the given ID.
    """

    if version(tweet) == 1:
        if not user_id:
            return tweet['user']
        else:
            authors = { tweet['user']['id_str']: tweet['user'] }
            if is_retweet(tweet):
                authors.update({ original(tweet)['user']['id_str']: original(tweet)['user'] })
            if is_quote(tweet):
                authors.update({ quoted(tweet)['user']['id_str']: quoted(tweet)['user'] })
            return authors[user_id]
    elif version(tweet) == 2:
        authors = { user['id']: user for user in tweet['includes']['users'] }
        return authors[user_id] if user_id else authors[tweet['data']['author_id']]

def is_verified(tweet):
    """
    Check whether the given tweet's author is verified.
    Verified authors have a ``verified`` key set to ``true``.

    .. note::

        If the tweet is a retweet, the function checks whether the retweeting author is verified, not the author of the original tweet.

    :param tweet: The tweet to check.
    :type tweet: dict

    :return: A boolean indicating whether the tweet is from a verified author.
    :rtype: bool
    """

    return tweet['user']['verified']

def expand_mentions(text, tweet):
    """
    Replace all mentions in the text with the user's display name.

    :param text: The text to clean.
    :type text: str
    :param tweet: The tweet dictionary.
    :type tweet: dict

    :return: The cleaned text.
    :rtype: str

    :raises ValueError: When the tweet is not given and the mentions should be replaced.
    """

    """
    Create a mapping between user mentions and their display names.
    User mentions can appear in:

        #. The base tweet,
        #. The retweeted tweet, and
        #. The quoted status.
    """
    mentions = { }
    mentions.update({ f"@{ mention['screen_name'] }": mention['name']
                      for mention in tweet['entities']['user_mentions'] })
    mentions.update({ f"@{ mention['screen_name'] }": mention['name']
                      for mention in tweet.get('extended_tweet', { }).get('entities', { }).get('user_mentions', { }) })
    mentions.update({ f"@{ mention['screen_name'] }": mention['name']
                      for mention in tweet.get('retweeted_status', { }).get('entities', { }).get('user_mentions', { }) })
    mentions.update({ f"@{ mention['screen_name'] }": mention['name']
                      for mention in tweet.get('retweeted_status', { }).get('extended_tweet', { }).get('entities', { }).get('user_mentions', { }) })
    mentions.update({ f"@{ mention['screen_name'] }": mention['name']
                      for mention in tweet.get('quoted_status', { }).get('entities', { }).get('user_mentions', { }) })
    mentions.update({ f"@{ mention['screen_name'] }": mention['name']
                      for mention in tweet.get('quoted_status', { }).get('extended_tweet', { }).get('entities', { }).get('user_mentions', { }) })

    # fix a pesky bug where some people have an empty name
    mentions = { handle: name for handle, name in mentions.items() if name }

    for handle, name in mentions.items():
        if '\\' in name:
            continue
        pattern = re.compile(f"{ re.escape(handle) }\\b", flags=re.I)
        text = re.sub(pattern, name, text)

    return text

from .listeners.bearer_token_auth import BearerTokenAuth
from .listeners.stream_v2 import Streamv2
