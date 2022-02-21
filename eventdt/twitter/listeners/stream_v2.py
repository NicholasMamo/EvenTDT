"""
A class that implements a simple Twitter stream.

Code based on `Twitter's Labs sample code <https://github.com/twitterdev/labs-sample-code/blob/master/Filtered_Stream%20v1/filtered_stream.py>`_.
"""

class Streamv2():
    """
    A simple class that connects with the Twitter stream for the APIv2.
    The class includes functionality to set the tracking rules.

    :ivar auth: The authentication class, a bearer token authentication.
                The class uses this class to communicate with the APIv2.
    :vartype auth: :class:`~twitter.listeners.bearer_token_auth.BearerTokenAuth`
    """

    def __init__(self, auth):
        """
        Initialize the stream with the bearer token authentication.

        :param auth: The authentication class, a bearer token authentication.
                    The class uses this class to communicate with the APIv2.
        :type auth: :class:`~twitter.listeners.bearer_token_auth.BearerTokenAuth`
        """

        self.auth = auth

    def connect(self, listener):
        """
        Connect with the stream, invoking the listener whenever it receives a tweet.

        :param listener: The tweet listener, which will process incoming tweets.
        :type listener: :class:`~tweepy.streaming.StreamListener`
        """

        pass

    def set_rules(self, rules):
        """
        Set the rules with which to collect tweets.

        :param rules: The list of rules with which to collect tweets.
                      The rules should be provided as a list of dictionaries.
                      Rules include a value and a descriptive tag, such as `{ 'value': '(lyon OR milan) lang:en', 'tag': 'football cities' }`.
                      More information on rules on `Twitter's API documentation <https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule>`_.
        :type rules: list of dict

        :return: The current rules.
        :rtype: list of dict
        """

        pass

    def get_all_rules(self):
        """
        Get all the rules with which the stream is listening to tweets.

        :return: The current rules.
        :rtype: list of dict
        """

        pass

    def delete_all_rules(self):
        """
        Delete all rules.

        :return: The current rules.
        :rtype: list of dict
        """

        pass
