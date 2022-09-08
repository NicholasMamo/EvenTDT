#!/usr/bin/env python3

"""
A tool to formally model events extracted by the :mod:`~tools.consume` tool.

To generate the formal event models, provide the input and output files.
The input file should be a timeline or a list of timelines, one for each stream, generated with the :mod:`~tools.consume` tool.
You can also specify a file where to store the metadata:

.. code-block:: bash

	./tools/concepts.py \\
    --file data/timeline.json \\
    --output data/models.json \\
    --meta data/models.meta.json \\
    --modeler UnderstandingModeler

The :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` accepts different types of understanding, which you can provide using the `--participants` and `--concepts` arguments.
In addition to the previously-generated understanding, you can also use NER to extract the Who and the Where using the `--with-ner` argument:

.. code-block:: bash

    ./tools/concepts.py \\
    --file data/timeline.json \\
    --output data/models.json \\
    --meta data/models.meta.json \\
    --modeler UnderstandingModeler \\
    --participants data/participants.json \\
    --concepts data/concepts.json \\
    --with-ner

The output is a JSON file with one event model on each line:

	{
		"who": [ "Verstappen" ],
		"what": [ "won", "race" ],
		"where": [ "Spain" ],
		"when": [ 1658688327 ],
        "why": [ ],
        "how": [ ]
	}

The full list of accepted arguments:

    - ``-f --file``             *<Required>* A timeline or a list of timelines, collected using the :mod:`~tools.consume` tool, to model.
    - ``-o --output``           *<Required>* The file or directory where to save the event models.
    - ``-m --modeler``          *<Required>* The modeler to use to generate models; supported: :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler`.
    - ``--meta``                *<Optional>* The file where to save the meta data.
    - ``--participants``        *<Optional>* A file containing a list of participants, symbolizing the Who and the Where, extracted using the :mod:`~tools.participants` tool.
    - ``--concepts``            *<Optional>* A file containing a list of concepts, symbolizing the What, extracted using the :mod:`~tools.concepts` tool.
    - ``--with-ner``            *<Optional>* Use NER to identify the Who and the Where in addition to the participants.
    - ``--stream-override``     *<Optional>* Override the concepts and use the timeline's streams to identify the What; this parameters avoids linking an event to a stream without having burst.
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
from tools import concepts, consume, participants

from modeling.modelers import UnderstandingModeler

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``             *<Required>* A timeline or a list of timelines collected using the :mod:`~tools.consume` tool, to model.
        - ``-o --output``           *<Required>* The file or directory where to save the event models.
        - ``-m --modeler``          *<Required>* The modeler to use to generate models; supported: :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler`.
        - ``--meta``                *<Optional>* The file where to save the meta data.
        - ``--participants``        *<Optional>* A file containing a list of participants, symbolizing the Who and the Where, extracted using the :mod:`~tools.participants` tool.
        - ``--concepts``            *<Optional>* A file containing a list of concepts, symbolizing the What, extracted using the :mod:`~tools.concepts` tool.
        - ``--with-ner``            *<Optional>* Use NER to identify the Who and the Where in addition to the participants.
        - ``--stream-override``     *<Optional>* Override the concepts and use the timeline's streams to identify the What; this parameters avoids linking an event to a stream without having burst.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Formally model timelines of events.")

    parser.add_argument('-f', '--file', nargs='+', type=str, required=True,
                        help='<Required> A timeline or a list of timelines, collected using the `consume` tool, to model.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file or directory where to save the event models.')
    parser.add_argument('-m', '--modeler', type=modeler, required=True,
                        help='<Required> The modeler to use to generate models; supported: `UnderstandingModeler`.')
    parser.add_argument('--meta', type=str, required=False,
                        help='<Optional> The file where to save the meta data.')
    parser.add_argument('--participants', type=str, required=False,
                        help='<Optional> A file containing a list of participants, symbolizing the Who and the Where, extracted using the `participants` tool.')
    parser.add_argument('--concepts', type=str, required=False,
                        help='<Optional> A file containing a list of concepts, symbolizing the What, extracted using the `concepts` tool.')
    parser.add_argument('--with-ner', required=False, action='store_true',
                        help='<Optional> Use NER to identify the Who and the Where in addition to the participants.')
    parser.add_argument('--stream-override', required=False, action='store_true',
                        help='<Optional> Override the concepts and use the timeline\'s streams to identify the What; this parameters avoids linking an event to a stream without having burst.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()
    cmd, pcmd = tools.meta(args), tools.meta(args) # get the meta arguments
    args = vars(args)

    # load the participants
    participants = tools.participants.load(args['participants']) if args['participants'] else [ ]
    args['participants'], pcmd['participants'] = participants, participants

    # load the concepts
    concepts = tools.concepts.load(args['concepts']) if args['concepts'] else [ ]
    args['concepts'], pcmd['concepts'] = concepts, concepts

    # create the model; the type of the model will be passed as one of the arguments
    modeler = create_modeler(**args)
    cmd['modeler'], pcmd['modeler'] = str(type(modeler).__name__), str(type(modeler).__name__)

    # model the timelines
    models = model(modeler, args['file'])

    # save the metadata and the output
    if args['meta']:
        tools.save(args['meta'], { 'cmd': cmd, 'pcmd': pcmd })
    tools.save(args['output'], models)

def is_own(output):
    """
    Check whether this tool produced the given output.

    :param output: A dictionary containing the output of a tool or a path to it.
    :type output: dict or str

    :return: A boolean indicating whether this tool produced the given output.
    :rtype: bool
    """

    pass

def load(output):
    """
    Load the event models from the given file.

    :param output: A dictionary containing this tool's output or a path to it.
    :type output: dict or str

    :return: The event models in the given output.
    :rtype: list of :class:`~modeling.EventModel`
    """

    return [ ]

def model(modeler, files, *args, **kwargs):
    """
    Formally model the given timelines.

    :param files: A timeline or a list of timelines collected using the :mod:`~tools.consume` tool, to model.
    :type files: list of str

    :return: A list of event models, one for each node on the timeline.
    :rtype: list of :class:`~modeling.EventModel`
    """

    models = [ ]

    for file in files:
        timelines = consume.load(file)
        timelines = timelines if type(timelines) is list else [ timelines ]
        splits = consume.load_splits(file) if len(timelines) > 0 else [ ]
        for timeline in timelines:
            _models = modeler.model(timeline)
            models.extend(_models)

    return models

def modeler(model):
    """
    Convert the given string into a modeler class.
    Only one class is accepted:

        #. :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler`

    :param model: The model string.
    :type model: str

    :return: The event modeler type that corresponds to the given model.
    :rtype: :class:`abc.ABCMeta`
    """

    if model.lower() == 'understandingmodeler':
        return UnderstandingModeler

    raise argparse.ArgumentTypeError(f"Invalid model: {method}")

def create_modeler(modeler, *args, **kwargs):
    """
    Instantiate the modeler from the given class.
    Any arguments and keyword arguments are passed on to the constructor.

    :param modeler: The class type of the modeler.
    :type modeler:

    :return: A new modeler.
    :rtype: :class:`~modeling.modelers.EventModeler`
    """

    return modeler(*args, **kwargs)

if __name__ == "__main__":
    main()
