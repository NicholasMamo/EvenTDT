import copy

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
