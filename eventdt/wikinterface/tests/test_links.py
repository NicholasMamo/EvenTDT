"""
Run unit tests on the LinkCollector class
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, "../")
if path not in sys.path:
	sys.path.append(path)

from libraries.wikinterface.linkcollector import LinkCollector

class TestLinkCollector(unittest.TestCase):
	"""
	Test the LinkCollector class
	"""

	def test_links(self):
		"""
		Tests the links methods
		"""

		l = LinkCollector()
		seed = ["Olympique Lyonnais"]
		links = l.get_links(seed, separate=False)
		self.assertTrue(len(links) > 0)
		self.assertEqual(len(l.get_links(seed, separate=False, encoding="utf-8")), len(links))

		seed = ["Android (operating system)"]
		links = l.get_links(seed, separate=False, first_section_only=True)
		self.assertTrue(len(links) > 0)
		self.assertTrue(len(l.get_links(seed, separate=False, encoding="utf-8")) >= len(links))

	def test_link_encoding(self):
		"""
		Test that the encoding works
		"""

		l = LinkCollector()
		seed = ["Olympique Lyonnais"]
		# isolate the UNFP link returned by the method
		links = l.get_links(seed, separate=False, encoding="utf-8")
		filtered_list = [link for link in links if link.decode("utf-8").startswith("Trop") and link.decode("utf-8").endswith("UNFP du football")]

		seed = ["Trophées UNFP du football"]
		links = l.get_links(seed, separate=False)
		self.assertTrue(len(links) > 0)
		self.assertEqual(len(links), len(l.get_links(filtered_list, separate=False))) # check that decoding the returned value works as well

		seed = ["Olympique Lyonnais", "France"]
		links = l.get_links(seed, separate=False)
		self.assertTrue(len(links) > 0)
		self.assertEqual(len(links), len(set(l.get_links([seed[0]], separate=False) + l.get_links([seed[1]], separate=False))))
		links = l.get_links(seed, separate=True)
		self.assertEqual(len(links), 2)

	def test_recursive_links(self):
		"""
		Test that the recursive links work
		"""

		l = LinkCollector()
		seed = ["Olympique Lyonnais"]
		links = l.get_links(seed, separate=False)
		self.assertEqual(len(links), len(l.get_recursive_links(seed, 1, separate=False, encoding="utf-8", first_section_only=False)))
		self.assertEqual(len(links), len(l.get_recursive_links(seed, 1, separate=True, encoding="utf-8", first_section_only=False)["Olympique Lyonnais"]))

		links = l.get_links(seed, separate=False, first_section_only=True)
		self.assertEqual(len(links), len(l.get_recursive_links(seed, 1, separate=False, encoding="utf-8", first_section_only=True)))
		self.assertEqual(len(links), len(l.get_recursive_links(seed, 1, separate=True, encoding="utf-8", first_section_only=True)["Olympique Lyonnais"]))
