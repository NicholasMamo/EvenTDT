#!/usr/bin/env python3

"""
A tool to extract lexical concepts from terms.
"""

import argparse
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

import tools
from logger import logger

parser = argparse.ArgumentParser(description="Extract terms from domain-specific corpora.")
def setup_args():
    """
    Set up and get the list of command-line arguments.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()

if __name__ == "__main__":
    main()
