#!/usr/bin/env python3

"""
The meta tool extracts and pretty-prints metadata from files generated by EvenTDT's tools.
To run the tool, use:

.. code-block:: bash

    ./tools/meta.py \\
    --file idf.json

The tool automatically highlights the parameters that were provided in the command.
This does not work, however, with single-character parameters since the meta tool is unaware of their mappings.

In addition to extracting the metadata from files, it is also possible to extract information from entire ``.tar.gz`` archives.
This tool can extract corpus information, collected using the :mod:`~tools.collect` tool.

.. code-block:: bash

    ./tools/meta.py \\
    --file #ManCityOL.tar.gz

The full list of accepted arguments:

    - ``-f --file``     *<Required>* The file from where to print the metadata, which must have been generated by an EvenTDT tool, or a ``.tar.gz`` file with a collected corpus.
"""

import argparse
from datetime import datetime
import json
import os
import re
import tarfile

parser = argparse.ArgumentParser(description="Extract the metadata from files generated by EvenTDT's tools.")

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``     *<Required>* The file from where to print the metadata, which must have been generated by an EvenTDT tool, or a ``.tar.gz`` file with a collected corpus.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The file from where to print the metadata, which must have been generated by an EvenTDT tool, or a `.tar.gz` file with a collected corpus.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    args = setup_args()
    file = args.file
    extension = '.'.join(file.split(os.extsep)[1:])
    if extension == 'json':
        pprint(file)
    elif extension == 'tar.gz':
        pprint_tar(file)
    else:
        parser.error("Unsupported file extension; supported 'json' and 'tar.gz'.")

def pprint(file):
    """
    Pretty-print the metadata from the given file.

    :param file: The path to the file from where to print the metadata.
    :type file: str
    """

    with open(file) as f:
        data = json.loads(''.join(f.readlines()))
        cmd, pcmd = data['cmd'], data['pcmd']
        del data

        """
        Print the general metadata first.
        """
        print(f"Generated on { cmd['_date'] }")
        print("=======================================")
        print(f"{ cmd['_cmd'] }")
        print()

        """
        Extract the parameters that were actually provided.
        """
        param_pattern = re.compile("--(.+?)(\s|$)")
        params = [ param[0] for param in param_pattern.findall(cmd['_cmd']) ]

        """
        Go through the rest of the metadata and print it.
        Skip the general metadata generated by the tool, which starts with an underscore.
        """
        for key, value in cmd.items():
            if key.startswith('_'):
                continue

            """
            If the parameter was given as a command-line parameter, highlight it.
            """
            key = key.replace('_', '-')
            if key in params:
                print(f"\033[0;36m{ key }: { value }\033[0;39m")
            else:
                print(f"{ key }: { value }")

def pprint_tar(archive):
    """
    Pretty-print the metadata from the given .tar.gz archive.
    This function assumes that the contents include files created by the :mod:`~tools.collect` tool.

    :param archive: The path to the archive from where to print the metadata.
    :type archive: str
    """

    details = { 'understanding': { }, 'event': { }, 'sample': { } }

    tar = tarfile.open(archive, "r:gz")
    files = [ 'meta.json', 'understanding.json', 'event.json', 'sample.json' ]
    for member in tar.getmembers():
        name = member.name
        basename = os.path.basename(name)
        full_path = name.split('/')
        if basename in files and not ('.out' in full_path or '.cache' in full_path):
            file = tar.extractfile(member)

            # read the meta.json file differently from the others
            if basename == 'meta.json':
                content = json.loads(file.read())
                details['sample'] = details.get('sample', { })
                details['understanding'] = details.get('understanding', { })
                details['event'] = details.get('event', { })

                details['understanding'].update(content.get('understanding', { }))
                details['event'].update(content.get('event', { }))
                if not any( details[corpus] for corpus in details ):
                    details['sample'].update(content)
            else:
                corpus = basename.split('.')[0]
                collected = 0
                while file.readline():
                    collected += 1
                details[corpus].update({ 'collected': collected })

    """
    Print the metadata for each corpus.
    """
    for corpus in [ 'understanding', 'event', 'sample' ]:
        if not details[corpus]:
            continue

        start, end = datetime.fromtimestamp(details[corpus]['start']), datetime.fromtimestamp(details[corpus]['end'])

        print(f"{ corpus.title() }")
        print("=======================================")
        print(f"Collected { details[corpus]['collected'] } tweets between { start.strftime('%Y-%m-%d %H:%M:%S') }–{ end.strftime('%Y-%m-%d %H:%M:%S') }")
        if 'keywords' in details[corpus]:
            print(f"Keywords: { ', '.join(details[corpus]['keywords']) }")
        print()

if __name__ == "__main__":
    main()
