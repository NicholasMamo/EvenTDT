#!/usr/bin/env python3

"""
Filter the given timelines' nodes by removing retweets, unless doing so would generate an empty node.

.. note::

    This tool removes the structure of the timeline and a lot of valuable information.
    The burst information, in particular, is removed, and the new timelines are constructed as :class:`~summarization.timeline.nodes.document_node.DocumentNode` instances.

The full list of accepted arguments:

    - ``-f --file``             *<Required>* The original timelines generated by the :mod:`~tools.consume` tool.
    - ``-o --output``           *<Required>* The file where to save the cleaned timeline.
"""

import argparse
import csv
from datetime import datetime
import json
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from summarization.timeline.nodes import DocumentNode
import tools
from tools import consume
import twitter

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``             *<Required>* The original timelines generated by the :mod:`~tools.consume` tool.
        - ``-o --output``           *<Required>* The file where to save the cleaned timeline.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Make a dataset shareable.")

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The original timelines generated by the `consume` tool')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the cleaned timeline.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    # set up the arguments and prepare the data directory.
    args = setup_args()

    with open(args.file) as file:
        output = json.loads(''.join(file.readlines()))
        cmd, pcmd = output['cmd'], output['pcmd']

    cmd.update(tools.meta(args))
    pcmd.update(tools.meta(args))

    timeline = clean(args.file)
    tools.save(args.output, { 'cmd': cmd, 'pcmd': pcmd, 'timeline': timeline })

def clean(file):
    """
    Clean the timeline stored in the given file.

    :param file: The original timelines generated by the `consume` tool.
    :type file: str

    :return: A new timeline, without retweets, unless removing them would create an empty node.
    :rtype: :class:`~summarization.timeline.Timeline`
    """

    timelines = consume.load(file)
    timelines = timelines if type(timelines) is list else [ timelines ]
    for timeline in timelines:
        nodes = [ ]
        for node in timeline.nodes:
            if not all( twitter.is_retweet(document.tweet) for document in node.get_all_documents() ):
                documents = [ document for document in node.get_all_documents() if not twitter.is_retweet(document.tweet) ]
                nodes.append(DocumentNode(created_at=node.created_at, documents=documents))
            else:
                nodes.append(node)
        timeline.nodes = nodes
    return timelines

if __name__ == "__main__":
    main()