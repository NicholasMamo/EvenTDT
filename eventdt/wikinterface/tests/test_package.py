"""
Run unit tests on the wikinterface package.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from wikinterface import *

class TestWikinterface(unittest.TestCase):
    """
    Test the wikinterface package.
    """

    def test_revert_redirects(self):
        """
        Test that when reverting redirections, the redirected page is not included.
        """

        """
        Create the test data.
        """
        redirects = [
            { 'from': 'Striker (association football)' , 'to': 'Forward (association football)' },
            { 'from': 'Inside forward' , 'to': 'Forward (association football)' },
        ]
        results = {
            'Forward (association football)': ''
        }

        """
        Revert the redirections.
        """

        pages = revert_redirects(results, redirects, with_redirects=False)
        self.assertTrue('Inside forward' in pages)
        self.assertTrue('Striker (association football)' in pages)
        self.assertFalse('Forward (association football)' in pages)

    def test_revert_redirects_multiple(self):
        """
        Test that when reverting multiple redirections, the original source is returned.
        """

        """
        Create the test data.
        """
        redirects = [
            {'from': 'Transgender rights', 'to': 'Legal status of transgender people'},
            {'from': 'Legal status of transgender people', 'to': 'Legal rights of trans people'}
        ]
        results = {
            'Legal rights of trans people': ''
        }

        """
        Revert the redirections.
        """

        pages = revert_redirects(results, redirects, with_redirects=False)
        self.assertTrue('Transgender rights' in pages)

    def test_revert_redirects_with_keep(self):
        """
        Test that when reverting redirections and keeping those redirections, the redirections are retained.
        """

        """
        Create the test data.
        """
        redirects = [
            { 'from': 'Education in Alaska' , 'to': 'Alaska' },
        ]
        results = {
            'Alaska': ''
        }

        """
        Revert the redirections.
        """

        pages = revert_redirects(results, redirects, with_redirects=True)
        self.assertTrue('Alaska' in pages)
        self.assertTrue('Education in Alaska' in pages)

    def test_construct_url_without_parameters(self):
        """
        Test that when constructing a URL without parameters, the original endpoint is returned instead.
        """

        self.assertEqual(API_ENDPOINT, construct_url())

    def test_construct_url_with_parameters(self):
        """
        Test that when constructing a URL with parameters, they are added at the end of the string.
        """

        parameters = {
            'format': 'json',
            'action': 'query',
        }

        self.assertEqual(API_ENDPOINT + "format=json&action=query", construct_url(parameters))

    def test_construct_url_with_boolean_parameters(self):
        """
        Test that when constructing a URL with boolean parameters, they are added without a value.
        """

        parameters = {
            'format': 'json',
            'action': 'query',
            'exintro': True,
        }

        self.assertEqual(API_ENDPOINT + "format=json&action=query&exintro", construct_url(parameters))

    def test_construct_url_with_false_boolean_parameters(self):
        """
        Test that when constructing a URL with `False` boolean parameters, they are excluded.
        """

        parameters = {
            'format': 'json',
            'action': 'query',
            'exintro': False,
        }

        self.assertEqual(API_ENDPOINT + "format=json&action=query", construct_url(parameters))

    def test_construct_url_with_zero_parameter(self):
        """
        Test that when constructing a URL with a parameter that has a value of zero, it is added.
        """

        parameters = {
            'format': 'json',
            'action': 'query',
            'limit': 0,
        }

        self.assertEqual(API_ENDPOINT + "format=json&action=query&limit=0", construct_url(parameters))

    def test_construct_url_with_null_parameter(self):
        """
        Test that when constructing a URL with a parameter that has a value of ``None``, it is excluded.
        """

        parameters = {
            'format': 'json',
            'action': 'query',
            'excontinue': None,
        }

        self.assertEqual(API_ENDPOINT + "format=json&action=query", construct_url(parameters))
