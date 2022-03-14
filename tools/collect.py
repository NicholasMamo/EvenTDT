#!/usr/bin/env python3

"""
The collection tool is used to automatically-collect datasets from Twitter.
This tool supports two modes:

    - Sampling: collects a sample of all tweets being published.

    - Filtering: collects tweets that mention the given tracking keywords (capped at 50 tweets per second by Twitter).

The default mode collects a sample of all tweets, and can be used as follows:

.. code-block:: bash

    ./tools/collect.py \\
    --output data/sample \\
    --event 60

The ``--output`` parameter is  a directory where the tool saves the corpora.
The sampling corpus is saved to sample.json in this directory.
The ``--event`` parameter specifies how long, in minutes, the tool should spend collecting the corpus.

If you provide tracking keywords, the tool automatically uses the filtering mode.
You can provide multiple keywords using the ``--track`` parameter:

.. code-block:: bash

    ./tools/collect.py \\
    --output data/#ARSWAT \\
    --event 60 \\
    --track '#ARSWAT' 'Arsenal' 'Watford'

When collecting corpora using tracking keywords, the corpus is saved to event.json instead.
In addition to the event period, you can also collect an understanding corpus, used notably by the :class:`~queues.consumers.algorithms.eld_consumer.ELDConsumer`.
The understanding period always precedes the event period when given.
To do this, pass the ``--understanding`` parameter in the same way as the ``--event`` parameter:

.. code-block:: bash

    ./tools/collect.py \\
    --output data/#ARSWAT \\
    --understanding 60 \\
    --event 60 \\
    --track '#ARSWAT' 'Arsenal' 'Watford'

The corpora are JSON files, where each line contains a JSON-encoded `tweet object <https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/overview/tweet-object>`_, as returned by Twitter.
Since the corpora can only contain tweets, the metadata is saved instead to a meta.json file in the same directory.

.. note::

    The tool uses the credentials saved in the `config/conf.py` file.
    If you have multiple accounts, you can choose which one to use by providing the ``--account`` parameter.

.. note::

    The tool collects tweets in English only.

After collecting the datasets, the collection tool writes the details to a separate ``meta.json`` file in the same ``--output`` directory.
The output is a JSON file with the following structure:

.. code-block:: json

    {
        "understanding": {
            "cmd": {
                "output": "data",
                "track": [
                    "PSG"
                ],
                "understanding": null,
                "event": 1,
                "account": 0,
                "no_retweets": false,
                "_date": "2021-01-13T16:38:11.654496",
                "_timestamp": 1610552291.6545098,
                "_cmd": "./tools/collect.py --output data --event 1 --track PSG"
            },
            "pcmd": {
                "output": "data",
                "track": [
                    "PSG"
                ],
                "understanding": null,
                "event": 1,
                "account": 0,
                "no_retweets": false,
                "_date": "2021-01-13T16:38:11.654520",
                "_timestamp": 1610552291.6545227,
                "_cmd": "./tools/collect.py --output data --event 1 --track PSG"
            },
            "output": "/mnt/data/#BREWBA/understanding.json",
            "start": 1593192602.7365842,
            "end": 1593196204.672771,
            "collected": 120
        },
        "event": {
            "cmd": {
                "output": "data",
                "track": [
                    "PSG"
                ],
                "understanding": null,
                "event": 1,
                "account": 0,
                "no_retweets": false,
                "_date": "2021-01-13T16:38:11.654496",
                "_timestamp": 1610552291.6545098,
                "_cmd": "./tools/collect.py --output data --event 1 --track PSG"
            },
            "pcmd": {
                "output": "data",
                "track": [
                    "PSG"
                ],
                "understanding": null,
                "event": 1,
                "account": 0,
                "no_retweets": false,
                "_date": "2021-01-13T16:38:11.654520",
                "_timestamp": 1610552291.6545227,
                "_cmd": "./tools/collect.py --output data --event 1 --track PSG"
            },
            "output": "/mnt/data/#BREWBA/event.json",
            "start": 1593204301.1733663,
            "end": 1593204901.384444,
            "collected": 131
        }
    }

The top-level keys depend on whether the collected corpus was from a filtered stream, and whether it includes the understanding or event period.
If no filter keywords were provided, the file collects a sample, and the ``meta.json`` file has the following structure:

.. code-block:: json

    {
        "event": {
            "cmd": {
                "output": "data",
                "track": null,
                "understanding": null,
                "event": 60,
                "account": 0,
                "no_retweets": false,
                "_date": "2021-01-13T16:35:57.414309",
                "_timestamp": 1610552157.414321,
                "_cmd": "./tools/collect.py --output data --event 60"
            },
            "pcmd": {
                "output": "data",
                "track": null,
                "understanding": null,
                "event": 60,
                "account": 0,
                "no_retweets": false,
                "_date": "2021-01-13T16:35:57.414329",
                "_timestamp": 1610552157.4143317,
                "_cmd": "./tools/collect.py --output data --event 60"
            },
            "output": "data/sample.json",
            "start": 1610552157.4145017,
            "end": 1610552217.9032204,
            "collected": 1342
        }
    }

The full list of accepted arguments:

    - ``-o --output``            *<Required>* The data directory where the corpus should be written.
    - ``-t --track``             *<Optional>* A list of tracking keywords. If none are given, the sample stream is used.
    - ``-u --understanding``     *<Optional>* The length of the understanding period in minutes. If it is not given, the understanding period is skipped.
    - ``-e --event``             *<Optional>* The length of the event period in minutes. If it is not given, the event period is skipped.
    - ``-a --account``           *<Optional>* The account to use to collect the corpus with, as an index of the configuration's accounts. Defaults to the first account.
    - ``--lang``                 *<Optional>* If given, only collect tweets in the given language.
    - ``--no-retweets``          *<Optional>* If given, the tweet listener will exclude all retweets.
    - ``--v2``                   *<Optional>* Use the Twitter APIv2 (not implemented to use tweepy).
"""

import argparse
import json
import os
import sys
import time

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from tweepy import OAuthHandler
from tweepy import Stream

from config import conf
from logger import logger
import tools
from twitter import BearerTokenAuth, Streamv2
from twitter.listeners import TweetListener

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-o --output``            *<Required>* The data directory where the corpus should be written.
        - ``-t --track``             *<Optional>* A list of tracking keywords. If none are given, the sample stream is used.
        - ``-u --understanding``     *<Optional>* The length of the understanding period in minutes. If it is not given, the understanding period is skipped.
        - ``-e --event``             *<Optional>* The length of the event period in minutes. If it is not given, the event period is skipped.
        - ``-a --account``           *<Optional>* The account to use to collect the corpus with, as an index of the configuration's accounts. Defaults to the first account.
        - ``--lang``                 *<Optional>* If given, only collect tweets in the given language.
        - ``--no-retweets``          *<Optional>* If given, the tweet listener will exclude all retweets.
        - ``--v2``                   *<Optional>* Use the Twitter APIv2 (not implemented to use tweepy).

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Collect a corpus of tweets.")

    """
    Parameters that define how the corpus should be collected.
    """

    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The data directory where the corpus should be written.')
    parser.add_argument('-t', '--track', nargs='+', required=False, help='<Optional> The initial tracking keywords. If none are given, the sample stream is used.')
    parser.add_argument('-u', '--understanding', nargs='?', type=int,
                        default=None, required=False,
                        help='<Optional> The length of the understanding period in minutes. If it is not given, the understanding period is skipped.')
    parser.add_argument('-e', '--event', nargs='?', type=int,
                        default=None, required=False,
                        help='<Optional> The length of the event period in minutes. If it is not given, the event period is skipped.')
    parser.add_argument('-a', '--account', nargs='?', type=int,
                        default=0, required=False,
                        help='<Optional> The account to use to collect the corpus with, as an index of the configuration\'s accounts. Defaults to the first account.')
    parser.add_argument('--lang', nargs='?', type=str, default='en', required=False,
                        help='<Optional> If given, only collect tweets in the given language. Defaults to English.')
    parser.add_argument('--no-retweets', required=False, action='store_true',
                        help='<Optional> If given, the tweet listener will exclude all retweets.')
    parser.add_argument('--v2', required=False, action='store_true',
                        help='<Optional> Use the Twitter APIv2 (not implemented to use tweepy).')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()
    cmd = tools.meta(args)
    pcmd = tools.meta(args)
    meta = { }

    """
    Create the data directory if it does not exist.
    """
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    auth = authenticate(args.account, args.v2)

    """
    Collect the tweets for the understanding period.
    """
    if args.understanding is not None:
        if args.understanding <= 0:
            raise ValueError("The understanding period must be longer than 0 minutes")

        filename = os.path.join(args.output, 'understanding.json')

        start = time.time()
        logger.info('Starting to collect understanding corpus')
        collected = collect(auth, args.track, filename, args.understanding * 60, lang=args.lang, no_retweets=args.no_retweets, v2=args.v2)
        logger.info('Understanding corpus collected')
        end = time.time()
        meta['understanding'] = {
            'cmd': cmd,
            'pcmd': pcmd,
            'output': filename,
            'start': start,
            'end': end,
            'collected': collected
        }

    """
    Collect the tweets for the event period.
    """
    if args.event is not None:
        if args.event <= 0:
            raise ValueError("The event period must be longer than 0 minutes")

        filename = os.path.join(args.output, ('event.json' if args.track else 'sample.json'))

        start = time.time()
        logger.info('Starting to collect event corpus')
        collected = collect(auth, args.track, filename, args.event * 60, lang=args.lang, no_retweets=args.no_retweets, v2=args.v2)
        logger.info('Event corpus collected')
        end = time.time()
        meta['event'] = {
            'cmd': cmd,
            'pcmd': pcmd,
            'output': filename,
            'start': start,
            'end': end,
            'collected': collected
        }

    if meta:
        save_meta(os.path.join(args.output, 'meta.json'), meta)

def authenticate(account, v2=False):
    """
    Set up the authentication with the Twitter Stream API.

    :param account: The account number to use to authenticate.
                    The account number refers to the :mod:`configured accounts <~config.conf>`
    :type account: int
    :param v2: A boolean indicating whether to use the Twitter APIv2.
    :type v2: bool

    :return: The authentication.
    :rtype: :class:`tweepy.auth.OAuthHandler` or :class:`~twitter.listeners.bearer_token_auth.BearerTokenAuth`
    """

    account = conf.ACCOUNTS[account]

    if v2:
        return BearerTokenAuth(account['CONSUMER_KEY'], account['CONSUMER_SECRET'])
    else:
        auth = OAuthHandler(account['CONSUMER_KEY'], account['CONSUMER_SECRET'])
        auth.set_access_token(account['ACCESS_TOKEN'], account['ACCESS_TOKEN_SECRET'])
        return auth

def setup_rules(track, lang=None, no_retweets=False):
    """
    Setup the rules used to collect tweets from the Twitter APIv2.

    Note that this function is most appropriate for `Elevated and Academic Research tracks <https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction>`_.
    Since this function creates one rule for each tracking keyword, the rule limits can be reached very quickly.

    :param track: The list of tracking keywords.
    :type track: list of str
    :param lang: The tweet collection language, defaults to English.
    :type lang: str or None
    :param no_retweets: A boolean indicating whether to skip retweets.
    :type no_retweets: bool

    :return: A list of rules as expected by the :fun:`~twitter.listeners.stream_v2.Streamv2.set_rules` function.
    :rtype: list of dict
    """

    if lang is None:
        logger.warning("No language set")

    rules = [ { 'value': f"{ _track } { 'lang:' + str(lang) if lang else '' } { '-is:retweet' if no_retweets else '' }".strip(),
                'tag': _track }
              for _track in track ]
    return rules

def collect(auth, track, filename, max_time, lang=None, no_retweets=False, v2=False, *args, **kwargs):
    """
    Collect tweets and save them to the given file.
    The tweets are collected synchronously.
    Any additional arguments or keyword arguments are passed on to the :class:`twitter.twevent.listener.TweetListener` constructor.

    :param auth: The OAuth handler to connect with Twitter's API.
    :type auth: :class:`tweepy.OAuthHandler`
    :param track: The list of tracking keywords.
    :type track: list of str
    :param filename: The filename where to save the collected tweets.
    :type filename: str
    :param max_time: The number of seconds to spend collecting tweets.
    :type max_time: int
    :param lang: The tweet collection language, defaults to English.
    :type lang: list of str or None
    :param no_retweets: A boolean indicating whether to skip retweets.
    :type no_retweets: bool
    :param v2: A boolean indicating whether to collect tweets using the Twitter APIv2 or not.
    :type v2: bool

    :return: The number of collected tweets.
    :rtype: int
    """

    collected = 0
    listener = None

    try:
        with open(filename, 'a') as file:
            if v2:
                listener = TweetListener(file, max_time=max_time, retweets=(not no_retweets), *args, **kwargs)
                stream = Streamv2(auth)
                rules = setup_rules(track, lang=lang, no_retweets=no_retweets)
                logger.info(rules)
                stream.set_rules(rules)
                start = time.time()
                stream.connect(listener)
            else:
                start = time.time()
                lang = [ 'en' ] if lang is None else [ lang ]
                listener = TweetListener(file, auth=auth, max_time=max_time, retweets=(not no_retweets))
                if track:
                    listener.filter(track=track, languages=lang)
                else:
                    listener.sample(languages=lang)

            collected += listener.collected # add the number of collected tweets when the listener stops collecting tweets
    except (Exception) as e:
        collected += listener.collected if listener else 0 # if the listener could be initialized, add the number of collected tweets
        elapsed = time.time() - start
        logger.warning(f"{e.__class__.__name__} after {elapsed} seconds, restarting for {max_time - elapsed} seconds")
        collected += collect(auth, track, filename, max_time - elapsed, lang, no_retweets=no_retweets, v2=v2, *args, **kwargs) # add the number of collected tweets from the new process

    return collected

def save_meta(filename, meta):
    """
    Save the metadata of the collected datasets.

    :param filename: The filename where to write the metadata.
    :type filename: str
    :param meta: The metadata to save.
    :type meta: list of dict
    """

    """
    Load the existing metadata if it exists.
    """
    if os.path.exists(filename):
        with open(filename, 'r') as meta_file:
            existing = json.loads(meta_file.readline())
            existing.update(meta)
            meta = existing

    """
    Save the metadata to the file.
    """
    with open(filename, 'w') as meta_file:
        meta_file.write(json.dumps(meta) + "\n")

if __name__ == "__main__":
    main()
