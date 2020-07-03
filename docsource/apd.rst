****************************************
5. Automatic Participant Detection (APD)
****************************************

.. meta::
   :description: The Automatic Participant Detection (APD) library
   :keywords: Python, TDT, APD

.. automodule:: apd
   :members:
   :special-members:

Automatic Participant Detection (APD) is a six-step process:

   #. :class:`Extract <apd.extractors.extractor>` candidate participants,
   #. :class:`Score <apd.scorers.scorer>` the candidates,
   #. :class:`Filter <apd.filters.filter>` out low-scoring candidates,
   #. :class:`Resolve <apd.resolvers.resolver>` the candidates to an alternate representation (such as a Wikipedia concept) to make them participants,
   #. :class:`Extrapolate <apd.extrapolators.extrapolator>` new participants, and
   #. :class:`Post-process <apd.postprocessors.postprocessor>` the final list of participants.

The APD process revolves around a central class: the :class:`~apd.participant_detector.ParticipantDetector`.
The class constructor accepts classes representing these six steps, and calls their main functions.
All of the step implementations are separated into local (using the corpus) or external (using a different source) methods.

Each step is represented by a base class.
Base classes define the minimum inputs and describe the expected outputs of each step.
Each base class also has a central function around which processing revolves.
For example, the :class:`~apd.extractors.extractor.Extractor` class has a :func:`~apd.extractors.extractor.Extractor.extract` function.

All APD functionality usually goes through the :class:`~apd.participant_detector.ParticipantDetector`.
This class represents APD's six steps.
It takes as inputs instances of the classes and calls them one after the other.

Participant Detectors
=====================

.. automodule:: apd.participant_detector
   :members:
   :special-members:

Named Entity Recognition Participant Detector
---------------------------------------------

.. automodule:: apd.ner_participant_detector
   :members:
   :special-members:

Extractors
==========

.. automodule:: apd.extractors.extractor
   :members:
   :special-members:

Local
-----

.. automodule:: apd.extractors.local
   :members:
   :special-members:

Token Extractor
^^^^^^^^^^^^^^^

.. automodule:: apd.extractors.local.token_extractor
   :members:
   :special-members:

Entity Extractor
^^^^^^^^^^^^^^^^

.. automodule:: apd.extractors.local.entity_extractor
   :members:
   :special-members:

Scorers
=======

.. automodule:: apd.scorers.scorer
   :members:
   :special-members:

Local
-----

.. automodule:: apd.scorers.local
   :members:
   :special-members:

Document Frequency Scorer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.scorers.local.df_scorer
   :members:
   :special-members:

Logarithmic Document Frequency Scorer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.scorers.local.log_df_scorer
   :members:
   :special-members:

Term Frequency Scorer
^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.scorers.local.tf_scorer
   :members:
   :special-members:

Logarithmic Term Frequency Scorer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.scorers.local.log_tf_scorer
   :members:
   :special-members:

Term Frequency-Inverse Document Frequency Scorer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.scorers.local.tfidf_scorer
   :members:
   :special-members:

Filters
=======

.. automodule:: apd.filters.filter
   :members:
   :special-members:

Local
-----

.. automodule:: apd.filters.local
   :members:
   :special-members:

Threshold Filter
^^^^^^^^^^^^^^^^

.. automodule:: apd.filters.local.threshold_filter
   :members:
   :special-members:

Resolvers
=========

.. automodule:: apd.resolvers.resolver
   :members:
   :special-members:

Local
-----

.. automodule:: apd.resolvers.local
   :members:
   :special-members:

Token Resolver
^^^^^^^^^^^^^^

.. automodule:: apd.resolvers.local.token_resolver
   :members:
   :special-members:

External
--------

.. automodule:: apd.resolvers.external
   :members:
   :special-members:

Wikipedia Name Resolver
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.resolvers.external.wikipedia_name_resolver
   :members:
   :special-members:

Wikipedia Search Resolver
^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.resolvers.external.wikipedia_search_resolver
   :members:
   :special-members:

Extrapolators
=============

.. automodule:: apd.extrapolators.extrapolator
   :members:
   :special-members:

External
--------

.. automodule:: apd.extrapolators.external
   :members:
   :special-members:

Wikipedia Extrapolator
^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.extrapolators.external.wikipedia_extrapolator
   :members:
   :special-members:

Post-processors
===============

.. automodule:: apd.postprocessors.postprocessor
   :members:
   :special-members:

External
--------

.. automodule:: apd.postprocessors.external
   :members:
   :special-members:

Wikipedia Post-processor
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: apd.postprocessors.external.wikipedia_postprocessor
   :members:
   :special-members:
