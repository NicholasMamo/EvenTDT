"""
A class used to connect with the Twitter APIv2.

Code based on `Twitter's Labs sample code <https://github.com/twitterdev/labs-sample-code/blob/master/Filtered_Stream%20v1/filtered_stream.py>`_.
"""

import requests
from requests.auth import AuthBase

class BearerTokenAuth(AuthBase):
    """
    A class that implements the connection to generate a bearer token and connect with the Twitter APIv2.

    :ivar consumer_key: The unique key identifying the consumer.
    :vartype consumer_key: str
    :ivar consumer_secret: The secret used to confirm the identity of the consumer.
    :vartype consumer_secret: str
    :ivar bearer_token: The generated bearer token.
    :vartype: None or str
    """

    def __init__(self, consumer_key, consumer_secret):
        """
        Initialize the class, saving the consumer key and secret.

        :param consumer_key: The unique key identifying the consumer.
        :type consumer_key: str
        :param consumer_secret: The secret used to confirm the identity of the consumer.
        :type consumer_secret: str
        """

        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.bearer_token = self.get_bearer_token()

    def get_bearer_token(self):
        """
        Generate the bearer access token.

        :return: The generated bearer token.
        :rtype: str
        """

        bearer_token_url = "https://api.twitter.com/oauth2/token"

        response = requests.post(
            bearer_token_url,
            auth=(self.consumer_key, self.consumer_secret),
            data={'grant_type': 'client_credentials'},
            headers={'User-Agent': 'EvenTDT'})

        if response.status_code != 200:
            raise Exception(f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

        body = response.json()
        return body['access_token']

    def __call__(self, request):
        """
        Code to call upon every request.
        The code adds two headers: the access token and the user agent.

        :param request: The request to which the function will add headers.
        :type request: :class:`requests.models.PreparedRequest`

        :return: The updated request.
        :rtype: :class:`requests.models.PreparedRequest`
        """

        request.headers['Authorization'] = f"Bearer %s" % self.bearer_token
        request.headers['User-Agent'] = 'EvenTDT'
        return request
