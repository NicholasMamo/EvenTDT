"""
The info collector fetches information about Wikipedia pages.
"""

from enum import Enum
import json
import math
import re
import urllib.request

from . import *
from . import text

class ArticleType(Enum):
	"""
	The type of article.

	:cvar NORMAL: A normal article on Wikipedia.
	:vartype NORMAL: int
	:cvar DISAMBIGUATION: An article that could not be resolved,
						  These articles contain links to other articles.
	:vartype NORMAL: int
	:cvar MISSING: No article exists with the given name.
	:vartype MISSING: int
	"""

	NORMAL = 0
	DISAMBIGUATION = 1
	MISSING = 2

def types(titles):
	"""
	Get the type of page each page title returns.

	:param titles: The titles of the pages whose types are desired.
	:type titles: list of str or str

	:return: A dictionary with page titles as keys and the types as :class:`wikinterface.info.ArticleType` values.
	:rtype: dict
	"""

	types = { }

	titles = titles if type(titles) is list else [ titles ]

	stagger = 20
	parameters = {
		'format': 'json',
		'action': 'query',
		'prop': 'pageprops',
		'titles': urllib.parse.quote('|'.join(titles)),
		'redirects': True, # allow redirects
		'excontinue': 0, # the page number from where to continue
	}

	"""
	When there are many page titles, the GET parameters could become far too long.
	Therefore in such cases, stagger the process.
	"""
	if len(urllib.parse.quote('|'.join(titles))) > 1024:
		for i in range(0, math.ceil(len(titles) / stagger)):
			subset = collect(titles[(i * stagger):((i + 1) * stagger)],
							 introduction_only=introduction_only)
			types.update(subset)
		return types

	"""
	If page titles are given, collect information about them.
	Pages are returned 20 at a time.
	When this happens, the response contains a continue marker.
	The loop continues fetching requests until there are no such markers.
	"""
	if len(titles):
		while parameters['excontinue'] is not None:
			endpoint = construct_url(parameters)
			response = urllib.request.urlopen(endpoint)
			response = json.loads(response.read().decode('utf-8'))

			if is_error_response(response):
				raise RuntimeError(response)

			"""
			Extract the page types from the responses.
			"""
			pages = response['query']['pages']
			redirects = response['query']['redirects'] if 'redirects' in response['query'] else {}

			"""
			Go through each page and find its type.
			By default, pages are normal.
			If the page has no properties, it is considered to be missing.
			Otherwise
			"""
			for page in pages.values():
				types[page['title']] = ArticleType.NORMAL

				"""
				Once a type is found, stop looking.
				"""
				if 'pageprops' not in page:
					types[page['title']] = ArticleType.MISSING
				elif 'disambiguation' in page.get('pageprops'):
					types[page['title']] = ArticleType.DISAMBIGUATION

			parameters['excontinue'] = response['continue']['excontinue'] if 'continue' in response else None

		"""
		Put the original page titles as keys.
		This is useful in case there were any redirects.
		"""
		types = revert_redirects(types, redirects)

	return types

def is_person(titles):
	"""
	Go through each page title and check whether it represents a person.
	The function assumes that an article is about a person if it mentions a birth date.

	:param titles: The titles of the pages that need to be checked.
	:type titles: list of str or str

	:return: A dictionary with page titles as keys and booleans as values indicating whether the article represents a person.
	:rtype: dict
	"""

	classes = { }

	"""
	Collect the introductions of the given articles.
	"""
	titles = titles if type(titles) is list else [ titles ]
	extracts = text.collect(titles, introduction_only=True)

	"""
	An article is about a person if it has a birth date.
	The function tries to capture this in the text using one of a number of regular expressions.
	"""
	birth_patterns = [
		re.compile("born [0-9]{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{2,4}"),
		re.compile("born in [0-9]{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{2,4}"), # NOTE: Returned by API in https://en.wikipedia.org/wiki/Dar%C3%ADo_Benedetto
		re.compile("born (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{1,2},? [0-9]{2,4}"),
		re.compile("born \([0-9]{4}-[0-9]{2}-[0-9]{2}\)(January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{1,2},? [0-9]{2,4}"), # NOTE: Returned by API in https://en.wikipedia.org/wiki/Valentina_Shevchenko_(fighter)
	]

	for page, introduction in extracts.items():
		classes[page] = any(len(birth_pattern.findall(introduction)) for birth_pattern in birth_patterns)

	return classes
