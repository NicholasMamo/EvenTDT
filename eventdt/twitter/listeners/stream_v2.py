"""
A class that implements a simple Twitter stream.

Code based on `Twitter's Labs sample code <https://github.com/twitterdev/labs-sample-code/blob/master/Filtered_Stream%20v1/filtered_stream.py>`_.
"""

import requests

class Streamv2():
    """
    A simple class that connects with the Twitter stream for the APIv2.
    The class includes functionality to set the tracking rules.

    :ivar auth: The authentication class, a bearer token authentication.
                The class uses this class to communicate with the APIv2.
    :vartype auth: :class:`~twitter.listeners.bearer_token_auth.BearerTokenAuth`
    """

    RULES_URL = "https://api.twitter.com/2/tweets/search/stream/rules"
    """
    The API endpoint that handles rules.
    """

    STREAM_URL = """https://api.twitter.com/2/tweets/search/stream?expansions=author_id,referenced_tweets.id,in_reply_to_user_id,attachments.media_keys,attachments.poll_ids,geo.place_id,entities.mentions.username,referenced_tweets.id.author_id&\
                    tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,in_reply_to_user_id,lang,non_public_metrics,organic_metrics,possibly_sensitive,promoted_metrics,public_metrics,referenced_tweets,reply_settings,source,withheld&\
                    user.fields=created_at,description,entities,location,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld""".replace(' ', '')
    """
    The API endpoint from where to stream tweets.
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

        response = requests.get(self.STREAM_URL, auth=self.auth, stream=True)

        """
        Keep collecting tweets until the listener decides to stop.
        This is done so that the stream acts just like tweepy.
        """
        collect = True
        for response_line in response.iter_lines():
            collect = listener.on_data(response_line)
            if not collect:
                break

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

        # delete the rules first
        self.delete_all_rules()

        # add the new rules
        payload = { 'add': rules }
        response = requests.post(self.RULES_URL, auth=self.auth, json=payload)

        if response.status_code != 201:
            raise Exception(f"Cannot create rules (HTTP %d): %s" % (response.status_code, response.text))

        return self.get_all_rules()

    def get_all_rules(self):
        """
        Get all the rules with which the stream is listening to tweets.

        :return: The current rules.
        :rtype: list of dict
        """

        response = requests.get(self.RULES_URL, auth=self.auth)

        if response.status_code != 200:
            raise Exception(f"Cannot get rules (HTTP %d): %s" % (response.status_code, response.text))

        # return the rules
        rules = response.json()
        return rules['data'] if 'data' in rules else [ ]

    def delete_all_rules(self):
        """
        Delete all rules.

        :return: The current rules.
        :rtype: list of dict
        """

        # fetch all rules and their IDs
        rules = self.get_all_rules()
        ids = list(map(lambda rule: rule['id'], rules))

        # if there are no rules, fetch all rules as confirmation and return
        if not ids:
            return [ ]

        # delete all rules
        payload = { 'delete': { 'ids': ids } }
        response = requests.post(self.RULES_URL, auth=self.auth, json=payload)

        if response.status_code != 200:
            raise Exception(f"Cannot delete rules (HTTP %d): %s" % (response.status_code, response.text))

        return self.get_all_rules()
