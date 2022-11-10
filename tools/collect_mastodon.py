#!/usr/bin/env python3

import os
import sys

file_path = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(file_path, '..')
lib = os.path.join(root, 'eventdt')
sys.path.insert(-1, root)
sys.path.insert(-1, lib)

from config import conf
import mastodon
from mastodon import Mastodon, StreamListener

class MastodonListener(StreamListener):
	# documentation: https://mastodonpy.readthedocs.io/en/stable/index.html#mastodon.Mastodon.stream_public

	def on_update(self, status):
		if status['language'] == 'en':
			print(status['url'])

	def on_unknown_event(self, name, event):
		pass

	def on_announcement_reaction(self, announcement):
		pass

# to consume the public stream, either create an application using the API (useful when an instance is not allowing new registrations)
# Mastodon.create_app('eventdt', api_base_url='https://mastodon.online', to_file='eventdt_clientcred.secret')
# client = Mastodon(client_id='eventdt_clientcred.secret', api_base_url='https://mastodon.online')

# ... or create an application from Mastodon and provide the client credentials and access token
client = Mastodon(client_id=conf.MASTODON[0]['CLIENT_ID'], client_secret=conf.MASTODON[0]['CLIENT_SECRET'],
				   access_token=conf.MASTODON[0]['ACCESS_TOKEN'], api_base_url='https://mastodon.social')

# NOTE: the public API seems to be the federated timeline, and the local API is the instance timeline
listener = MastodonListener()
client.stream_local(listener, run_async=False, timeout=300, reconnect_async=False, reconnect_async_wait_sec=5)