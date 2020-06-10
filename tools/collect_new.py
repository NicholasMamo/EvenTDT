#!/usr/bin/env python3

import os
import requests
import json
import time
from pprint import pprint
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth

consumer_key = "Qg4UBCaYSTQyco38M6DACls8y"	# Add your API key here
consumer_secret = "eCIhph66A48sqOPQZNDFLLWjeJnCegKU7JvDGzImnQNnT7ze9g"	# Add your API secret key here

stream_url = "https://api.twitter.com/labs/1/tweets/stream/filter?format=detailed&expansions=referenced_tweets.id,entities.mentions.username&user.format=detailed"
rules_url = "https://api.twitter.com/labs/1/tweets/stream/filter/rules"

sample_rules = [
	{ 'value': '(frankfurt OR benfica) lang:en', 'tag': 'single' },
	# { 'value': 'madrid', 'tag': 'single' },
	# { 'value': 'tottenham', 'tag': 'single' },
	# { 'value': 'atletico', 'tag': 'single' },
	# { 'value': 'juventus', 'tag': 'single' },
	# { 'value': 'champions', 'tag': 'single' },
	# { 'value': 'brugges', 'tag': 'single' },
	# { 'value': 'lyon', 'tag': 'single' },
	# { 'value': 'lille', 'tag': 'single' },
	# { 'value': 'barcelona', 'tag': 'single' },
	# { 'value': 'dog has:images', 'tag': 'dog pictures' },
	# { 'value': 'cat has:images -grumpy', 'tag': 'cat pictures' },
]

# Gets a bearer token
class BearerTokenAuth(AuthBase):
	def __init__(self, consumer_key, consumer_secret):
		self.bearer_token_url = "https://api.twitter.com/oauth2/token"
		self.consumer_key = consumer_key
		self.consumer_secret = consumer_secret
		self.bearer_token = self.get_bearer_token()

	def get_bearer_token(self):
		response = requests.post(
			self.bearer_token_url,
			auth=(self.consumer_key, self.consumer_secret),
			data={'grant_type': 'client_credentials'},
			headers={'User-Agent': 'TwitterDevFilteredStreamQuickStartPython'})

		if response.status_code is not 200:
			raise Exception(f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

		body = response.json()
		return body['access_token']

	def __call__(self, r):
		r.headers['Authorization'] = f"Bearer %s" % self.bearer_token
		r.headers['User-Agent'] = 'TwitterDevFilteredStreamQuickStartPython'
		return r


def get_all_rules(auth):
	response = requests.get(rules_url, auth=auth)

	if response.status_code is not 200:
		raise Exception(f"Cannot get rules (HTTP %d): %s" % (response.status_code, response.text))

	return response.json()


def delete_all_rules(rules, auth):
	if rules is None or 'data' not in rules:
		return None

	ids = list(map(lambda rule: rule['id'], rules['data']))

	payload = {
		'delete': {
			'ids': ids
		}
	}

	response = requests.post(rules_url, auth=auth, json=payload)

	if response.status_code is not 200:
		raise Exception(f"Cannot delete rules (HTTP %d): %s" % (response.status_code, response.text))

def set_rules(rules, auth):
	if rules is None:
		return

	payload = {
		'add': rules
	}

	response = requests.post(rules_url, auth=auth, json=payload)

	if response.status_code is not 201:
		raise Exception(f"Cannot create rules (HTTP %d): %s" % (response.status_code, response.text))

def stream_connect(auth):
	collected = 0
	response = requests.get(stream_url, auth=auth, stream=True)
	for response_line in response.iter_lines():
		if response_line:
			response_data = json.loads(response_line)
			collected += 1
			if (not collected % 100):
				print(collected)
			if 'data' in response_data:
				if '…' in response_data['data']['text']:
					# pprint(response_data)
					print('>', response_data['data']['text'])
					pass
				else:
					print('>', response_data['data']['text'])
					pass
			else:
				pprint(response_data)
				pass

bearer_token = BearerTokenAuth(consumer_key, consumer_secret)

def setup_rules(auth):
	current_rules = get_all_rules(auth)
	if 'data' in current_rules and len(current_rules['data']):
		print('deleting rules')
		pprint(current_rules)
		delete_all_rules(current_rules, auth)
	set_rules(sample_rules, auth)


# Comment this line if you already setup rules and want to keep them
setup_rules(bearer_token)

# Listen to the stream.
# This reconnection logic will attempt to reconnect when a disconnection is detected.
# To avoid rate limites, this logic implements exponential backoff, so the wait time
# will increase if the client cannot reconnect to the stream.
timeout = 0
while True:
	stream_connect(bearer_token)
	time.sleep(2 ** timeout)
	timeout += 1
