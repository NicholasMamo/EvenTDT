****************************************
4. Automatic Participant Detection (APD)
****************************************

.. meta::
   :description: The Automatic Participant Detection (APD) library
   :keywords: Python, TDT, APD

.. automodule:: eventdt.apd
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

The APD process revolves around a central class: the :class:`eventdt.apd.participant_detector.ParticipantDetector`.
The class constructor accepts classes representing these six steps, and calls their main functions.
