"""
The text collector is used to fetch data from Wikipedia.
"""

import json
import math
import re
import urllib.request

from .wikicollector import WikiCollector

class TextCollector(WikiCollector):
	"""
	The TextCollector class creates an interface to fetch information from Wikipedia.
	It abstracts obscure parameters.
	"""

	def get_plain_text(self, page_titles, introduction_only=False):
		"""
		Get the plain text content of the pages with the given titles.

		:param page_titles: The titles of the pages from where to get the plain text.
		:type page_titles: list
		:param introduction_only: A boolean indicating whether to get only the introduction's text.
		:type introduction_only: bool

		:return: A dict with page title-text pairs for keys and values respectively.
		:rtype: dict
		"""

		# TODO: Surround requests with try-catch, and same for the other wikinterfaces

		text = {}
		stagger = 40
		base_endpoint = "format=json&action=query&prop=extracts&exlimit=20&explaintext&titles=%s&redirects%s" % (urllib.parse.quote('|'.join(page_titles)), "&exintro" if introduction_only else "")

		"""
		In some cases, the GET arguments could become far too long.
		Therefore in such cases, stagger the process.
		"""
		if len(page_titles) > stagger:
			for i in range(0, math.ceil(len(page_titles) / stagger)):
				subset = self.get_plain_text(page_titles[(i*stagger):((i+1)*stagger)], introduction_only=introduction_only)
				text.update(subset)
		else:
			excontinue = 0
			if len(page_titles) > 20:
				while excontinue is not None:
					endpoint = "%s&excontinue=%s" % (base_endpoint, excontinue)
					response = urllib.request.urlopen(self.BASE_URL + endpoint)
					response = json.loads(response.read().decode("utf-8"))

					pages = response["query"]["pages"]
					redirects = response["query"]["redirects"] if "redirects" in response["query"] else {}

					for page in pages.values():
						if "extract" in page:
							text[page["title"]] = page["extract"]

					"""
					Put the original page titles as keys.
					This is useful in case there were any redirects.
					"""
					text = self._resolve_redirects(text, redirects)

					excontinue = response["continue"]["excontinue"] if "continue" in response else None
			elif len(page_titles) > 0:
				endpoint = base_endpoint

				response = urllib.request.urlopen(self.BASE_URL + endpoint)
				response = json.loads(response.read().decode("utf-8"))
				
				pages = response["query"]["pages"]
				redirects = response["query"]["redirects"] if "redirects" in response["query"] else {}

				for page in pages.values():
					if "extract" in page:
						text[page["title"]] = page["extract"]

				"""
				Put the original page titles as keys.
				This is useful in case there were any redirects.
				"""
				text = self._resolve_redirects(text, redirects)

		return text
