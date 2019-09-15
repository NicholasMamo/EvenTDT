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

	- -U					<Optional> Collect only the understanding corpus.
"""

import argparse
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

import conf

from tweepy import OAuthHandler

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- -t --track			<Required> A list of tracking keywords.
		- -o --output			<Required> The data directory where the corpus should be written.
		- -u --understanding	<Optional> The length of the understanding period in minutes. Defaults to an hour.
		- -U					<Optional> Collect only the understanding corpus.

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

if __name__ == "__main__":
	main()
