************************************
3. Natural Language Processing (NLP)
************************************

.. meta::
   :description: The Natural Language Processing (NLP) library
   :keywords: Python, TDT, NLP

.. _nlp:

Documents find their basis in the Vector Space Model (VSM).
For this reason, EvenTDT's documents are based on the :class:`~eventdt.vsm.vector.Vector` class.
EvenTDT adds functionality to make it easier to work with documents, including by storing the original text.
Keep reading to learn more about the different NLP classes available in EvenTDT.

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

.. automodule:: nlp.term_weighting
   :members:
   :special-members:

.. automodule:: nlp.term_weighting.scheme
   :members:
   :special-members:

Common Term-Weighting Schemes
-----------------------------

.. automodule:: nlp.term_weighting.tf
   :members:
   :special-members:

.. automodule:: nlp.term_weighting.tfidf
   :members:
   :special-members:

Local Term-Weighting Schemes
----------------------------

.. automodule:: nlp.term_weighting.local_schemes.boolean
   :members:
   :special-members:

.. automodule:: nlp.term_weighting.local_schemes.tf
   :members:
   :special-members:

Global Term-Weighting Schemes
-----------------------------

.. automodule:: nlp.term_weighting.global_schemes.filler
   :members:
   :special-members:

.. automodule:: nlp.term_weighting.global_schemes.idf
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
