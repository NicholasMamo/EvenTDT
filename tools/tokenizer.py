#!/usr/bin/env python3

"""
A tool to tokenize a corpus of tweets.
The tokenizer can be used to pre-process a corpus.

Each line in the tokenizer corresponds to a tweet.
Each line is a JSON object containing, at minimum, the tweet ID and the tokens.

To run the script, use:

.. code-block:: bash

    ./tools/tokenize.py \\
	-f data/sample.json \\
	-o data/idf.json \\
	--remove-unicode-entities \\
	--normalize-words --stem

Accepted arguments:

	- ``-f --file``							*<Required>* The file to use to construct the tokenized corpus.
	- ``-o --output``						*<Required>* The file where to save the tokenized corpus.
	- ``--remove-unicode-entities``			*<Optional>* Remove unicode entities from the tweets.
	- ``--normalize-words``					*<Optional>* Normalize words with repeating characters in them.
	- ``--character-normalization-count``	*<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
	- ``-stem``								*<Optional>* Stem the tokens when constructing the tokenized corpus.

"""
