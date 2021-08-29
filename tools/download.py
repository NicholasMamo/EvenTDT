#!/usr/bin/env python3

"""
The download tool is used to download tweets from shareable datasets, which are made up of tweet IDs.
The tool expects as input a file with one tweet ID on each line, produced by the :mod:`~tools.shareable` tool.
"""

import argparse
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
sys.path.insert(-1, root)

import tools

def setup_args():
    """
    Set up and get the list of command-line arguments.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Download a shareable dataset.")

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    # set up the arguments
    args = setup_args()

if __name__ == "__main__":
    main()
