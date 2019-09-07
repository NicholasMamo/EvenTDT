"""
The link collector is used to collect links from Wikipedia pages.
"""

import json
import math
import re
import urllib.request

from .wikicollector import WikiCollector

class LinkCollector(WikiCollector):
	"""
	The LinkCollector class is responsible for collecting links from Wikipedia articles.

	:cvar REFERENCE_PATTERN: The regex pattern to look for references.
	:vartype REFERENCE_PATTERN: :class:`re.RegexObject`
	:cvar HTML_COMMENTS_PATTERN: The regex pattern to look for HTML comments.
	:vartype HTML_COMMENTS_PATTERN: :class:`re.RegexObject`
	:cvar LINK_PATTERN: The regex pattern to look for internal links.
	:vartype LINK_PATTERN: :class:`re.RegexObject`
	"""

	REFERENCE_PATTERN = re.compile("<ref(.|\\n)*?((\/>)|(>(.|\\n)*?<\/ref>))")
	HTML_COMMENTS_PATTERN = re.compile("<!--(.|\n)+?-->")
	LINK_PATTERN = re.compile("\[\[(?!File|#)(.*?)(\|.*?)?\]\]")

	def get_recursive_links(self, seed, max_level, separate=True, encoding=None, collected_links=None, first_section_only=False):
		"""
		Keep fetching links, starting from the seed set.
		Important - this is a very expensive operation as it grows exponentially.
		If the first_section_only flag is True, links are only fetched from the first section.

		:param seed: The seed set, representing the pages from where to start (or continue) looking.
		:type seed: list
		:param max_level: The maximum level to traverse.
		:type max_level: int
		:param separate: A boolean indicating whether the links should be separated according to the source.
			The alternative is to get a set of all the encountered links.
		:type separate: bool
		:param encoding: The encoding to use.
		:type encoding: str
		:param collected_links: Any links that have already been collected.
		:type collected_links: list
		:param first_section_only: A boolean indicating whether links should only be fetched from the first section.
			The first section is usually the introduction.
			This flag may be set to limit the number of links that are retrieved since they grow exponentially.
		:type first_section_only: bool

		:return: A list of links.
		:rtype: dict if the separate flag is True, list otherwise
		"""

		"""
		In the base case, get a list of links again, and stop looking
		In the recursive case, fetch the links, and use these same links to look for outgoing links from them
		"""

		collected_links = list() if collected_links is None else collected_links

		seed = list(set(seed).difference(set(collected_links))) # remove duplicates and links that were already collected
		if max_level <= 1:
			return self.get_links(list(seed), separate=separate, encoding=encoding, first_section_only=first_section_only)
		else:
			links = self.get_links(list(seed), separate=separate, encoding=encoding, first_section_only=first_section_only) # get the links from this level
			if separate:
				flattened_links  = [link for link_set in links.values() for link in link_set]
				next_links = next_links = self.get_recursive_links(flattened_links,
																	max_level=(max_level - 1),
																	separate=separate,
																	encoding=encoding,
																	collected_links=list(set(seed + collected_links)),
																	first_section_only=first_section_only) # go a level deeper
				links.update(next_links)
				return { page_title: list(set(links[page_title])) for page_title in links }
			else:
				next_links = self.get_recursive_links(links,
														max_level=(max_level - 1),
														separate=separate, encoding=encoding,
														collected_links=list(set(seed + collected_links)),
														first_section_only=first_section_only)
				return list(set(links + next_links))

	def get_links(self, page_titles, separate=True, encoding=None, first_section_only=False):
		"""
		Get a list of outgoing links from the given list of page title
		The returned links may be separated according to the pages
		"""

		if len(page_titles) == 0:
			return {}

		"""
		Since there is a 2048-character limit on GET requests, stagger the searches.
		"""
		break_point = 50
		if len(page_titles) > break_point:
			links = { page_title: [] for page_title in page_titles }
			for i in range(0, math.ceil(len(page_titles)/float(break_point))):
				"""
				Pages are always fetched separately, and then merged later if need be.
				"""
				new_links = self.get_links(page_titles[(i * break_point):((i + 1) * break_point)], separate=True, encoding=encoding, first_section_only=first_section_only)
				for page_title, link_set in new_links.items():
					links[page_title] = links.get(page_title, []) + link_set

			if separate:
				return { page_title: list(set(links[page_title])) for page_title in links }
			else:
				return list(set([ title for page_title in page_titles for title in links[page_title] ])) # if need be, flatten the list
		else:
			page_titles = [ page_title.decode("utf-8") if type(page_title) == bytes else page_title for page_title in page_titles ]
			links = { page_title: [] for page_title in page_titles }

			if first_section_only:
				base_endpoint = "format=json&action=query&prop=revisions&rvprop=content&rvsection=0&explaintext=&titles=%s&redirects" % (urllib.parse.quote('|'.join(page_titles)))
			else:
				base_endpoint = "action=query&titles=%s&prop=links&pllimit=500&format=json&redirects" % (urllib.parse.quote('|'.join(page_titles)))

			"""
			The collector keeps looking for links until the batch is complete.
			"""
			endpoint = base_endpoint
			while True:
				response = urllib.request.urlopen(self.BASE_URL + endpoint)
				response = json.loads(response.read().decode("utf-8"))

				if "query" in response:
					pages = response["query"]["pages"]
					redirects = response["query"]["redirects"] if "redirects" in response["query"] else {}

					"""
					Go through each page, fetching its content
					"""
					for page in pages:
						title = pages[page]["title"]
						if (first_section_only):
							internal_links = self.get_intro_links(pages[page], encoding=encoding)
						else:
							internal_links = self.get_all_links(pages[page], encoding=encoding)
						links[title] = links.get(title, []) + internal_links

					"""
					Put the original page titles as keys.
					This is useful in case there were any redirects.
					"""
					links = self._resolve_redirects(links, redirects)

					"""
					If there are no more links to fetch, stop iterating
					If the limit was reached, the collector must have stopped midway
					Therefore, the endpoint is updated to continue looking from where it left off
					"""
					if "batchcomplete" in response:
						break
					elif "continue" in response:
						endpoint = base_endpoint + "&plcontinue=%s" % urllib.parse.quote(response["continue"]["plcontinue"])

			if separate:
				return { page_title: list(set(links[page_title])) for page_title in links }
			else:
				return list(set([ title for page_title in links for title in links[page_title] ])) # if need be, flatten the list

	def get_intro_links(self, page, encoding=None):
		"""
		Get a list of outgoing links from the given list of page titles, but only from the first section, usually the introduction
		The returned links may be separated according to the pages
		"""

		if "revisions" in page:
			latest_revision = page["revisions"][0]
			content = latest_revision["*"]
			content = self.REFERENCE_PATTERN.sub("", content) # remove references
			content = self.HTML_COMMENTS_PATTERN.sub("", content) # remove HTML comments
			internal_links = self.LINK_PATTERN.findall(content) # fetch all internal links
			internal_links = [ internal_link[0] for internal_link in internal_links ] # isolate the internal links, ignoring the labels
			return internal_links
		else:
			return []

	def get_all_links(self, page, encoding=None):
		"""
		Get a list of outgoing links from the given list of page titles
		The returned links may be separated according to the pages
		"""

		if "links" in page:
			internal_links = [link["title"].encode(encoding) if encoding else link["title"] for link in page["links"]]
			return internal_links
		else:
			return []
