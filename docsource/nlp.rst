************************************
3. Natural Language Processing (NLP)
************************************

.. meta::
   :description: The Natural Language Processing (NLP) library
   :keywords: Python, TDT, NLP

Documents find their basis in the Vector Space Model (VSM).
For this reason, EvenTDT's documents are based on the :class:`eventdt.vsm.vector.Vector` class.
EvenTDT adds functionality to make it easier to work with documents, including by storing the original text.
Keep reading to learn more about the different NLP classes available in EvenTDT.

.. automodule:: eventdt.nlp
   :members:
   :private-members:
   :special-members:

=========
Documents
=========

.. automodule:: eventdt.nlp.document
   :members:
   :private-members:
   :special-members:

==============
Term-Weighting
==============

.. automodule:: eventdt.nlp.term_weighting
   :members:
   :private-members:
   :special-members:

.. automodule:: eventdt.nlp.term_weighting.scheme
   :members:
   :private-members:
   :special-members:

Common Term-Weighting Schemes
-----------------------------

.. automodule:: eventdt.nlp.term_weighting.tf
   :members:
   :private-members:
   :special-members:

.. automodule:: eventdt.nlp.term_weighting.tfidf
   :members:
   :private-members:
   :special-members:

Local Term-Weighting Schemes
----------------------------

.. automodule:: eventdt.nlp.term_weighting.local_schemes.boolean
   :members:
   :private-members:
   :special-members:

.. automodule:: eventdt.nlp.term_weighting.local_schemes.tf
   :members:
   :private-members:
   :special-members:

Global Term-Weighting Schemes
-----------------------------

.. automodule:: eventdt.nlp.term_weighting.global_schemes.filler
   :members:
   :private-members:
   :special-members:

.. automodule:: eventdt.nlp.term_weighting.global_schemes.idf
   :members:
   :private-members:
   :special-members:
