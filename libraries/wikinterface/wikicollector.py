"""
The basic Wikipedia API interface.
The Wikimedia API is used: https://www.mediawiki.org/wiki/API:Main_page.
"""

from abc import ABC

class WikiCollector(ABC):
	"""
	The WikiCollector defines the basic component of any other classes that connects to Wikipedia.

	:cvar BASE_URL: The API's basic URL - other functions must only append the endpoint themselves.
	:vartype BASE_URL: str
	"""

	BASE_URL = "https://en.wikipedia.org/w/api.php?"

	def validate(self, response):
		"""
		Validate Wikipedia responses.

		:param response: The response to validate.
		:type response: dict

		:return: A boolean indicating whether the response is valid.
		:rtype: bool
		"""

		if "error" in response:
			print("Error: %s" % response["error"]["info"])
			return False

		return True

	def _resolve_redirects(self, results, redirects):
		"""
		The function assumes that the results are organized by page.
		In this case, the redirects are made to be the keys, not the page titles.

		:param results: Any results obtained from Wikipedia.
			It is assumed that the results are grouped according to the page title.
		:type results: dict
		:param redirects: The redirects provided by Wikipedia.
		:type redirects: dict

		:return: A new dictionary with redirections.
		:rtype: dict
		"""

		original_pages = list(results.keys())
		redirected_pages = dict(results)

		"""
		Recreate the redirection representation.
		"""
		targets = { redirect["to"]: redirect["from"] for redirect in redirects }

		for result in results:
			"""
			If a result was redirected, 'redirect' it back.
			"""
			if result in targets:
				"""
				If the redirect target (`to`) existed, do not remove the original key.
				Nonetheless, still reverse the redirection.

				For example, consider `West Ham United` and `West Ham United F.C.`
				`West Ham United` redirects to `West Ham United F.C.`
				If both exist in the result set, applying the reverse redirection would be detrimental.
				In fact, this process would remove `West Ham United F.C.`, which is needed.
				Therefore retain both options.
				"""
				redirected_pages[targets[result]] = redirected_pages[result]
				if result not in original_pages:
					del redirected_pages[result]

		"""
		In some cases, two pages may coalesce.
		For example, `Striker (association football)` and `Inside forward` both point to `Forward (association football)`.
		In these cases, missing redirects (redirect from) are added.

		Note that when a query is split, the result could be empty for this missing page might not have been loaded yet.
		This happens when there are more than `x` results and Wikipedia returns only the first `x`.
		The redirection for a page that hasn't been loaded yet is given, but the content isn't there yet.
		Therefore this has to be checked in advance.
		"""
		for redirect in redirects:
			if redirect["from"] not in redirected_pages:
				if redirect["to"] in results:
					redirected_pages[redirect["from"]] = results[redirect["to"]]

		return redirected_pages
