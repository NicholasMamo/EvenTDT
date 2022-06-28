#!/usr/bin/env python3

"""
The shareable tool is used to convert tweet datasets into shareable datasets.
As per `Twitter's Developer Policy <https://developer.twitter.com/en/developer-terms/policy>`_, only tweet IDs can be shared.
Therefore this tool retains only the tweet IDs from corpora.

To run this tool, use the following:

.. code-block:: bash

    ./tools/shareable.py \\
    --file data/corpus.json \\
    --output data/shareable.json

By default, the tool saves the meta details to a file in the same directory.
However, you can save the meta file in a different path by providing the ``--meta`` parameter:

.. code-block:: bash

    ./tools/shareable.py \\
    --file data/corpus.json \\
    --output data/shareable.json \\
    --meta meta/shareable.json

The full list of accepted arguments:

    - ``-f --file``                          *<Required>* The original corpus collected by the :mod:`~tools.collect` tool.
    - ``-o --output``                        *<Required>* The file where to save the shareable corpus.
    - ``--meta``                             *<Optional>* The file where to save the meta data, defaults to [--file].meta.

The tool writes one tweet ID on each line in the output file.
"""

import argparse
import json
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

import tools

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``             *<Required>* The original corpus collected by the :mod:`~tools.collect` tool.
        - ``-o --output``           *<Required>* The file where to save the shareable corpus.
        - ``--meta``                *<Optional>* The file where to save the meta data, defaults to [--file].meta.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Make a dataset shareable.")

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The original corpus collected by the `collect` tool.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the shareable corpus.')
    parser.add_argument('--meta', type=str, required=False,
                        help='<Optional> The file where to save the meta data, defaults to [--file].meta.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    # set up the arguments and prepare the data directory.
    args = setup_args()
    cmd = tools.meta(args)
    pcmd = tools.meta(args)
    tools.save(args.output, { }) # to create the directory if it doesn't exist
    write(args.file, args.output)

    meta = args.meta or tools.meta_file(args.output)
    pcmd['meta'] = meta
    tools.save(meta, { 'cmd': cmd, 'pcmd': pcmd })

def write(file, output):
    """
    Make the given file shareable, writing the tweet IDs into the given output file.

    :param file: The path to the original corpus of tweets.
    :type file: str
    :param output: The path where to write the tweet IDs.
    :type output: str
    """

    with open(file, 'r') as infile, \
         open(output, 'w') as outfile:
        for line in infile:
            tweet = json.loads(line)
            outfile.write(f"{ tweet['id_str'] }\n")

if __name__ == "__main__":
    main()
