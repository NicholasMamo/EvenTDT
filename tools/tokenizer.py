#!/usr/bin/env python3

"""
The tokenizer tokenizes tweets in a corpus.
Tokenization can be used as a pre-processing step for other tools, such as the :mod:`~tools.terms` and :mod:`~tools.bootstrap` tools.

The tokenizer goes through each line the input file and creates another line in the output file with the tokenized tweet.
This tool always uses the full text to tokenize text.
To generate tokens, you need to provide, at least, the input and output files:

.. code-block:: bash

    ./tools/tokenizer.py \\
    --file data/sample.json \\
    --output data/tokenized.json

By default, there will be one output line for each input line.
This is not the case in only one scenario: when you pass on the ``--remove-retweets`` parameter, which skips retweets.

In addition to the basic functionality, this tool lets you specify how to pre-process tokens.
The functions include common approaches, like stemming, as well as character normalization, which removes repeated characters:

.. code-block:: bash

    ./tools/idf.py \\
    --file data/sample.json \\
    --output data/tokenized.json \\
    --remove-unicode-entities \\
    --normalize-words --stem

In addition to the tokens, you can specify tweet attributes to keep alongside the tokenized tweets.
The output always contains the ID and used text at least, but you can store more attributes as follows:

.. code-block:: bash

    ./tools/idf.py \\
    --file data/sample.json \\
    --output data/tokenized.json \\
    --keep timestamp_ms lang created_at

Finally, the tokenizer provides functionality to keep only a subset of the tokens.
You can provide which parts-of-speech to retain by using  the `--nouns`, `--proper-nouns`, `--verbs` and `--adjectives` arguments.
If none are given, all tokens are collected, including other parts-of-speech, like adverbs.
You can specify multiple parts-of-speech at a time:

.. code-block:: bash

    ./tools/idf.py \\
    --file data/sample.json \\
    --output data/tokenized.json \\
    --stem --nouns --verbs --adjectives

The full list of accepted arguments:

    - ``-f --file``                          *<Required>* The file to use to construct the tokenized corpus.
    - ``-o --output``                        *<Required>* The file where to save the tokenized corpus.
    - ``-k --keep``                          *<Optional>* The tweet attributes to store.
    - ``--remove-retweets``                  *<Optional>* Exclude retweets from the corpus.
    - ``--remove-unicode-entities``          *<Optional>* Remove unicode entities from the tweets.
    - ``--normalize-words``                  *<Optional>* Normalize words with repeating characters in them.
    - ``--character-normalization-count``    *<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
    - ``--remove-stopwords``                 *<Optional>* Remove stopwords from the tokens.
    - ``--stem``                             *<Optional>* Stem the tokens when constructing the tokenized corpus.
    - ``--nouns``                            *<Optional>* Extract nouns from the corpus.
    - ``--proper-nouns``                     *<Optional>* Extract proper nouns from the corpus.
    - ``--verbs``                            *<Optional>* Extract verbs from the corpus.
    - ``--adjectives``                       *<Optional>* Extract adjectives from the corpus.

The output is a JSON file where each line is a JSON-encoded tweet:

.. code-block:: json

    { "id": 1276194677906190336, "text": "Do you know how mentally strong you have to be as an Arsenal fan to carry on watching", "tokens": ["know", "mental", "strong", "arsen", "fan", "carri", "watch"], "timestamp_ms": "1593103496420"}
"""

import argparse
import json
import os
import sys

from nltk.corpus import stopwords

path = os.path.join(os.path.dirname(__file__), '..', 'eventdt')
if path not in sys.path:
    sys.path.append(path)

from nlp.tokenizer import Tokenizer
import twitter

def setup_args():
    """
    Set up and get the list of command-line arguments.

    Accepted arguments:

        - ``-f --file``                          *<Required>* The file to use to construct the tokenized corpus.
        - ``-o --output``                        *<Required>* The file where to save the tokenized corpus.
        - ``-k --keep``                          *<Optional>* The tweet attributes to store.
        - ``--remove-retweets``                  *<Optional>* Exclude retweets from the corpus.
        - ``--remove-unicode-entities``          *<Optional>* Remove unicode entities from the tweets.
        - ``--normalize-words``                  *<Optional>* Normalize words with repeating characters in them.
        - ``--character-normalization-count``    *<Optional>* The number of times a character must repeat for it to be normalized. Used only with the ``--normalize-words`` flag.
        - ``--remove-stopwords``                 *<Optional>* Remove stopwords from the tokens.
        - ``--stem``                             *<Optional>* Stem the tokens when constructing the tokenized corpus.
        - ``--nouns``                            *<Optional>* Extract nouns from the corpus.
        - ``--proper-nouns``                     *<Optional>* Extract proper nouns from the corpus.
        - ``--verbs``                            *<Optional>* Extract verbs from the corpus.
        - ``--adjectives``                       *<Optional>* Extract adjectives from the corpus.

    :return: The command-line arguments.
    :rtype: :class:`argparse.Namespace`
    """

    parser = argparse.ArgumentParser(description="Tokenize a corpus of tweets.")

    """
    Parameters that define how the corpus should be collected.
    """

    parser.add_argument('-f', '--file', type=str, required=True,
                        help='<Required> The file to use to construct the tokenized corpus.')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='<Required> The file where to save the tokenized corpus.')
    parser.add_argument('-k', '--keep', type=str, nargs='+', required=False,
                        help='<Optional> The tweet attributes to store.')
    parser.add_argument('--remove-retweets', action="store_true",
                        help='<Optional> Exclude retweets from the corpus.')
    parser.add_argument('--remove-unicode-entities', action="store_true",
                        help='<Optional> Remove unicode entities from the tweets.')
    parser.add_argument('--remove-stopwords', action="store_true",
                        help='<Optional> Remove stopwords from the tokens.')
    parser.add_argument('--normalize-words', action="store_true",
                        help='<Optional> Normalize words with repeating characters in them.')
    parser.add_argument('--character-normalization-count', type=int, required=False, default=3,
                        help='<Optional> The number of times a character must repeat for it to be normalized. Used only with the --normalize-words flag.')
    parser.add_argument('--stem', action="store_true",
                        help='<Optional> Stem the tokens when constructing the tokenized corpus.')
    parser.add_argument('--nouns', action="store_true",
                        help='<Optional> Extract nouns from the corpus.')
    parser.add_argument('--proper-nouns', action="store_true",
                        help='<Optional> Extract proper nouns from the corpus.')
    parser.add_argument('--verbs', action="store_true",
                        help='<Optional> Extract verbs from the corpus.')
    parser.add_argument('--adjectives', action="store_true",
                        help='<Optional> Extract adjectives from the corpus.')

    args = parser.parse_args()
    return args

def main():
    """
    Main program loop.
    """

    """
    Set up the arguments, create the tokenizer and prepare the data directory.
    """
    args = setup_args()
    prepare_output(args.output)
    tags = get_tags(nouns=args.nouns, proper_nouns=args.proper_nouns,
                    verbs=args.verbs, adjectives=args.adjectives)
    tokenizer = Tokenizer(normalize_words=args.normalize_words, pos=tags,
                          character_normalization_count=args.character_normalization_count,
                          remove_unicode_entities=args.remove_unicode_entities, stem=args.stem,
                          stopwords=({ } if not args.remove_stopwords else stopwords.words('english')))
    tokenize_corpus(args.file, args.output, tokenizer, args.keep, args.remove_retweets)

def prepare_output(output):
    """
    Create the data directory if it does not exist.

    :param output: The output path.
    :type output: str
    """

    dir = os.path.dirname(output)
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_tags(nouns, proper_nouns, verbs, adjectives):
    """
    Get the parts-of-speech tags based on the command-line arguments.
    If neither of the tags are given, `None` is returned.

    :param nouns: A boolean indicating whether to extract nouns.
    :type nouns: bool
    :param proper_nouns: A boolean indicating whether to extract proper nouns.
    :type proper_nouns: bool
    :param verbs: A boolean indicating whether to extract verbs.
    :type verbs: bool
    :param adjectives: A boolean indicating whether to extract adjectives.
    :type adjectives: bool

    :return: A list of parts-of-speech tags corresponding to the given flags, or `None` if all tags should be collected.
    :rtype: None or list of str
    """

    """
    If no command-line arguments for parts-of-speech tags are given, collect all tags.
    This happens by returning `None`.
    """
    if not any([ nouns, proper_nouns, verbs, adjectives ]):
        return None

    map = {
        'nouns': [ 'NN', 'NNS' ],
        'proper_nouns': [ 'NNP', 'NNPS' ],
        'verbs': [ 'VB', 'VBG', 'VBD', 'VBN', 'VBP', 'VBZ' ],
        'adjectives': [ 'JJ', 'JJR', 'JJS' ]
    }

    tags = [ ]
    if nouns:
        tags.extend(map['nouns'])

    if proper_nouns:
        tags.extend(map['proper_nouns'])

    if verbs:
        tags.extend(map['verbs'])

    if adjectives:
        tags.extend(map['adjectives'])

    return tags

def tokenize_corpus(file, output, tokenizer, keep=None, remove_retweets=False):
    """
    Tokenize the corpus represented by the given file.
    The function iterates over each tweet, tokenizes it and saves it to the file.

    :param file: The path to the corpus file.
    :type file: str
    :param output: The output path.
                   This function assumes that the directory path exists.
    :type output: str
    :param tokenizer: The tokenizer to use to create the tokenized corpus.
    :type tokenizer: :class:`~nlp.tokenizer.Tokenizer`
    :param keep: The list of tweet attributes to store for each tweet.
                 By default, the tweet ID is always kept.
    :type keep: list or None
    :param remove_retweets: A boolean indicating whether to xclude retweets from the corpus.
    :type remove_retweets: bool
    """

    keep = keep or [ ]

    with open(file, 'r') as infile, \
          open(output, 'w') as outfile:
        for line in infile:
            tweet = json.loads(line)

            """
            Skip the tweet if retweets should be excluded.
            """
            if remove_retweets and 'retweeted_status' in tweet:
                continue

            text = twitter.full_text(tweet)
            tokens = tokenizer.tokenize(text)

            """
            By default, each tweet object stores:

            - The tweet ID,
            - The text used to extract tokens, and
            - The tokens themselves.
            """
            object = { 'id': tweet['id'], 'text': tweet['text'],
                       'tokens': tokens }

            """
            Other attributes can be specified as arguments.
            """
            for attribute in keep:
                object[attribute] = tweet.get(attribute)

            outfile.write(f"{ json.dumps(object) }\n")

if __name__ == "__main__":
    main()
