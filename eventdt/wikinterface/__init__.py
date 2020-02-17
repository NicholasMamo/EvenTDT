"""
The basic Wikipedia API interface uses the `Wikimedia API <https://www.mediawiki.org/wiki/API:Main_page>`_.
This module makes it easier to access the API.
"""

API_ENDPOINT = "https://en.wikipedia.org/w/api.php?"
"""
:var API_ENDPOINT: The Wikipedia API endpoint.
:vartype API_ENDPOINT: str
"""

def is_error_response(response):
	"""
	Validate whether the given Wikipedia response is an error.

	:param response: The response to validate.
	:type response: dict

	:return: A boolean indicating whether the response is valid.
	:rtype: bool
	"""

	return 'error' in response

def construct_url(parameters=None):
	"""
	Construct the URL using the given parameters.

	:param parameters: The list of GET parameters to send.
					   The parameter values can be either strings or booleans.
					   If a parameter is a boolean and `True`, it is added without a value.
					   If a parameter is a boolean and `False`, it is excluded altogether
	:type parameters: dict or None

	:return: The URL with any GET parameters provided.
	:rtype: str
	"""

	url = f"{API_ENDPOINT}"

	"""
	If parameters are given, they are filtered for `False` boolean values.
	Then, they are added as query parameters.
	"""
	if parameters:
		parameters = {
			key: value for key, value in parameters.items() if type(value) is not bool or value
		}

		parameter_strings = [ f"{key}" if type(value) is bool else f"{key}={value}" for key, value in parameters.items() ]
		url = url + '&'.join(parameter_strings)

	return url

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
