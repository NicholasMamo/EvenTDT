#!/usr/bin/env python3

"""
The download tool is used to download tweets from shareable datasets, which are made up of tweet IDs.
The tool expects as input a file with one tweet ID on each line, produced by the :mod:`~tools.shareable` tool.

To run this tool, use the following:

.. code-block:: bash

    ./tools/download.py \\
    --file data/shareable.txt \\
    --output data/output.json \\
    --meta meta/output.json

.. note::

    The downloaded datasets have some missing fields: {'quote_count', 'reply_count', 'filter_level', 'timestamp_ms'}.
    This is a restriction in the Twitter API.

The full list of accepted arguments:

    - ``-f --file``                          *<Required>* The shareable corpus created by the :mod:`~tools.collect` tool.
    - ``-o --output``                        *<Required>* The file where to save the downloaded corpus.
    - ``--meta``                             *<Optional>* The file where to save the meta data, defaults to [--file].meta.
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
        - ``--meta``                             *<Optional>* The file where to save the meta data, defaults to [--file].meta.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Download a shareable dataset.")

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The shareable corpus created by the `shareable` tool.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the downloaded corpus.')
    parser.add_argument('--meta', type=str, required=False,
                        help='<Optional> The file where to save the meta data, defaults to [--file].meta.')

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
    auth = authenticate()
    download(args.file, args.output, auth)

    meta = args.meta or f"{ args.output }.meta"
    pcmd['meta'] = meta
    tools.save(meta, { 'cmd': cmd, 'pcmd': pcmd })

def authenticate():
    """
    Authenticate with the Twitter API.

    :return: The authentication object.
    :rtype: :class:`tweepy.auth.OAuthHandler`
    """

    account = conf.ACCOUNTS[0]
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

    downloaded, deleted = [ ], [ ]

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
                    downloaded.extend([ status['id_str'] for status in statuses ])
                    deleted.extend([ id for id in _ids if id not in downloaded ])

                    for status in statuses:
                        outfile.write(f"{ json.dumps(status)}\n")
                    read = True
                except tweepy.error.RateLimitError:
                    logger.warning("Rate limit reached")
                    time.sleep(60)

    return (downloaded, deleted)

if __name__ == "__main__":
    main()
