"""
Run unit tests on the link collector module.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from wikinterface import links

class TestLink(unittest.TestCase):
	"""
	Test the link module.
	"""

	def test_get_no_links(self):
		"""
		Test that when no links are requested, nothing is returned.
		"""

		self.assertEqual({ }, links.collect([ ]))
		self.assertEqual([ ], links.collect([ ], separate=False))

	def test_get_separated_links(self):
		"""
		Test that when the links are requested to be separated, a dictionary is returned.
		"""

		page = 'Olympique Lyonnais'
		articles = links.collect(page, separate=True)
		self.assertEqual(dict, type(articles))
		self.assertTrue(page in articles)
		self.assertTrue('Fernando Marçal' in articles.get(page))
		self.assertTrue('AS Saint-Étienne' in articles.get(page))

	def test_get_separated_links_multiple_pages(self):
		"""
		Test that when the links from multiple pages are requested to be separated, a dictionary with multiple keys is returned.
		"""

		pages = [ 'Olympique Lyonnais', 'Michelangelo' ]
		articles = links.collect(pages, separate=True)
		self.assertEqual(dict, type(articles))
		self.assertEqual(set(pages), set(articles.keys()))
		self.assertTrue('Olympique Lyonnais' in articles)
		self.assertTrue('Michelangelo' in articles)

	def test_get_unseparated_links(self):
		"""
		Test that when the links are requested to be unseparated, a list is returned.
		"""

		page = 'Olympique Lyonnais'
		articles = links.collect(page, separate=False)
		self.assertEqual(list, type(articles))
		self.assertTrue('Fernando Marçal' in articles)
		self.assertTrue('AS Saint-Étienne' in articles)

	def test_get_links_multiple_pages(self):
		"""
		Test that when links are requested from multiple pages, all links are returned.
		"""

		pages = [ 'Olympique Lyonnais', 'Michelangelo' ]
		articles = links.collect(pages, separate=True)
		self.assertEqual(set(pages), set(articles.keys()))
		self.assertTrue('Olympique Lyonnais' in articles)
		self.assertTrue('Michelangelo' in articles)
		self.assertTrue('AS Saint-Étienne' in articles.get('Olympique Lyonnais'))
		self.assertTrue('Leonardo da Vinci' in articles.get('Michelangelo'))

	def test_get_links_with_redirects(self):
		"""
		Test that when getting links from a page that redirects, the collection allows redirection.
		"""

		page = 'Olympique Lyon'
		articles = links.collect(page, separate=True)
		self.assertTrue(page in articles)

	def test_get_links_with_redirects_same_as_redirects(self):
		"""
		Test that the links from the redirection are the same as the links without redirection.
		"""

		redirect_articles = links.collect('Olympique Lyon', separate=False)
		articles = links.collect('Olympique Lyonnais', separate=False)
		self.assertEqual(set(articles), set(redirect_articles))

	def test_link_with_accents(self):
		"""
		Test that links that include an accent are still returned.
		"""

		page = 'French name'
		articles = links.collect(page, separate=False)
		self.assertTrue('Orléans' in articles)
		self.assertTrue('Claude Allègre' in articles)
		self.assertTrue('Côté' in articles)
		self.assertTrue('Māori naming customs' in articles)
		self.assertTrue('García (surname)' in articles)

	def test_seed_set_with_accents(self):
		"""
		Test that seed sets that include accents return results.
		"""

		pages = [ 'Orléans', 'Claude Allègre', 'Côté', 'Māori naming customs', 'García (surname)' ]
		articles = links.collect(pages, separate=True)
		self.assertEqual(set(pages), set(articles.keys()))
		self.assertTrue(all(len(links) for links in articles.values()))

	def test_collective_links_same_as_individual(self):
		"""
		Test that getting links from pages individually results in the same links as when fetched collectively.
		"""

		results = [ ]
		pages = [ 'Orléans', 'Claude Allègre', 'Côté', 'Māori naming customs', 'García (surname)' ]
		for page in pages:
			results = results + links.collect(page, separate=False)

		self.assertTrue(set(results), links.collect(pages, separate=False))

	def test_links_introduction_only(self):
		"""
		Test getting links from the introduction only.
		"""

		page = 'Olympique Lyon'
		articles = links.collect(page, separate=True, introduction_only=True)
		self.assertTrue(page in articles)
		self.assertTrue(len(articles.get(page)))

	def test_links_introduction_less_than_whole(self):
		"""
		Test that when getting the links from the introduction, there are fewer links than when fetching from the whole article.
		"""

		intro_articles = links.collect('Olympique Lyonnais', separate=False, introduction_only=True)
		articles = links.collect('Olympique Lyonnais', separate=False, introduction_only=False)
		self.assertLess(len(intro_articles), len(articles))

	def test_links_introduction_subset_whole(self):
		"""
		Test that when getting links from the introduction, the links a subset of the links in the whole article.
		"""

		intro_articles = links.collect('Olympique Lyonnais', separate=False, introduction_only=True)
		articles = links.collect('Olympique Lyonnais', separate=False, introduction_only=False)
		articles = [ article.lower() for article in articles ]
		self.assertTrue(all(article.lower() in articles for article in intro_articles))
