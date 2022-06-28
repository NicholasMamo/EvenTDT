"""
Test the functionality of the package functions.
"""

import json
import os
import sys
import unittest

from datetime import datetime

paths = [ os.path.join(os.path.dirname(__file__), '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

import tools

class TestPackage(unittest.TestCase):
    """
    Test the functionality of the package functions.
    """

    def test_is_json_json_file(self):
        """
        Test that when given a JSON file path, it is recognized as a JSON file.
        """

        self.assertTrue(tools.is_json('/path/to/file.json'))

    def test_is_json_text_file(self):
        """
        Test that when given a text file path, it is not recognized as a JSON file.
        """

        self.assertFalse(tools.is_json('/path/to/file.txt'))

    def test_is_file_string(self):
        """
        Test that when given a string, it is not recognized as a file path.
        """

        self.assertFalse(tools.is_file('a string'))

    def test_is_file_path(self):
        """
        Test that when given a file path, it is recognized as a file path.
        """

        self.assertTrue(tools.is_file('file.txt'))
        self.assertTrue(tools.is_file('file.json'))

    def test_is_file_path_with_slashes(self):
        """
        Test that when given a file path with slashes, it is recognized as a file path.
        """

        self.assertTrue(tools.is_file('data/file.txt'))

    def test_is_file_path_with_multiple_extensions(self):
        """
        Test that when given a file path with multiple extensions, it is recognized as a file path.
        """

        self.assertTrue(tools.is_file('data/file.tar.gz'))

    def test_meta_file_empty_string(self):
        """
        Test that getting the meta filename of an empty string returns an empty `.meta.` file.
        Most importantly, it shouldn't crash.
        """

        self.assertEqual('.meta', tools.meta_file(''))

    def test_meta_file_no_path(self):
        """
        Test that getting the meta filename of a string with no path simply returns a new filename.
        """

        self.assertEqual('event.meta.json', tools.meta_file('event.json'))

    def test_meta_file_with_path(self):
        """
        Test that getting the meta filename of a string with a path keeps the path.
        """

        self.assertEqual('/path/to/event.meta.json', tools.meta_file('/path/to/event.json'))

    def test_meta_file_with_extension(self):
        """
        Test that getting the meta filename of a string retains the original extension.
        """

        self.assertEqual('/path/to/event.meta.txt', tools.meta_file('/path/to/event.txt'))

    def test_remove_prefix_empty(self):
        """
        Test that if the prefix is empty, the kwargs are unchanged.
        """

        kwargs = { 'filter_threshold': 0.5, 'resolver_threshold': 0.2 }
        _kwargs = tools.remove_prefix('', **kwargs)
        self.assertEqual(kwargs, _kwargs)

    def test_remove_prefix_returns_dict(self):
        """
        Test that removing the prefix returns another dictionary.
        """

        kwargs = { 'filter_threshold': 0.5, 'resolver_threshold': 0.2 }
        _kwargs = tools.remove_prefix('', **kwargs)
        self.assertEqual(dict, type(_kwargs))

    def test_remove_prefix_returns_all(self):
        """
        Test that removing the prefix does not change the kwargs size.
        """

        kwargs = { 'filter_threshold': 0.5, 'resolver_threshold': 0.2 }
        _kwargs = tools.remove_prefix('', **kwargs)
        self.assertEqual(len(kwargs), len(_kwargs))

    def test_remove_prefix_original_unchanged(self):
        """
        Test that removing the prefix does not change the original dictionary.
        """

        kwargs = { 'filter_threshold': 0.5, 'resolver_threshold': 0.2 }
        original = dict(kwargs)
        _kwargs = tools.remove_prefix('', **kwargs)
        self.assertEqual(original, kwargs)

    def test_remove_prefix_behaviour(self):
        """
        Test that removing the prefix works correctly.
        """

        kwargs = { 'filter_threshold': 0.5, 'resolver_threshold': 0.2 }
        _kwargs = tools.remove_prefix('filter_', **kwargs)
        self.assertEqual({ 'threshold': 0.5, 'resolver_threshold': 0.2 }, _kwargs)

        _kwargs = tools.remove_prefix('resolver_', **kwargs)
        self.assertEqual({ 'filter_threshold': 0.5, 'threshold': 0.2 }, _kwargs)

    def test_remove_prefix_from_start_only(self):
        """
        Test that the prefix is only removed from the start of the keyword arguments.
        """

        kwargs = { 'filter_threshold': 0.5, 'resolver_threshold': 0.2 }
        _kwargs = tools.remove_prefix('threshold', **kwargs)
        self.assertEqual(kwargs, _kwargs)

    def test_remove_prefix_same_values(self):
        """
        Test that the values do not change when removing the prefix.
        """

        kwargs = { 'filter_threshold': 0.5, 'resolver_threshold': 0.2 }
        _kwargs = tools.remove_prefix('filter_', **kwargs)
        self.assertEqual(list(kwargs.values()), list(_kwargs.values()))
