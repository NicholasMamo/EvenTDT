"""
The Twitter package is used to facilitate collecting, reading and processing tweet corpora.
At the package-level there are functions to help with general processing tasks.

.. note::

    The user-level functions always return the user who tweeted, quoted or retweeted a tweet—not the original author of those tweets.
    Conversely, tweet-level functions return content from a mix of the original and modified tweets.
"""

from dateutil.parser import parse
import re

MEDIA_URL = re.compile("\/(photo|video)\/\\d$")
"""
The pattern used to search for media URLs in APIv2 tweets.
"""

def version(tweet):
    """
    Get the Twitter API version with which the tweet was collected.

    :param tweet: The tweet from which to extract the API version.
    :type tweet: dict

    :return: The version of the API with which the tweet was collected.
    :rtype: int
    """

    if 'id_str' in tweet:
        return 1

    return 2

def id(tweet):
    """
    Get the tweet's ID.

    :param tweet: The tweet from which to extract the ID.
    :type tweet: dict

    :return: The tweet's ID as a string.
    :rtype: str
    """

    if version(tweet) == 1:
        return tweet['id_str']
    else:
        return str(tweet.get('data', tweet)['id'])

def lang(tweet):
    """
    Extract the language from the given tweet.

    :param tweet: The tweet from which to extract the language.
    :type tweet: dict

    :return: The tweet's language.
    :rtype: str
    """

    return tweet.get('data', tweet)['lang']

def timestamp(tweet):
    """
    An alias to the :func:`~twitter.extract_timestamp` function.

    :param tweet: The tweet from which to extract the timestamp.
    :type tweet: dict

    :return: The timestamp of the tweet.
    :rtype: int
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
        return parse(tweet.get('data', tweet)['created_at']).timestamp()

    raise KeyError("Neither the 'timestamp_ms' attribute, nor the 'created_at' attribute could be found in the tweet.")

def text(tweet):
    """
    An alias to the :func:`~twitter.full_text` function.

    :param tweet: The tweet from which to extract the text.
    :type tweet: dict

    :return: The full text of the tweet.
    :rtype: str
    """

    return full_text(tweet)

def full_text(tweet):
    """
    Extract the full text from the tweet.

    Normally, long tweets are truncated (they end with a `…`).
    This function looks for the original full text.
    If it's a retweet, the text is somewhere in the ``retweeted_status``.
    If the tweet has an ``extended_tweet`` attribute, then the ``full_text`` may be set there.
    Otherwise, the function defaults to using the ``text``.

    :param tweet: The tweet from which to extract the text.
    :type tweet: dict

    :return: The full text of the tweet.
    :rtype: str
    """

    if version(tweet) == 1:
        while is_retweet(tweet):
            tweet = original(tweet)
    else:
        # this function assumes there can only be one referenced tweet that is a retweet (tested in `test_package`)
        tweet = original(tweet) if is_retweet(tweet) else tweet

    if version(tweet) == 1:
        if "extended_tweet" in tweet:
            text = tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
        else:
            text = tweet.get("text", "")
    else:
        text = tweet.get('data', tweet)['text']

    return text

def urls(tweet):
    """
    Extract the URLs from the given tweet.
    The function does not return media URLs.

    For APIv1.1 tweets, the function looks for URLs in the extended tweet and in the original tweet.

    :param tweet: The tweet from which to extract URLs.
    :type tweet: dict

    :return: A list of expanded URLs.
    :rtype: list of str
    """

    if version(tweet) == 1:
        tweet = original(tweet) if is_retweet(tweet) else tweet
        urls = tweet.get('extended_tweet', tweet).get('entities', { }).get('urls', [ ]) + tweet.get('entities', { }).get('urls', [ ])
    else:
        tweet = original(tweet) if is_retweet(tweet) else tweet
        urls = tweet.get('data', tweet).get('entities', { }).get('urls', [ ])
    urls = [ url['expanded_url'] for url in urls ]
    urls = [ url for url in urls if not MEDIA_URL.search(url) ]
    return list(set(urls))

def hashtags(tweet):
    """
    Extract the hashtags from the given tweet.

    :param tweet: The tweet from which to extract hashtags.
    :type tweet: dict

    :return: A list of hashtags.
    :rtype: list of str
    """

    if version(tweet) == 1:
        tweet = original(tweet) if is_retweet(tweet) else tweet
        hashtags = tweet.get('extended_tweet', tweet).get('entities', { }).get('hashtags', [ ])
        return [ hashtag['text'] for hashtag in hashtags ]
    else:
        tweet = original(tweet) if is_retweet(tweet) else tweet
        hashtags = tweet.get('data', tweet).get('entities', { }).get('hashtags', [ ])
        return [ hashtag['tag'] for hashtag in hashtags ]

def annotations(tweet):
    """
    Extract the annotations from the given tweet.

    .. warning::

        Only APIv2 tweets include annotations.

    :param tweet: The tweet from which to extract hashtags.
    :type tweet: dict

    :return: A list of entities.
    :rtype: list of str

    :raises NotImplementedError: When trying to retrieve the annotation from an APIv1.1 tweet.
    """

    if version(tweet) == 1:
        raise NotImplementedError("Annotations are only provided in APIv2 tweets.")
    else:
        tweet = original(tweet) if is_retweet(tweet) else tweet
        annotations = tweet.get('data', tweet).get('entities', { }).get('annotations', [ ])
        return [ annotation['normalized_text'] for annotation in annotations ]

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
        return any( referenced['type'] == 'retweeted' for referenced in tweet.get('data', tweet).get('referenced_tweets', [ ]) )

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
        if is_retweet(tweet) and not 'errors' in tweet:
            referenced = [ referenced for referenced in tweet.get('data', tweet).get('referenced_tweets', [ ])
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

    :param tweet: The tweet whose author to extract.
    :type tweet: dict
    :param user_id: The ID of the user to extract.
    :type user_id: str

    :raises KeyError: If there is no user with the given ID.
    :raises KeyError: If the tweet object does not include users.
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
            return authors[str(user_id)]
    elif version(tweet) == 2:
        if 'includes' not in tweet:
            raise KeyError("The included users are not available. Make sure to provide the original tweet as the first parameter.")

        authors = { user['id']: user for user in tweet['includes']['users'] }
        return authors[user_id] if user_id else authors[tweet['data']['author_id']]

def user_id(tweet):
    """
    Extract the user ID who published the given tweet.
    The function accepts not only original tweet objects but also quoted and original tweets.

    :param tweet: The tweet whose author to extract.
    :type tweet: dict

    :return: The ID of the user who published the tweet.
    :rtype: str
    """

    if version(tweet) == 1:
        return tweet['user']['id_str']
    else:
        return tweet.get('data', tweet)['author_id']

def user_handle(tweet, user_id=None):
    """
    Extract the handle of the user who published the given tweet.
    The function accepts not only original tweet objects but also quoted and original tweets.

    .. note::

        By default, if the tweet is a retweet, the function retrieves the number of tweets favorited by the retweeting author, not by the author of the original tweet.

    :param tweet: The tweet whose user handle to extract.
    :type tweet: dict

    :return: The ID of the user who published the tweet.
    :rtype: str
    """

    if version(tweet) == 1:
        return author(tweet, user_id)['screen_name']
    else:
        return author(tweet, user_id)['username']

def user_favorites(tweet, user_id=None):
    """
    Get the number of tweets favorited by the author of the tweet.

    .. note::

        By default, if the tweet is a retweet, the function retrieves the number of tweets favorited by the retweeting author, not by the author of the original tweet.

    .. warning::

        APIv2 tweets currently do not include the number of tweets liked by the author.

    :param tweet: The tweet to check.
    :type tweet: dict
    :param user_id: The ID of the user whose favorites to extract.
                    Use this parameter to extract information about retweet or quote tweet authors from APIv2 tweets.
    :type user_id: str

    :return: The number of tweets favorited by the author of the tweet.
    :rtype: int

    :raises NotImplementedError: When trying to retrieve the number of tweets favorited by the author from an APIv2 tweet.
    """

    if version(tweet) == 1:
        return author(tweet, user_id)['favourites_count']
    else:
        raise NotImplementedError("Favorites counts are not provided in APIv2 tweets.")

def user_statuses(tweet, user_id=None):
    """
    Get the number of tweets published by the author of the tweet.

    .. note::

        By default, if the tweet is a retweet, the function retrieves the number of tweets published by the retweeting author, not by the author of the original tweet.

    :param tweet: The tweet to check.
    :type tweet: dict
    :param user_id: The ID of the user whose statuses to extract.
                    Use this parameter to extract information about retweet or quote tweet authors from APIv2 tweets.
    :type user_id: str

    :return: The number of tweets published by the author of the tweet.
    :rtype: int
    """

    if version(tweet) == 1:
        return author(tweet, user_id)['statuses_count']
    else:
        return author(tweet, user_id)['public_metrics']['tweet_count']

def user_followers(tweet, user_id=None):
    """
    Get the number of followers of the author of the tweet.

    .. note::

        By default, if the tweet is a retweet, the function retrieves the number of followers of the retweeting author, not of the author of the original tweet.

    :param tweet: The tweet to check.
    :type tweet: dict
    :param user_id: The ID of the user whose followers to extract.
                    Use this parameter to extract information about retweet or quote tweet authors from APIv2 tweets.
    :type user_id: str

    :return: The number of followers of the author of the tweet.
    :rtype: int
    """

    if version(tweet) == 1:
        return author(tweet, user_id)['followers_count']
    else:
        return author(tweet, user_id)['public_metrics']['followers_count']

def user_description(tweet, user_id=None):
    """
    Get the profile description of the tweet's author.

    .. note::

        By default, if the tweet is a retweet, the function retrieves retweeting author's description, not the description of the original tweet's author.

    :param tweet: The tweet to check.
    :type tweet: dict
    :param user_id: The ID of the user whose description to extract.
                    Use this parameter to extract information about retweet or quote tweet authors from APIv2 tweets.
    :type user_id: str

    :return: The number of followers of the author of the tweet.
    :rtype: str or None
    """

    return author(tweet, user_id)['description']

def is_verified(tweet, user_id=None):
    """
    Check whether the given tweet's author is verified.
    Verified authors have a ``verified`` key set to ``true``.

    .. note::

        By default, if the tweet is a retweet, the function checks whether the retweeting author is verified, not whether the author of the original tweet is verified.

    :param tweet: The tweet to check.
    :type tweet: dict
    :param user_id: The ID of the user to check whether is verified.
                    Use this parameter to extract information about retweet or quote tweet authors from APIv2 tweets.
    :type user_id: str

    :return: A boolean indicating whether the tweet is from a verified author.
    :rtype: bool
    """

    return author(tweet, user_id)['verified']

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

    if version(tweet) == 1:
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
    else:
        mentions = { }
        mentions.update({ f"@{ mention['username'] }": [ user['name'] for user in tweet['includes']['users']
                                                                      if user['username'] == mention['username'] ]
                          for mention in tweet['data'].get('entities', { }).get('mentions', [ ]) })

        # Fixes an error about the user being unavailable because Twitter has suspended them by the time the tweet is collected
        mentions = { username: names[0] for username, names in mentions.items() if len(names) }

        # Mentions in referenced tweets are not expanded because information about them is unavailable
        # mentions.update({ f"@{ mention['username'] }": [ user['name'] for user in tweet['includes']['users']
        #                                                               if user['username'] == mention['username'] ][0]
        #                   for included in tweet['includes'].get('tweets', [ ])
        #                   for mention in included.get('entities', { }).get('mentions', [ ]) })

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
