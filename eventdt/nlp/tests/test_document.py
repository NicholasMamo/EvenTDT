"""
Run unit tests on the :class:`~nlp.document.Document` class.
"""

import json
import os
import random
import sys
import time
import unittest

path = os.path.join(os.path.dirname(__file__), '..')
if path not in sys.path:
    sys.path.append(path)

from document import Document
from objects import Exportable
from tokenizer import Tokenizer
import twitter
from weighting.tf import TF

class TestDocument(unittest.TestCase):
    """
    Test the :class:`~nlp.document.Document` class.
    """

    def test_empty_document(self):
        """
        Test that the document may be created empty.
        """

        d = Document()
        self.assertEqual('', d.text)
        self.assertEqual({ }, d.dimensions)

    def test_document_constructor(self):
        """
        Test creating a document with text and dimensions.
        """

        d = Document('text', { 'text': 1 })
        self.assertEqual('text', d.text)
        self.assertEqual({ 'text': 1 }, d.dimensions)

    def test_document_attributes(self):
        """
        Test creating a document with text, dimensions, and attributes.
        """

        d = Document('text', { 'text': 1 }, attributes={ 'label': True })
        self.assertEqual('text', d.text)
        self.assertEqual({ 'text': 1 }, d.dimensions)
        self.assertTrue(d.attributes['label'])

    def test_create_document_with_tokens(self):
        """
        Test creating a document with tokens and a term-weighting scheme.
        """

        text = 'this is not a pipe'
        d = Document(text, text.split(), scheme=TF())
        self.assertEqual({ 'this': 1, 'is': 1, 'not': 1, 'a': 1, 'pipe': 1 }, d.dimensions)

    def test_export(self):
        """
        Test exporting and importing documents.
        """

        text = 'this is not a pipe'
        d = Document(text, text.split(), attributes={ 'timestamp': 10 })
        e = d.to_array()
        self.assertEqual(d.dimensions, Document.from_array(e).dimensions)
        self.assertEqual(d.text, Document.from_array(e).text)
        self.assertEqual(d.__dict__, Document.from_array(e).__dict__)

    def test_export_attributes(self):
        """
        Test that exporting and importing documents include their attributes.
        """

        text = 'this is not a pipe'
        d = Document(text, text.split(), attributes={ 'timestamp': 10 })
        e = d.to_array()
        self.assertEqual(d.attributes, Document.from_array(e).attributes)
        self.assertEqual(d.attributes['timestamp'], Document.from_array(e).attributes['timestamp'])

    def test_concatenate(self):
        """
        Test that when documents are concatenated, all documents are part of the new document.
        """

        """
        Create the test data.
        """
        strings = [
            'this is not a pipe',
            'this is just a cigarette',
            'still just as deadly'
        ]

        tokenizer = Tokenizer(stem=False)
        documents = [
            Document(string, tokenizer.tokenize(string), scheme=TF()) for string in strings
        ]

        document = Document.concatenate(*documents, tokenizer=tokenizer, scheme=TF())
        self.assertEqual(2, document.dimensions.get('this'))
        self.assertEqual(2, document.dimensions.get('just'))
        self.assertEqual(1, document.dimensions.get('pipe'))
        self.assertEqual(1, document.dimensions.get('cigarette'))
        self.assertEqual(1, document.dimensions.get('deadly'))
        self.assertEqual(' '.join(strings), document.text)

    def test_concatenate_zero_documents(self):
        """
        Test that when no documents are given to be concatenated, an empty document is created.
        """

        tokenizer = Tokenizer(stem=False)
        documents = [ ]

        document = Document.concatenate(*documents, tokenizer=tokenizer, scheme=TF())
        self.assertFalse(document.dimensions)
        self.assertEqual('', document.text)

    def test_concatenate_with_attributes(self):
        """
        Test that when attributes are given to the concatentation, they are included in the new document.
        """

        """
        Create the test data.
        """
        strings = [
            'this is not a pipe',
            'this is just a cigarette',
            'still just as deadly'
        ]

        tokenizer = Tokenizer(stem=False)
        documents = [
            Document(string, tokenizer.tokenize(string), scheme=TF()) for string in strings
        ]

        document = Document.concatenate(*documents, tokenizer=tokenizer, scheme=TF(),
                                        attributes={ 'attr': True })
        self.assertTrue(document.attributes['attr'])

    def test_str(self):
        """
        Test that the string representation of the document is equivalent to its text.
        """

        document = Document('this is not a pipe')
        self.assertEqual('this is not a pipe', str(document))

    def test_from_dict_full_text(self):
        """
        Test that creating a tweet from a dictionary uses the full text.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.expand_mentions(twitter.full_text(tweet), tweet), document.text)

    def test_from_dict_expanded_mentions(self):
        """
        Test that creating a tweet from a dictionary expands mentions.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.expand_mentions(twitter.full_text(tweet), tweet), document.text)

    def test_from_dict_no_dimensions(self):
        """
        Test that creating a tweet from a dictionary without dimensions instantiates a document without dimensions.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual({ }, document.dimensions)

    def test_from_dict_with_dimensions(self):
        """
        Test that creating a document from a dictionary with dimensions stores the dimensions.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'idf.json'), 'r') as f:
            data = json.loads(f.readline())
            scheme = Exportable.decode(data)['tfidf']

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                text = twitter.expand_mentions(twitter.full_text(tweet), tweet)
                dimensions = scheme.create(Tokenizer(stem=True).tokenize(text), text=text).dimensions
                document = Document.from_dict(tweet, dimensions=dimensions)
                self.assertEqual(dimensions, document.dimensions)

    def test_from_dict_with_id(self):
        """
        Test that creating a document from a dictionary saves the tweet ID as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.id(tweet), document.id)

    def test_from_dict_v2_with_id(self):
        """
        Test that creating a document from a dictionary saves the tweet ID as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.id(tweet), document.id)

    def test_from_dict_with_version(self):
        """
        Test that creating a document from a dictionary saves the tweet ID as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.version(tweet), document.version)

    def test_from_dict_v2_with_version(self):
        """
        Test that creating a document from a dictionary saves the tweet ID as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.version(tweet), document.version)

    def test_from_dict_with_lang(self):
        """
        Test that creating a document from a dictionary saves the language as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.lang(tweet), document.lang)

    def test_from_dict_v2_with_lang(self):
        """
        Test that creating a document from a dictionary saves the language as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.lang(tweet), document.lang)

    def test_from_dict_with_timestamp(self):
        """
        Test that creating a document from a dictionary saves the timestamp as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.timestamp(tweet), document.timestamp)

    def test_from_dict_v2_with_timestamp(self):
        """
        Test that creating a document from a dictionary saves the timestamp as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.timestamp(tweet), document.timestamp)

    def test_from_dict_with_urls(self):
        """
        Test that creating a document from a dictionary saves the tweet's URLs as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.urls(tweet), document.urls)

    def test_from_dict_v2_with_urls(self):
        """
        Test that creating a document from a dictionary saves the tweet's URLs as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.urls(tweet), document.urls)

    def test_from_dict_with_hashtags(self):
        """
        Test that creating a document from a dictionary saves the tweet's hashtags as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.hashtags(tweet), document.hashtags)

    def test_from_dict_v2_with_hashtags(self):
        """
        Test that creating a document from a dictionary saves the tweet's hashtags as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.hashtags(tweet), document.hashtags)

    def test_from_dict_without_annotations(self):
        """
        Test that creating a document from an APIv1.1 tweet dictionary does not save the tweet's annotations as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertFalse(document.annotations)

    def test_from_dict_v2_with_annotations(self):
        """
        Test that creating a document from an APIv2 tweet dictionary saves the tweet's annotations as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.annotations(tweet), document.annotations)

    def test_from_dict_is_retweet(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is a retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.is_retweet(tweet), document.is_retweet)

    def test_from_dict_v2_is_retweet(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is a retweet.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.is_retweet(tweet), document.is_retweet)

    def test_from_dict_is_reply(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is a reply.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.is_reply(tweet), document.is_reply)

    def test_from_dict_v2_is_reply(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is a reply.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.is_reply(tweet), document.is_reply)

    def test_from_dict_is_quote(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is a quote.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.is_quote(tweet), document.is_quote)

    def test_from_dict_v2_is_quote(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is a quote.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(twitter.is_quote(tweet), document.is_quote)

    def test_from_dict_author_is_verified(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is by a verified author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                if not twitter.is_retweet(tweet):
                    self.assertEqual(twitter.is_verified(tweet), document.author_is_verified)

    def test_from_dict_v2_author_is_verified(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is by a verified author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                if not twitter.is_retweet(tweet):
                    self.assertEqual(twitter.is_verified(tweet), document.author_is_verified)

    def test_from_dict_author_is_verified_retweet(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is by a verified author.
        In the case of retweets, the author attribute should refer to the original tweet's author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.is_verified(tweet, user_id=twitter.user_id(twitter.original(tweet))), document.author_is_verified)

    def test_from_dict_v2_author_is_verified_retweet(self):
        """
        Test that creating a document from a dictionary saves a boolean indicating whether the tweet is by a verified author.
        In the case of retweets, the author attribute should refer to the original tweet's author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.is_verified(tweet, user_id=twitter.user_id(twitter.original(tweet))), document.author_is_verified)

    def test_from_dict_author_handle(self):
        """
        Test that creating a document from a dictionary saves the author's handle.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                if not twitter.is_retweet(tweet):
                    self.assertEqual(twitter.user_handle(tweet), document.author_handle)

    def test_from_dict_v2_author_handle(self):
        """
        Test that creating a document from a dictionary saves the author's handle.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                if not twitter.is_retweet(tweet):
                    self.assertEqual(twitter.user_handle(tweet), document.author_handle)

    def test_from_dict_author_handle_retweet(self):
        """
        Test that creating a document from a dictionary saves the author's handle.
        In the case of retweets, the author attribute should refer to the original tweet's author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.user_handle(tweet, user_id=twitter.user_id(twitter.original(tweet))), document.author_handle)

    def test_from_dict_v2_author_handle_retweet(self):
        """
        Test that creating a document from a dictionary saves the author's handle.
        In the case of retweets, the author attribute should refer to the original tweet's author.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                if twitter.is_retweet(tweet):
                    self.assertEqual(twitter.user_handle(tweet, user_id=twitter.user_id(twitter.original(tweet))), document.author_handle)

    def test_from_dict_with_tweet(self):
        """
        Test that creating a document from a dictionary saves the tweet as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'CRYCHE-500.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(tweet, document.tweet)

    def test_from_dict_v2_with_tweet(self):
        """
        Test that creating a document from a dictionary saves the tweet as an attribute.
        """

        with open(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'corpora', 'samplev2.json'), 'r') as f:
            for line in f:
                tweet = json.loads(line)
                document = Document.from_dict(tweet)
                self.assertEqual(tweet, document.tweet)

    def test_copy(self):
        """
        Test that when copying a document, the text, dimensions and attributes are identical.
        """

        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'timestamp': time.time() })
        copy = document.copy()
        self.assertEqual(document.text, copy.text)
        self.assertEqual(document.dimensions, copy.dimensions)
        self.assertEqual(document.attributes, copy.attributes)

    def test_copy_attributes_original(self):
        """
        Test that changing the copy's attributes does not affect the original's, and vice-versa.
        """

        now = time.time()
        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'timestamp': now })
        copy = document.copy()

        then = time.time()
        copy.attributes['timestamp'] = then
        self.assertEqual(then, copy.attributes['timestamp'])
        self.assertTrue(now, document.attributes['timestamp'])

        now = time.time()
        document.attributes['timestamp'] = now
        self.assertEqual(then, copy.attributes['timestamp'])
        self.assertEqual(now, document.attributes['timestamp'])

    def test_copy_nested_attributes_original(self):
        """
        Test that changing the copy's nested attributes does not affect the original's, and vice-versa.
        """

        now = time.time()
        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'timestamp': { 'start': now } })
        copy = document.copy()

        then = time.time()
        copy.attributes['timestamp']['start'] = then
        self.assertEqual(then, copy.attributes['timestamp']['start'])
        self.assertTrue(now, document.attributes['timestamp']['start'])

        now = time.time()
        document.attributes['timestamp']['start'] = now
        self.assertEqual(then, copy.attributes['timestamp']['start'])
        self.assertEqual(now, document.attributes['timestamp']['start'])

    def test_copy_dimensions_original(self):
        """
        Test that changing the copy's dimensions does not affect the original's, and vice-versa.
        """

        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'timestamp': time.time() })
        copy = document.copy()

        copy.dimensions['pipe'] = 2
        self.assertEqual(2, copy.dimensions['pipe'])
        self.assertEqual(1, document.dimensions['pipe'])

        document.dimensions['pipe'] = 3
        self.assertEqual(2, copy.dimensions['pipe'])
        self.assertEqual(3, document.dimensions['pipe'])

    def test_copy_text_original(self):
        """
        Test that changing the copy's text does not affect the original's, and vice-versa.
        """

        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'timestamp': time.time() })
        copy = document.copy()

        copy.text = 'this is a cigar'
        self.assertEqual('this is a cigar', copy.text)
        self.assertEqual('this is a pipe', document.text)

        document.text = 'this is nothing'
        self.assertEqual('this is a cigar', copy.text)
        self.assertEqual('this is nothing', document.text)

    def test_copy_true(self):
        """
        Test that when copying a document, changes to the copy do not affect the original.
        """

        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'original': True })
        copy = document.copy()

        self.assertEqual(document.text, copy.text)
        copy.text = 'this is a cigar'
        self.assertEqual('this is a cigar', copy.text)
        self.assertEqual('this is a pipe', document.text)

        self.assertEqual(document.dimensions, copy.dimensions)
        copy.dimensions = { 'cigar': 1 }
        self.assertEqual({ 'cigar': 1 }, copy.dimensions)
        self.assertEqual({ 'pipe': 1 }, document.dimensions)

        self.assertEqual(document.attributes, copy.attributes)
        copy.attributes = { 'original': False }
        self.assertEqual({ 'original': False }, copy.attributes)
        self.assertEqual({ 'original': True }, document.attributes)

    def test_hash_without_id(self):
        """
        Test that hashing a document without an ID returns the hash of its array representation.
        """

        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'original': True })
        self.assertEqual(hash(json.dumps(document.to_array())), hash(document))

    def test_hash_with_id(self):
        """
        Test that hashing a document with an ID returns the ID.
        """

        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'id': random.randint(0, 1e6), 'original': True })
        self.assertEqual(document.id, hash(document))

    def test_hash_with_id_returns_int(self):
        """
        Test that hashing a document with an ID returns the ID as an integer.
        """

        document = Document('this is a pipe', { 'pipe': 1 }, attributes={ 'id': str(random.randint(0, 1e6)), 'original': True })
        self.assertEqual(int, type(hash(document)))