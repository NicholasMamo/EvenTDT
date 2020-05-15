#!/usr/bin/env python3

"""
A tool to collect tweets.

The tool collects a corpus of tweets.
A corpus can be split into an understanding and an event corpus.
Both can be collected by specifying tracking keywords.
All related corpora are stored together in the same directory.
Each corpus is a JSON file, where each line is one tweet.

To run the script, use:

.. code-block:: bash

    ./tools/collect.py \\
	-o data/#ARSWAT \\
	-t '#ARSWAT' Arsenal Watford \\
	-U -u 60 \\
	-E -e 60

If no tracking keywords are specified, a sample of all tweets is collected.

.. code-block:: bash

    ./tools/collect.py \\
	-o data/sample \\
	-U -u 60 \\
	-E -e 60

Accepted arguments:

	- ``-o --output``			*<Required>* The data directory where the corpus should be written.
	- ``-t --track``			*<Optional>* A list of tracking keywords. If none are given, the sample stream is used.
	- ``-u --understanding``	*<Optional>* The length of the understanding period in minutes. Defaults to an hour and must be a natural number.
	- ``-e --event``			*<Optional>* The length of the event period in minutes. Defaults to an hour and must be a natural number.
	- ``-a --account``			*<Optional>* The account to use to collect the corpus with, as an index of the configuration's accounts. Defaults to the first account.

The implemented modes of operation are:

	- ``-U``					*<Optional>* Collect the understanding corpus.
	- ``-E``					*<Optional>* Collect the event corpus.
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

from logger import logger
from twitter.listener import TweetListener

from tweepy import OAuthHandler
from tweepy import Stream

from config import conf

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-o --output``			*<Required>* The data directory where the corpus should be written.
		- ``-t --track``			*<Optional>* A list of tracking keywords. If none are given, the sample stream is used.
		- ``-U``					*<Optional>* Collect the understanding corpus.
		- ``-u --understanding``	*<Optional>* The length of the understanding period in minutes. Defaults to an hour and must be a natural number.
		- ``-E``					*<Optional>* Collect the event corpus.
		- ``-e --event``			*<Optional>* The length of the event period in minutes. Defaults to an hour and must be a natural number.
		- ``-a --account``			*<Optional>* The account to use to collect the corpus with, as an index of the configuration's accounts. Defaults to the first account.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Collect a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The data directory where the corpus should be written.')
	parser.add_argument('-t', '--track', nargs='+', type=str, required=False,
						action='append', help='<Optional> The initial tracking keywords. If none are given, the sample stream is used.')
	parser.add_argument('-u', '--understanding', nargs='?', type=int,
						default=60, required=False,
						help='<Optional> The length of the understanding period in minutes. Defaults to an hour.')
	parser.add_argument('-e', '--event', nargs='?', type=int,
						default=60, required=False,
						help='<Optional> The length of the event period in minutes. Defaults to an hour.')
	parser.add_argument('-a', '--account', nargs='?', type=int,
						default=0, required=False,
						help='<Optional> The account to use to collect the corpus with, as an index of the configuration\'s accounts. Defaults to the first account.')

	"""
	The modes of operation.
	"""

	parser.add_argument('-U', action='store_true',
						help='<Optional> Collect the understanding corpus.')
	parser.add_argument('-E', action='store_true',
						help='<Optional> Collect the event corpus.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()

	"""
	Create the data directory if it does not exist.
	"""
	if not os.path.exists(args.output):
		os.makedirs(args.output)

	"""
	Set up the authentication with the Twitter Stream API.
	"""
	account = conf.ACCOUNTS[args.account]
	auth = OAuthHandler(account['CONSUMER_KEY'], account['CONSUMER_SECRET'])
	auth.set_access_token(account['ACCESS_TOKEN'], account['ACCESS_TOKEN_SECRET'])

	"""
	Start collecting tweets.
	"""
	meta = { }
	if args.U:
		if args.understanding <= 0:
			raise ValueError("The understanding period must be longer than 0 minutes")

		filename = os.path.join(args.output, 'understanding.json')

		start = time.time()
		logger.info('Starting to collect understanding corpus')
		collect(auth, args.track, filename, args.understanding * 60)
		logger.info('Understanding corpus collected')
		end = time.time()
		meta['understanding'] = {
			'keywords': args.track,
			'output': filename,
			'start': start,
			'end': end
		}

	if args.E:
		if args.event <= 0:
			raise ValueError("The event period must be longer than 0 minutes")

		filename = os.path.join(args.output, ('event.json' if args.track else 'sample.json'))

		start = time.time()
		logger.info('Starting to collect event corpus')
		collect(auth, args.track, filename, args.event * 60)
		logger.info('Event corpus collected')
		end = time.time()
		meta['event'] = {
			'keywords': args.track,
			'output': filename,
			'start': start,
			'end': end
		}

	if meta:
		save_meta(os.path.join(args.output, 'meta.json'), meta)

def collect(auth, track, filename, max_time, lang=None, *args, **kwargs):
	"""
	Collect tweets and save them to the given file.
	The tweets are collected synchronously.
	Any additional arguments or keyword arguments are passed on to the :class:`twitter.twevent.listener.TweetListener` constructor.

	:param auth: The OAuth handler to connect with Twitter's API.
	:type auth: :class:`tweepy.OAuthHandler`
	:param track: The tracking keywords:
	:type track: list of str
	:param filename: The filename where to save the collected tweets.
	:type filename: str
	:param max_time: The number of seconds to spend collecting tweets.
	:type max_time: int
	:param lang: The tweet collection language, defaults to English.
	:type lang: list of str
	"""

	lang = [ 'en' ] if lang is None else lang

	start = time.time()
	try:
		with open(filename, 'w') as file:
			listener = TweetListener(file, max_time=max_time, *args, **kwargs)
			stream = Stream(auth, listener)
			if track:
				stream.filter(track=track, languages=lang)
			else:
				stream.sample(languages=lang)
	except (Exception) as e:
		elapsed = time.time() - start
		logger.warning(f"{e.__class__.__name__} after {elapsed} seconds, restarting for {max_time - elapsed} seconds")
		collect(auth, track, filename, max_time - elapsed, lang, *args, **kwargs)

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
