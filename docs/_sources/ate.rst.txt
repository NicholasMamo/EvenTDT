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
   :private-members:
   :special-members:

Extractor
=========

.. automodule:: ate.extractor
   :members:
   :private-members:
   :special-members:

Linguistic
==========

.. automodule:: ate.linguistic
   :members:
   :private-members:
   :special-members:

Statistical
===========

.. automodule:: ate.stat
   :members:
   :private-members:
   :special-members:

Algorithms
----------

Term Frequency
^^^^^^^^^^^^^^

.. automodule:: ate.stat.tf
   :members:
   :private-members:
   :special-members:

Term Frequency-Inverse Document Frequency
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: ate.stat.tfidf
   :members:
   :private-members:
   :special-members:

Probability
-----------

.. automodule:: ate.stat.probability
   :members:
   :private-members:
   :special-members:

Corpus Comparison
-----------------

.. automodule:: ate.stat.corpus
   :members:
   :private-members:
   :special-members:

TF-DCF
^^^^^^

.. automodule:: ate.stat.corpus.tfdcf
   :members:
   :private-members:
   :special-members:

Application
===========

.. automodule:: ate.application
   :members:
   :private-members:
   :special-members:

Events
------

.. automodule:: ate.application.event

Event Frequency (EF)
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ate.application.event.EF
   :members:
   :private-members:
   :special-members:

Logarithmic Event Frequency (EF)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ate.application.event.LogEF
   :members:
   :private-members:
   :special-members:

Event Frequency-Inverse Document Frequency (EF-IDF)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: ate.application.event.EFIDF
   :members:
   :private-members:
   :special-members:

Variability
^^^^^^^^^^^

.. autoclass:: ate.application.event.Variability
   :members:
   :private-members:
   :special-members:

Bootstrapping
=============

.. automodule:: ate.bootstrapping
   :members:
   :private-members:
   :special-members:

Probability
-----------

.. automodule:: ate.bootstrapping.probability
   :members:
   :private-members:
   :special-members:

Pointwise Mutual Information (PMI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: ate.bootstrapping.probability.pmi
   :members:
   :private-members:
   :special-members:

Chi-Square
^^^^^^^^^^

.. automodule:: ate.bootstrapping.probability.chi
   :members:
   :private-members:
   :special-members:
