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

