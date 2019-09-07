import json

S = "/mnt/data/twitter/FRAGER_APD.json"
s = "/mnt/data/twitter/FRAGER.json"

ids = { }
with open(S, "r") as f:
	for line in f:
		tweet = json.loads(line)
		ids[tweet["id"]] = 1

print("File loaded, comparison to start")

with open(s, "r") as f:
	for line in f:
		tweet = json.loads(line)
		if tweet["id"] not in ids:
			print(tweet["id"], "not found, published at", tweet["created_at"])
