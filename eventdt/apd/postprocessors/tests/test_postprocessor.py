"""
Test the functionality of the base postprocessor.
"""

import copy
import os
import sys
import unittest
import warnings

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from apd.postprocessors.postprocessor import Postprocessor

class TestPostprocessor(unittest.TestCase):
    """
    Test the implementation and results of the Postprocessor.
    """

    def test_postprocess_returns_dict(self):
        """
        Test that post-processing returns a dictionary.
        """

        participants = [ 'Eden Hazard', 'Chelsea F.C.', 'Maurizio Sarri' ]
        postprocessor = Postprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(dict, type(postprocessed))

    def test_postprocess_all_participants(self):
        """
        Test that the post-processor returns all participants.
        """

        participants = [ 'Eden Hazard', 'Chelsea F.C.', 'Maurizio Sarri' ]
        postprocessor = Postprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertTrue(all( participant in postprocessed for participant in participants ))

    def test_postprocess_no_duplicates(self):
        """
        Test that the post-processor returns no duplicates.
        """

        participants = [ 'Eden Hazard', 'Chelsea F.C.', 'Maurizio Sarri' ]
        postprocessor = Postprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(len(postprocessed), len(set(participants)))
        self.assertEqual(sorted(set(postprocessed)), sorted(participants))

    def test_postprocess_same_order(self):
        """
        Test that the post-processor returns the participants in teh same order.
        """

        participants = [ 'Eden Hazard', 'Chelsea F.C.', 'Maurizio Sarri' ]
        postprocessor = Postprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertEqual(participants, list(postprocessed))

    def test_postprocess_no_chage(self):
        """
        Test that the basic post-processor does not change the participants.
        """

        participants = [ 'Eden Hazard', 'Chelsea F.C.', 'Maurizio Sarri' ]
        postprocessor = Postprocessor()
        postprocessed = postprocessor.postprocess(participants)
        self.assertTrue(all( participant == _postprocessed
                             for participant, _postprocessed in postprocessed.items() ))
