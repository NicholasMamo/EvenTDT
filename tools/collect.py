#!/usr/bin/env python3

"""
A tool to collect tweets.

The tool collects a corpus of tweets.
Each event, described by the first tracking keyword, has its own directory.
All related corpora are stored together in this directory.
Each corpus is a JSON file, where each line is one tweet.

To run the script, use:

.. code-block:: bash

    ./tools/collect.py \\
		-t '#ARSWAT' Arsenal Watford \\
		-o data

Accepted arguments:

	- -t --track			<Required> A list of tracking keywords.
	- -o --output			<Required> The data directory where the corpus should be written.
	- -u --understanding	<Optional> The length of the understanding period in minutes. Defaults to an hour.

The implemented modes of operation are:

	- -U					<Optional> Collect the understanding corpus.
"""

import argparse
import json
import os
import sys
import time

sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(1, os.path.join(sys.path[0], '../libraries'))

from logger import logger
from twitter.twevent.listener import TweetListener

from tweepy import OAuthHandler
from tweepy import Stream

import conf

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- -t --track			<Required> A list of tracking keywords.
		- -o --output			<Required> The data directory where the corpus should be written.
		- -U					<Optional> Collect the understanding corpus.
		- -u --understanding	<Optional> The length of the understanding period in minutes. Defaults to an hour.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Collect a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-t', '--track', nargs='+', type=str, required=True,
						action='append', help='<Required> The initial tracking keywords.')
	parser.add_argument('-o', '--output', nargs='+', type=str, required=True,
						help='<Required> The data directory where the corpus should be written.')
	parser.add_argument('-u', '--understanding', nargs='?', type=int,
						default=60, required=False,
						help='<Optional> The length of the understanding period in minutes. Defaults to an hour.')

	"""
	The modes of operation.
	"""

	parser.add_argument('-U', action='store_true',
						help='<Optional> Collect only the understanding corpus.')

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

	output = args.output[0]
	track = args.track[0]
	data_dir = os.path.join(output, track[0])

	if not os.path.exists(data_dir):
		os.makedirs(data_dir)

	"""
	Set up the authentication with the Twitter Stream API.
	"""

	auth = OAuthHandler(conf.ACCOUNTS[0]['CONSUMER_KEY'], conf.ACCOUNTS[0]['CONSUMER_SECRET'])
	auth.set_access_token(conf.ACCOUNTS[0]['ACCESS_TOKEN'], conf.ACCOUNTS[0]['ACCESS_TOKEN_SECRET'])

	"""
	If only the understanding corpus needs to be collected, track normally during the understanding period.
	"""
	if args.U:
		file_name = os.path.join(data_dir, 'understanding.json')

		start = time.time()
		logger.info('Starting to collect understanding corpus')
		with open(file_name, 'w') as file:
			listener = TweetListener(file, max_time=args.understanding * 60, silent=True)
			stream = Stream(auth, listener)
			stream.filter(track=track, languages=["en"])
		logger.info('Understanding corpus collected')
		end = time.time()

		"""
		Save the meta data of the collected file.
		"""
		meta_file_name = os.path.join(data_dir, 'understanding.meta.json')
		with open(meta_file_name, 'w') as meta_file:
			meta = {
				'keywords': track,
				'output': file_name,
				'start': start,
				'end': end,
			}
			meta_file.write(json.dumps(meta) + "\n")

if __name__ == "__main__":
	main()
