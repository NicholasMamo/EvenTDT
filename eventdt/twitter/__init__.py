"""
The Twitter package is used to facilitate collecting, reading and processing tweet corpora.
At the package-level there are functions to help with general processing tasks.
"""

from dateutil.parser import parse
import re

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

    if 'timestamp_ms' in tweet:
        timestamp_ms = int(tweet["timestamp_ms"])
        timestamp_ms = timestamp_ms - timestamp_ms % 1000
        return timestamp_ms / 1000.
    elif 'created_at' in tweet:
        return parse(tweet['created_at']).timestamp()

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

    while "retweeted_status" in tweet:
        tweet = tweet["retweeted_status"]

    if "extended_tweet" in tweet:
        text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
    else:
        text = tweet.get("text", "")

    return text

def is_retweet(tweet):
    """
    Check whether the given tweet is a retweet.
    A tweet is a retweet if it has a ``retweeted_status`` key.

    :param tweet: The tweet to check.
    :type tweet: dict

    :return: A boolean indicating whether the tweet is a retweet.
    :rtype: bool
    """

    return 'retweeted_status' in tweet

def is_reply(tweet):
    """
    Check whether the given tweet is a reply to another tweet.
    A tweet is a reply if it has a non-null ``in_reply_to_status_id_str`` (or any other attribute that starts with ``in_reply_to_``).

    :param tweet: The tweet to check.
    :type tweet: dict

    :return: A boolean indicating whether the tweet is a retweet.
    :rtype: bool
    """

    return tweet['in_reply_to_status_id_str'] is not None

def is_verified(tweet):
    """
    Check whether the given tweet's author is verified.
    Verified authors have a ``verified`` key set to ``true``.

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

    for handle, name in mentions.items():
        if '\\' in name:
            continue
        pattern = re.compile(f"{ re.escape(handle) }\\b", flags=re.I)
        text = re.sub(pattern, name, text)

    return text
