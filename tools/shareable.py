#!/usr/bin/env python3

"""
The shareable tool is used to convert tweet datasets into shareable datasets.
As per `Twitter's Developer Policy <https://developer.twitter.com/en/developer-terms/policy>`_, only tweet IDs can be shared.
Therefore this tool retains only the tweet IDs from corpora.

To run this tool, use the following:

.. code-block:: bash

    ./tools/shareable.py
"""

import argparse

def setup_args():
    """
    Set up and get the list of command-line arguments.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Make a dataset shareable.")

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    """
    Set up the arguments, create the tokenizer and prepare the data directory.
    """
    args = setup_args()

if __name__ == "__main__":
    main()
