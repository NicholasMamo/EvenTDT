#!/usr/bin/env python3

"""
The download tool is used to download tweets from shareable datasets, which are made up of tweet IDs.
The tool expects as input a file with one tweet ID on each line, produced by the :mod:`~tools.shareable` tool.

To run this tool, use the following:

.. code-block:: bash

    ./tools/download.py \\
    --file data/shareable.txt \\
    --output data/output.json \\
    --meta meta/output.meta.json

.. note::

    The downloaded datasets have some missing fields: {'quote_count', 'reply_count', 'filter_level', 'timestamp_ms'}.
    This is a restriction in the Twitter API.

The full list of accepted arguments:

    - ``-f --file``                          *<Required>* The shareable corpus created by the :mod:`~tools.collect` tool.
    - ``-o --output``                        *<Required>* The file where to save the downloaded corpus.
    - ``-a --account``                       *<Optional>* The account to use to collect the corpus with, as an index of the configuration's accounts. Defaults to the first account.
    - ``--meta``                             *<Optional>* The file where to save the meta data, defaults to [--file].meta.json.
"""

import argparse
import json
import math
import os
import sys
import time

import tweepy
from tweepy import API, OAuthHandler

file_path = os.path.dirname(os.path.abspath(__file__))
lib = os.path.join(file_path, '../eventdt')
root = os.path.join(file_path, '..')
sys.path.insert(-1, lib)
sys.path.insert(-1, root)

from config import conf
from logger import logger
import tools

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``                          *<Required>* The shareable corpus created by the :mod:`~tools.collect` tool.
        - ``-o --output``                        *<Required>* The file where to save the downloaded corpus.
        - ``-a --account``                       *<Optional>* The account to use to collect the corpus with, as an index of the configuration's accounts. Defaults to the first account.
        - ``--meta``                             *<Optional>* The file where to save the meta data, defaults to [--file].meta.json.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Download a shareable dataset.")

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The shareable corpus created by the `shareable` tool.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the downloaded corpus.')
    parser.add_argument('-a', '--account', nargs='?', type=int,
                        default=0, required=False,
                        help='<Optional> The account to use to collect the corpus with, as an index of the configuration\'s accounts. Defaults to the first account.')
    parser.add_argument('--meta', type=str, required=False,
                        help='<Optional> The file where to save the meta data, defaults to [--file].meta.json.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    # set up the arguments and prepare the data directory
    args = setup_args()
    cmd = tools.meta(args)
    pcmd = tools.meta(args)
    tools.save(args.output, { }) # to create the directory if it doesn't exist
    start = time.time()
    auth = authenticate(args.account)
    retrieved, irretrievable = download(args.file, args.output, auth)
    end = time.time()

    meta = args.meta or f"{ os.path.splitext(os.path.basename(args.output))[0] }.meta.json"
    pcmd['meta'] = meta
    pcmd['retrieved'], pcmd['irretrievable'] = retrieved, irretrievable
    pcmd['start'] = start
    pcmd['elapsed'] = time.time() - start
    pcmd['end'] = end
    tools.save(meta, { 'cmd': cmd, 'pcmd': pcmd })

def authenticate(account):
    """
    Authenticate with the Twitter API.

    :param account: The account to use to collect the corpus with, as an index of the configuration's accounts.
    :type account: int

    :return: The authentication object.
    :rtype: :class:`tweepy.auth.OAuthHandler`
    """

    account = conf.ACCOUNTS[account]
    auth = OAuthHandler(account['CONSUMER_KEY'], account['CONSUMER_SECRET'])
    auth.set_access_token(account['ACCESS_TOKEN'], account['ACCESS_TOKEN_SECRET'])
    return auth

def download(file, output, auth):
    """
    Download the tweets identified by the IDs in the given file and save them to a file.

    .. note::

        The downloaded datasets have some missing fields: {'quote_count', 'reply_count', 'filter_level', 'timestamp_ms'}.
        This is a restriction in the Twitter API.

    :param file: The path to the file containing IDs.
                 The function expects the file to contain one ID in plain text on each line, as outputted by the :mod:`~tools.shareable` file.
    :type file: str
    :param output: The path to the file where the tool will save downloaded tweets.
    :type output: str
    :param auth: The authentication object for the Twitter API.
    :type auth: :class:`tweepy.auth.OAuthHandler`

    :return: A tuple containing a list of downloaded IDs and a list of irretrievable IDs.
    :rtype: tuple of list
    """

    start, last_output = time.time(), 0

    retrieved, irretrievable = [ ], [ ]

    # create the API object
    api = API(auth)

    # open the input and output files and download the tweets
    with open(file, 'r') as infile, \
         open(output, 'w') as outfile:
        ids = [ id.strip() for id in infile.readlines() ]

        # read the tweets in batches: the maximum batch size is 100
        batch = 100
        for i in range(math.floor(len(ids)/batch) + 1):
            _ids = ids[i * batch:(i + 1) * batch]
            if not _ids:
                break

            # try to download the next batch of tweets, but if the rate limit is reached, sleep for a while
            read = False
            while not read:
                try:
                    statuses = api.statuses_lookup(_ids)
                    statuses = [ status._json for status in statuses ]

                    # sort the statuses in the same order as in the original list
                    statuses = sorted(statuses, key=lambda status: _ids.index(status['id_str']))

                    # find which statuses could be retrieved
                    retrieved.extend([ status['id_str'] for status in statuses ])
                    irretrievable.extend([ id for id in _ids if id not in retrieved ])

                    for status in statuses:
                        outfile.write(f"{ json.dumps(status)}\n")
                    read = True
                except tweepy.error.RateLimitError:
                    logger.warning("Rate limit reached")
                    time.sleep(60)

            # print progress updates regularly
            progress = (len(retrieved) + len(irretrievable)) / len(ids)
            if progress - last_output > 0.1: # every 10%
                last_output = progress
                elapsed = time.time() - start
                eta =  elapsed * (1 - progress) / progress
                logger.info(f"Downloaded { round(progress * 100) }% ({ len(retrieved) }/{ len(retrieved) + len(irretrievable) }) - ETA { math.floor(eta / 60) }m { round(eta % 60) }s")

    return (retrieved, irretrievable)

if __name__ == "__main__":
    main()
