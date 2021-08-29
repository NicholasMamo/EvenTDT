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

The full list of accepted arguments:

    - ``-f --file``                          *<Required>* The shareable corpus created by the :mod:`~tools.collect` tool.
    - ``-o --output``                        *<Required>* The file where to save the downloaded corpus.
    - ``--meta``                             *<Optional>* The file where to save the meta data, defaults to [--file].meta.
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

    meta = args.meta or f"{ args.output }.meta"
    pcmd['meta'] = meta
    tools.save(meta, { 'cmd': cmd, 'pcmd': pcmd })

if __name__ == "__main__":
    main()
