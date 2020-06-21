import copy
import json
import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from objects.exportable import Exportable

def meta(args):
	"""
	Get the meta arguments.

	:param args: The command-line arguments.
	:type args: :class:`argparse.Namespace`

	:return: The meta arguments as a dictionary.
	:rtype: dict
	"""

	meta = copy.deepcopy(vars(args))
	return meta

def save(file, data):
	"""
	Save the data to the given file.
	The function saves the data as a JSON file.

	:param file: The path to the file where to save the data.
	:type file: str
	:param data: The data to save.
				 The function expects a dictionary that can be JSON serializable.
				 The function tries to convert the values that cannot be serialized to arrays.
				 Only classes that inherit the :class:`~objects.exportable.Exportable` can be converted to arrays.
				 This is done through the :func:`~objects.exportable.Exportable.to_array` function.
	:type data: dict
	"""

	"""
	Create the directory if it doesn't exist.
	"""
	dir = os.path.dirname(file)
	if not os.path.exists(dir):
		os.mkdir(dir)

	"""
	Encode the data and save it.
	"""
	data = Exportable.encode(data)
	with open(file, 'w') as f:
		f.write(json.dumps(data))
