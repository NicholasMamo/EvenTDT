"""
The info collector is used to fetch information about Wikipedia pages.
"""

from enum import Enum
import json
import math
import re
import urllib.request

from .textcollector import TextCollector
from .wikicollector import WikiCollector

class PageType(Enum):
	"""
	The type of page.

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

# TODO: Needs testing
class InfoCollector(WikiCollector):
	"""
	The information collector collects general information about pages.
	This includes what kind of page it is.
	"""

	def get_type(self, page_titles):
		"""
		Get the type of page each page title returns.

		:param page_titles: The titles of the pages whose types are desired.
		:type page_titles: list

		:return: A dict with page title-type for keys and values respectively.
		:rtype: dict
		"""

		type_map = {
			"normal": PageType.NORMAL,
			"disambiguation": PageType.DISAMBIGUATION,
			"missing": PageType.MISSING
		}

		types = {}
		stagger = 40
		endpoint = "format=json&action=query&prop=pageprops&titles=%s&redirects" % urllib.parse.quote('|'.join(page_titles))

		if len(page_titles) > stagger:
			for i in range(0, math.ceil(len(page_titles) / stagger)):
				subset = self.get_type(page_titles[(i*stagger):((i+1)*stagger)])
				types.update(subset)
		else:
			response = urllib.request.urlopen(self.BASE_URL + endpoint)
			response = json.loads(response.read().decode("utf-8"))
			pages = response["query"]["pages"]
			redirects = response["query"]["redirects"] if "redirects" in response["query"] else {}

			"""
			Go through each page and find its type.
			"""
			for page in pages.values():
				types[page["title"]] = {
					"title": page["title"],
					"type": type_map["normal"],
				}

				"""
				Once a type is found, stop looking.
				"""
				if "pageprops" not in page:
					types[page["title"]]["type"] = type_map["missing"]
				else:
					for prop in page["pageprops"]:
						if prop in type_map:
							types[page["title"]]["type"] = type_map[prop]
							break

			"""
			Put the original page titles as keys.
			This is useful in case there were any redirects.
			"""
			types = self._resolve_redirects(types, redirects)

		return types

	def is_person(self, page_titles):
		"""
		Go through each page title and check whether it represents a person.
		This works by getting the introduction's text and seeing whether there is birth information.

		:param page_titles: The titles of the pages that need to be checked.
		:type page_titles: list

		:return: A dict with page title-status for keys and values respectively.
		:rtype: dict
		"""

		birth_patterns = [
			re.compile("born [0-9]{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{2,4}"),
			re.compile("born in [0-9]{1,2} (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{2,4}"), # NOTE: Returned by API in https://en.wikipedia.org/wiki/Dar%C3%ADo_Benedetto
			re.compile("born (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{1,2},? [0-9]{2,4}"),
			re.compile("born \([0-9]{4}-[0-9]{2}-[0-9]{2}\)(January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{1,2},? [0-9]{2,4}"), # NOTE: Returned by API in https://en.wikipedia.org/wiki/Valentina_Shevchenko_(fighter)
		]
		persons = { }

		text_collector = TextCollector()
		text = text_collector.get_plain_text(page_titles, introduction_only=True)

		for page, introduction in text.items():
			# persons[page] = len(birth_pattern.findall(introduction)) != 0
			persons[page] = any( len(birth_pattern.findall(introduction)) != 0 for birth_pattern in birth_patterns )

		return persons
