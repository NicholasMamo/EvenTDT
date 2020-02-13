****************************************
4. Automatic Participant Detection (APD)
****************************************

.. meta::
   :description: The Automatic Participant Detection (APD) library
   :keywords: Python, TDT, APD

.. automodule:: apd
   :members:
   :private-members:
   :special-members:

Automatic Participant Detection (APD) is a six-step process:

   #. Extraction
   #. Scoring
   #. Filtering
   #. Resolution
   #. Extrapolation
   #. Postprocesing

The APD process revolves around a central class: the :class:`apd.participant_detector.ParticipantDetector`.
The class constructor accepts classes representing these six steps, and calls their main functions.
All of the step implementations are separated into local (using the corpus) or external (using a different source).

Extractors
==========

.. automodule:: apd.extractors.extractor
   :members:
   :private-members:
   :special-members:

Local
-----

.. automodule:: apd.extractors.local.token_extractor
   :members:
   :private-members:
   :special-members:

.. automodule:: apd.extractors.local.entity_extractor
   :members:
   :private-members:
   :special-members:

Scorers
=======

.. automodule:: apd.scorers.scorer
   :members:
   :private-members:
   :special-members:

Local
-----

.. automodule:: apd.scorers.local.df_scorer
   :members:
   :private-members:
   :special-members:

.. automodule:: apd.scorers.local.log_df_scorer
   :members:
   :private-members:
   :special-members:

.. automodule:: apd.scorers.local.tf_scorer
   :members:
   :private-members:
   :special-members:

.. automodule:: apd.scorers.local.log_tf_scorer
   :members:
   :private-members:
   :special-members:

.. automodule:: apd.scorers.local.tfidf_scorer
   :members:
   :private-members:
   :special-members:

Filters
=======

.. automodule:: apd.filters.filter
   :members:
   :private-members:
   :special-members:

Local
-----

.. automodule:: apd.filters.local.threshold_filter
   :members:
   :private-members:
   :special-members:

Resolvers
=========

.. automodule:: apd.resolvers.resolver
   :members:
   :private-members:
   :special-members:
