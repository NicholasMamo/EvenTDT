#!/usr/bin/env python3

"""
The summarization tool receives a timeline and creates a summary for each node.
This tool is meant to summarize the ``consume`` tool's output retrospectively, after all tweets have been assigned to the correct cluster.
Moreover, the summarization tool makes it easier to experiment with different parameters on the fly.

To run the script, use:

.. code-block:: bash

    ./tools/summarize.py
"""

import argparse

def setup_args():
	"""
	Set up and get the list of command-line arguments.
	"""

	parser = argparse.ArgumentParser(description="Summarize a timeline.")

	args = parser.parse_args()
	return args

def main():
	"""
	Main program loop.
	"""

	args = setup_args()

if __name__ == "__main__":
	main()
