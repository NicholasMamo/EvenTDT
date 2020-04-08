#!/usr/bin/env python3

"""
A tool to collect tweets using the Sampling API.

The tool collects a corpus of tweets.
Each collection has its own directory.
Each corpus is a JSON file, where each line is one tweet.

To run the script, use:

.. code-block:: bash

    ./tools/sample.py \\
	-o data/sample \\
	-t 60

Accepted arguments:

	- ``-t --time``		*<Required>* The time to spend collecting tweets in minutes.
	- ``-o --output``	*<Required>* The data directory where the corpus should be written.
	- ``-a --account``	*<Optional>* The account to use to collect the corpus with, as an index of the configuration's accounts. Defaults to the first account.

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

		- ``-t --time``		*<Required>* The time to spend collecting tweets in minutes.
		- ``-o --output``	*<Required>* The data directory where the corpus should be written.
		- ``-a --account``	*<Optional>* The account to use to collect the corpus with, as an index of the configuration's accounts. Defaults to the first account.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Collect a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-t', '--time', type=int, required=True,
						help='<Required> The time to spend collecting tweets in minutes.')
	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The data directory where the corpus should be written.')
	parser.add_argument('-a', '--account', nargs='?', type=int,
						default=0, required=False,
						help='<Optional> The account to use to collect the corpus with, as an index of the configuration\'s accounts. Defaults to the first account.')

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
	meta = []
	if args.time <= 0:
		raise ValueError("The time must be longer than 0 minutes")

	filename = os.path.join(args.output, 'sample.json')
	start = time.time()
	logger.info('Starting to collect sample')
	collect(auth, filename, args.time * 60)
	logger.info('Sample collected')
	end = time.time()
	meta.append({
		'output': filename,
		'start': start,
		'end': end
	})

	if meta:
		save_meta(os.path.join(args.output, 'meta.json'), meta)

def collect(auth, filename, max_time, lang=None, *args, **kwargs):
	"""
	Collect tweets and save them to the given file.
	The tweets are collected synchronously.
	Any additional arguments or keyword arguments are passed on to the :class:`twitter.twevent.listener.TweetListener` constructor.

	:param auth: The OAuth handler to connect with Twitter's API.
	:type auth: :class:`tweepy.OAuthHandler`
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
			stream.sample(languages=lang)
	except (Exception) as e:
		elapsed = time.time() - start
		logger.warning(f"{e.__class__.__name__} after {elapsed} seconds, restarting for {max_time - elapsed} seconds")
		collect(auth, filename, max_time - elapsed, lang, *args, **kwargs)

def save_meta(filename, meta):
	"""
	Save the metadata of the collected dataset.

	:param filename: The filename where to write the metadata.
	:type filename: str
	:param meta: The metadata to save.
	:type meta: list of dict
	"""
	meta_filename = os.path.join(filename)
	with open(meta_filename, 'w') as meta_file:
		for collection in meta:
			meta_file.write(json.dumps(collection) + "\n")

if __name__ == "__main__":
	main()