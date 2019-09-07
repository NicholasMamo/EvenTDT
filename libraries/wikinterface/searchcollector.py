"""
The search collector is used to look for articles in Wikipedia.
"""

import asyncio
import json
import math
import re
import time
import urllib.request

from .wikicollector import WikiCollector

class SearchCollector(WikiCollector):
	"""
	The SearchCollector uses the search endpoint to look for articles containing some search terms.
	"""

	def search(self, terms, limit=10):
		"""
		Look for pages containing the given terms.
		The search API is often overloaded and fails.

		:param terms: The search terms.
		:type terms: list
		:param limit: The number of search results to return.
			Wikipedia limits the results to 50, but the collector is built to fetch more.
		:type limit: int

		:return: A list of search results in the form of page titles.
			Their content cann be fetched using these titles.
		:rtype: list
		"""

		terms = [ terms ] if type(terms) == str else terms

		"""
		Do not get more than 50 - Wikipedia's limit.
		"""
		base_endpoint = "action=query&list=search&format=json&srsearch=%s&srlimit=%d" % (urllib.parse.quote(' '.join(terms)), min(50, limit))
		pages = []

		srcontinue = True
		endpoint = base_endpoint + "&sroffset=0" # no offset in the beginning
		while len(pages) < limit and srcontinue:
			"""
			Keep searching until the number of pages that are required have been found or there are more results.
			"""

			response = urllib.request.urlopen(self.BASE_URL + endpoint)
			response = json.loads(response.read().decode("utf-8"))
			if self.validate(response):
				results = response["query"]["search"]

				"""
				Store the page titles
				"""
				pages += [ page["title"] for page in results ]

				"""
				Update the endpoint if there are more pages to collect
				"""
				if "continue" in response:
					endpoint = base_endpoint + "&sroffset=%d" % response["continue"]["sroffset"]
				else:
					srcontinue = False
			else:
				time.sleep(1)

		return pages
