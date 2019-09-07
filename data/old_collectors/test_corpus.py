import json
import nltk
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '../'))

from nltk.corpus import stopwords
from libraries.vector.nlp.tokenizer import Tokenizer

t = Tokenizer()

def get_named_entities(text, filter=[]):
	tokens = t.tokenize(text, case_fold=False, remove_numbers=False, remove_punctuation=False, min_length=1, stem=False)
	pos_tags = nltk.pos_tag(tokens)
	entities = nltk.ne_chunk(pos_tags)

	named_entities = []
	current_entity, current_entity_type = [], ""
	for entity in entities:
		if type(entity) == nltk.tree.Tree:
			named_entity_type = entity.label()
			named_entity_tokens = [pair[0].lower() for pair in entity]
			named_entity_tokens = [token for token in named_entity_tokens if token not in filter]
			name = ' '.join(named_entity_tokens)
			name = name.strip()
			named_entities.append(name.lower())
	return [entity for entity in named_entities if len(entity) > 0]

lines = 7000
token_dict, entity_dict = {}, {}
to_remove = ["communityshield", "cfc", "mcfc", "chemci", "mciche", "community", "shield", "manchester", "city", "chelsea"]
# to_remove = ["beleng", "engbel", "bel", "eng"]
with open("data/twitter/community_shield_sample.json", "r") as f:
	f.readline()
	for i in range(0, lines):
		line = f.readline()
		data = json.loads(line.replace('\x00', ''))
		if (data["lang"] == "en" and data["user"]["verified"]):
		# if (data["lang"] == "en"):
			tokens = t.tokenize(data["text"], stopwords=stopwords.words("english"), min_length=3)
			for token in tokens:
				if token not in to_remove:
					token_dict[token] = token_dict.get(token, 0) + 1

			entities = get_named_entities(data["text"], filter=to_remove)
			for entity in entities:
				entity_dict[entity] = entity_dict.get(entity, 0) + 1

print((sorted(token_dict.items(), key=lambda x : x[1])[::-1])[:25])
print((sorted(entity_dict.items(), key=lambda x : x[1])[::-1])[:25])
