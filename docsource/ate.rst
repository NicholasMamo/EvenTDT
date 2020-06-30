***********************************
11. Automatic Term Extraction (ATE)
***********************************

.. meta::
   :description: The Automatic Term Extraction (ATE) library
   :keywords: Python, TDT, ATE

Automatic Term Extraction (ATE) is a research that automatically extracts domain-specific terms.
The package includes algorithms that extract terms and bootstrap terms from a seed set.
These algorithms are both those that are popular as baselines and peer-reviewed algorithms.
Included are general functions that are likely to be useful for all algorithms.

.. automodule:: ate
   :members:
   :special-members:

The Basic Extractor
===================

.. automodule:: ate.extractor
   :members:
   :special-members:

Linguistic
==========

.. automodule:: ate.linguistic
   :members:
   :special-members:

Statistical
===========

.. automodule:: ate.stat
   :members:
   :special-members:

Algorithms
----------

Term Frequency
^^^^^^^^^^^^^^

.. automodule:: ate.stat.tf
   :members:
   :special-members:

Term Frequency-Inverse Document Frequency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: ate.stat.tfidf
   :members:
   :special-members:

Probability
-----------

.. automodule:: ate.stat.probability
   :members:
   :special-members:

Corpus Comparison
-----------------

.. automodule:: ate.stat.corpus
   :members:
   :special-members:

Domain Specificity
^^^^^^^^^^^^^^^^^^

.. automodule:: ate.stat.corpus.specificity
   :members:
   :special-members:

Rank Difference
^^^^^^^^^^^^^^^

.. automodule:: ate.stat.corpus.rank
   :members:
   :special-members:

Term Frequency-Disjoint Corpora Frequency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: ate.stat.corpus.tfdcf
   :members:
   :special-members:

Application
===========

.. automodule:: ate.application
   :members:
   :special-members:

Events
------

.. automodule:: ate.application.event

Event Frequency (EF)
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ate.application.event.EF
   :members:
   :special-members:

Logarithmic Event Frequency (EF)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ate.application.event.LogEF
   :members:
   :special-members:

Event Frequency-Inverse Document Frequency (EF-IDF)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ate.application.event.EFIDF
   :members:
   :special-members:

Variability
^^^^^^^^^^^

.. autoclass:: ate.application.event.Variability
   :members:
   :special-members:

Bootstrapping
=============

.. automodule:: ate.bootstrapping
   :members:
   :special-members:

Probability
-----------

.. automodule:: ate.bootstrapping.probability
   :members:
   :special-members:

Pointwise Mutual Information (PMI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: ate.bootstrapping.probability.pmi
   :members:
   :special-members:

Chi-Square
^^^^^^^^^^

.. automodule:: ate.bootstrapping.probability.chi
   :members:
   :special-members:
