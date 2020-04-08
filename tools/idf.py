#!/usr/bin/env python3

"""
A tool to create a TF-IDF scheme from a corpus of tweets.

To run the script, use:

.. code-block:: bash

    ./implementation/consume.py \\
	-f data/sample.json \\
	-o data/idf.json

Accepted arguments:

	- ``-f --file``		*<Required>* The file to use to construct the TF-IDF scheme.
	- ``-o --output``	*<Required>* The file where to save the TF-IDF scheme.
"""

import argparse
import copy

def setup_args():
	"""
	Set up and get the list of command-line arguments.

	Accepted arguments:

		- ``-f --file``		*<Required>* The file to use to construct the TF-IDF scheme.
		- ``-o --output``	*<Required>* The file where to save the TF-IDF scheme.

	:return: The command-line arguments.
	:rtype: list
	"""

	parser = argparse.ArgumentParser(description="Consume a corpus of tweets.")

	"""
	Parameters that define how the corpus should be collected.
	"""

	parser.add_argument('-f', '--file', type=str, required=True,
						help='<Required> The file to use to construct the TF-IDF scheme.')
	parser.add_argument('-o', '--output', type=str, required=True,
						help='<Required> The file where to save the TF-IDF scheme.')

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()
def update(idf, tokens):
	"""
	Update the given IDF table with the given tokens.

	:param idf: The IDF table as a dictionary.
				The keys are the tokens and the values are the document frequencies.
	:type idf: dict
	:param tokens: The tokens to add to the IDF.
				   The function automatically gets the set of tokens to remove duplicates.
	:type: list of str
	"""

	idf = copy.deepcopy(idf)
	for token in set(tokens):
		idf[token] = idf.get(token, 0) + 1

	return idf

if __name__ == "__main__":
	main()
