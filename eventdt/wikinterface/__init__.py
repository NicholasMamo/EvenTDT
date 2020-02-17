"""
The basic Wikipedia API interface uses the `Wikimedia API <https://www.mediawiki.org/wiki/API:Main_page>`_.
This module makes it easier to access the API.
"""

API_ENDPOINT = "https://en.wikipedia.org/w/api.php?"

def is_error_response(response):
	"""
	Validate whether the given Wikipedia response is an error.

	:param response: The response to validate.
	:type response: dict

	:return: A boolean indicating whether the response is valid.
	:rtype: bool
	"""

	return 'error' in response

def revert_redirects(results, redirects, keep_redirects=False):
	"""
	Revert redirections.

	The function takes in search results with keys as the page titles.
	The redirections are those retorned by Wikipedia to redirect these keys.

	:param results: Any results obtained from Wikipedia.
					It is assumed that the keys are the page titles.
	:type results: dict
	:param redirects: The redirects provided by Wikipedia.
					  This dictionary has keys 'from' and 'to'.
	:type redirects: dict
	:param keep_redirects: A boolean indicating whether the redirected pages should be retained.
	:type keep_redirects: bool

	:return: A new dictionary with redirections.
	:rtype: dict
	"""

	pages = dict(results)

	"""
	Recreate the redirection representation.
	The redirects are represented as to-from instead of from-to.
	"""
	targets = { redirect["to"]: redirect["from"] for redirect in redirects }

	for page in results:
		"""
		If a page was redirected, 'redirect' it back.
		"""
		if page in targets:
			pages[targets[page]] = pages[page]

			"""
			If the page was only created because of a redirection, remove it.
			"""
			if not keep_redirects:
				del pages[page]

	"""
	In some cases, two pages may redirect to the same page.
	For example, `Striker (association football)` and `Inside forward` both point to `Forward (association football)`.
	Therefore if a redirection (the `from`) has no page, create a page for it.

	Note that when a query is split, the result could be empty for this missing page might not have been loaded yet.
	This happens when there are more than `x` results and Wikipedia returns only the first `x`.
	The redirection for a page that hasn't been loaded yet is given, but the content isn't there yet.
	Therefore this has to be checked in advance.
	"""
	for page in redirects:
		if page["from"] not in pages and page["to"] in results:
			pages[page["from"]] = results[page["to"]]

	return pages
