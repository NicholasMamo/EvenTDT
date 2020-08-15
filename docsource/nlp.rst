************************************
3. Natural Language Processing (NLP)
************************************

.. meta::
   :description: The Natural Language Processing (NLP) library
   :keywords: Python, TDT, NLP

.. _nlp:

.. automodule:: nlp
   :members:
   :special-members:

=========
Documents
=========

.. automodule:: nlp.document
   :members:
   :special-members:

============
Tokenization
============

.. automodule:: nlp.tokenizer
   :members:
   :special-members:

==============
Term-Weighting
==============

.. automodule:: nlp.weighting
   :members:
   :special-members:

.. automodule:: nlp.weighting.scheme
   :members:
   :special-members:

Common Term-Weighting Schemes
-----------------------------

.. automodule:: nlp.weighting.tf
   :members:
   :special-members:

.. automodule:: nlp.weighting.tfidf
   :members:
   :special-members:

Local Term-Weighting Schemes
----------------------------

.. automodule:: nlp.weighting.local_schemes.boolean
   :members:
   :special-members:

.. automodule:: nlp.weighting.local_schemes.tf
   :members:
   :special-members:

Global Term-Weighting Schemes
-----------------------------

.. automodule:: nlp.weighting.global_schemes.filler
   :members:
   :special-members:

.. automodule:: nlp.weighting.global_schemes.idf
   :members:
   :special-members:

========
Cleaners
========

EvenTDT comes with classes to clean documents.
These can be used, for example, to clean summaries.

.. automodule:: nlp.cleaners.cleaner
   :members:
   :special-members:

.. automodule:: nlp.cleaners.tweet_cleaner
   :members:
   :special-members:
