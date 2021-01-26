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
    - ``--meta``                             *<Optional>* The file where to save the meta data, defaults to [--file].meta.json.
"""

import argparse

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``             *<Required>* The original corpus collected by the :mod:`~tools.collect` tool.
        - ``-o --output``           *<Required>* The file where to save the shareable corpus.
        - ``--meta``                *<Optional>* The file where to save the meta data, defaults to [--file].meta.json.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Make a dataset shareable.")

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The original corpus collected by the `collect` tool.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the shareable corpus.')
    parser.add_argument('--meta', type=str, required=False,
                        help='<Optional> The file where to save the meta data, defaults to [--file].meta.json.')

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
