"""
The search collector is used to look for articles containing a particular list of terms.
"""

import json
import re
import time
import urllib.request

from . import *

def collect(terms, limit=10):
	"""
	Look for pages containing the given terms.

	.. warning:

		The search API is often overloaded and fails.

	:param terms: The search terms.
	:type terms: list of str or str
	:param limit: The number of search results to return.
				  Wikipedia limits the results to 50, but the collector can fetch more.
	:type limit: int

	:return: A list of search results in the form of page titles.
			 Their content can be fetched using these titles.
	:rtype: list of str
	"""

	articles = [ ]

	terms = terms if type(terms) is list else [ terms ]

	parameters = {
		'format': 'json',
		'action': 'query',
		'list': 'search',
		'srsearch': urllib.parse.quote(' '.join(terms)),
		'srlimit': min(50, limit), # the search endpoint retrieves at most 50 at a time
		'sroffset': 0
	}

	"""
	Searching until the number of articles that are required have been found or there are no more results.
	Keep only the page titles.
	"""
	while len(results) < limit and continue:
		endpoint = construct_url(parameters)
		response = urllib.request.urlopen(endpoint)
		response = json.loads(response.read().decode("utf-8"))

		"""
		Since errors are common, if one is encountered, sleep for a second and then continue.
		"""
		if not is_error_response(response):
			results = response["query"]["search"]
			articles += [ article["title"] for article in results ]

			"""
			Update the endpoint if there are more search results to collect.
			Otherwise, stop looking immediately.
			"""
			if "continue" in response:
				parameters['sroffset'] = response["continue"]["sroffset"]
			else:
				break
		else:
			time.sleep(1)

	return articles
