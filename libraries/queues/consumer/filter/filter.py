"""
A filter object is responsible for filtering out and removing unnecessary data.
This is based on a number of rules.
The comparison objects must support the operators that are used.
"""

import collections
import copy

def true(o1):
	"""
	The result is True.

	:param o1: The boolean to check.
	:type o1: bool

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1

def false(o1):
	"""
	The result is False.

	:param o1: The boolean to check.
	:type o1: bool

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return not o1

def lte(o1, o2):
	"""
	Less than or equal to operator.

	:param o1: The first object to use in the comparison.
	:type o1: :class:`object`
	:param o2: The second object to use in the comparison.
	:type o2: :class:`object`

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1 <= o2

def lt(o1, o2):
	"""
	Less than operator.

	:param o1: The first object to use in the comparison.
	:type o1: :class:`object`
	:param o2: The second object to use in the comparison.
	:type o2: :class:`object`

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1 < o2

def gte(o1, o2):
	"""
	Greater than or equal to operator.

	:param o1: The first object to use in the comparison.
	:type o1: :class:`object`
	:param o2: The second object to use in the comparison.
	:type o2: :class:`object`

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1 >= o2

def gt(o1, o2):
	"""
	Greater than operator.

	:param o1: The first object to use in the comparison.
	:type o1: :class:`object`
	:param o2: The second object to use in the comparison.
	:type o2: :class:`object`

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1 > o2

def equal(o1, o2):
	"""
	Equality operator.

	:param o1: The first object to use in the comparison.
	:type o1: :class:`object`
	:param o2: The second object to use in the comparison.
	:type o2: :class:`object`

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1 == o2

def not_equal(o1, o2):
	"""
	Inequality operator.

	:param o1: The first object to use in the comparison.
	:type o1: :class:`object`
	:param o2: The second object to use in the comparison.
	:type o2: :class:`object`

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1 != o2

def in_list(o1, o2):
	"""
	Set membership operator.

	:param o1: The first object to use in the comparison.
	:type o1: :class:`object`
	:param o2: The second object to use in the comparison.
	:type o2: list

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1 in o2

def not_in_list(o1, o2):
	"""
	Set difference operator.

	:param o1: The first object to use in the comparison.
	:type o1: :class:`object`
	:param o2: The second object to use in the comparison.
	:type o2: list

	:return: A boolean indicating the operation's status.
	:rtype: bool
	"""

	return o1 not in o2

class Filter(object):
	"""
	The Filter class receives dict instances and filters them out based on a number of rules.
	Rules are triples of indices, function names and the comparison operators.

	:ivar _rules: The rules used by the filter.
	:vartype _rules: list
	:ivar _delimiter: The separator between indices.
	:vartype _delimiter: str
	"""

	def __init__(self, rules, delimiter=":"):
		"""
		Create the Filter instance based on the given rules.

		:param rules: A list of rules.
			Rules must be given as triplets of the form (index, function, operator).
		:type rules: list
		:param delimiter: The delimiter to use to split the index.
		:type delimiter: str
		"""

		self._rules = rules
		self._delimeter = delimiter

	def set_rules(self, rules):
		"""
		Update the rules.

		:param rules: A list of rules.
			Rules must be given as triplets of the form (index, function, operator).
		:type rules: list
		"""

		self._rules = rules

	def get_operand(self, element, index):
		"""
		Get the operand from the item.
		If the index is not found, the index itself is used as the operand.
		The index is split using the delimiter - each split means going one level deeper.
		Priority is given to strings - if a string is not found as an index, an integer is tried.

		:param element: The current element being searched for the operand.
		:type element: dict
		:param index: The index being searched.
		:type index: str

		:return: The operand if it is found, or the index itself if the operand is not found.
		:rtype: :class:`object`
		"""

		if type(index) == str: # an index can only be split if it is a string
			indices = index.split(self._delimeter)
			curr_element = copy.deepcopy(element)
			"""
			Look for the indices in the item.
			If the index is not found, return the original index as the operand.
			"""
			for i in indices:
				if i in curr_element:
					curr_element = curr_element[i]
				elif i.isdigit() and int(i) in curr_element:
					return curr_element[int(i)]
				else:
					return i

			return curr_element
		else:
			"""
			If the index is not a string, look for the index in the element.
			If it is found, return the value at that index.
			Otherwise, the index itself - which could be an integer value, for example - is returned as the operand.
			"""
			if isinstance(index, collections.Hashable) and index in element:
					return element[index]

			return index

	def filter(self, element):
		"""
		Return a boolean indicating whether the element passes all rules.

		:param element: The current element being searched for the operand.
		:type element: dict

		:return: A boolean indicating whether the element passes all rules.
		:rtype: bool
		"""

		for rule in self._rules:
			"""
			Get the actual operands
			"""
			o1, function = rule[0], rule[1]
			o1 = self.get_operand(element, o1)

			if len(rule) == 3:
				"""
				Some rules have two operands, not only one.
				"""

				o2 = rule[2]
				o2 = self.get_operand(element, o2)

				"""
				Pass the operands through the filter
				"""
				if not function(o1, o2):
					return False
			else:
				"""
				Pass the operands through the filter
				"""
				if not function(o1):
					return False

		return True
