#!/usr/bin/env python3

from twarc import Twarc2, expansions
import json

# Replace your bearer token below
client = Twarc2(bearer_token="XYZ")

# NOTE: twarc automatically expands everything. See the `__twarc` key in each collected tweet for the full list of expansions.

def main():
    # Remove existing rules
    existing_rules = client.get_stream_rules()
    if 'data' in existing_rules and len(existing_rules['data']) > 0:
        rule_ids = [rule['id'] for rule in existing_rules['data']]
        client.delete_stream_rule_ids(rule_ids)

    # Add new rules
    # Replace the rules below with the ones that you want to add as discussed in module 5
    new_rules = [
        {"value": "#engger lang:en", "tag": "euro 2020"},
        {"value": "covid", "tag": "corona-related-tweets"}
    ]
    added_rules = client.add_stream_rules(rules=new_rules)

    # Connect to the filtered stream
    for count, result in enumerate(client.stream()):
        # The Twitter API v2 returns the Tweet information and the user, media etc.  separately
        # so we use expansions.flatten to get all the information in a single JSON
        tweet = expansions.flatten(result)
        # Here we are printing the full Tweet object JSON to the console
        print(json.dumps(tweet)) # prints a list with a dictionary, the tweet, but seemingly each list contains only one tweet
        # Replace with the desired number of Tweets
        if count > 100:
            break

    # Delete the rules once you have collected the desired number of Tweets
    rule_ids = [rule['id'] for rule in added_rules['data']]
    client.delete_stream_rule_ids(rule_ids)


if __name__ == "__main__":
    main()
