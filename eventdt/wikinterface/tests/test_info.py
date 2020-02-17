"""
Run unit tests on the info module.
"""

import os
import sys
import unittest

path = os.path.join(os.path.dirname(__file__), '..', '..')
if path not in sys.path:
    sys.path.append(path)

from wikinterface import info

class TestInfo(unittest.TestCase):
	"""
	Test the info module.
	"""

	def test_get_type_no_pages(self):
		"""
		Test getting the type of a simple page.
		"""

		type = info.types([ ])
		self.assertEqual({ }, type)

	def test_get_type(self):
		"""
		Test getting the type of a simple page.
		"""

		page = 'Rudi Garcia'
		type = info.types(page)
		self.assertEqual(info.ArticleType.NORMAL, type[page])

	def test_get_type_missing_page(self):
		"""
		Test getting the type of a page that doesn't exist.
		"""

		page = 'Rudi Garcia (French coach)'
		type = info.types(page)
		self.assertEqual(info.ArticleType.MISSING, type[page])

	def test_get_type_disambiguation_page(self):
		"""
		Test getting the type of a page that is actually a disambiguation.
		"""

		page = 'Garcia'
		type = info.types(page)
		self.assertEqual(info.ArticleType.DISAMBIGUATION, type[page])

	def test_get_type_redirect(self):
		"""
		Test getting the type of a page that redirects returns the input page.
		"""

		page = 'Olympique Lyon'
		type = info.types(page)
		self.assertEqual(info.ArticleType.NORMAL, type[page])

	def test_get_type_multiple_pages(self):
		"""
		Test getting the types of multiple pages returns information about all pages.
		"""

		pages = [ 'Bordeaux', 'Lyon' ]
		types = info.types(pages)
		self.assertEqual(len(pages), len(types))
		self.assertEqual(set(pages), set(list(types.keys())))
		self.assertTrue(all(type == info.ArticleType.NORMAL for type in types.values()))

	def test_get_type_many_pages(self):
		"""
		Test getting the types of many pages returns (more than the stagger value) information about all pages.
		"""

		pages = [ 'Anthony Lopes', 'Mapou Yanga-Mbiwa', 'Joachim Andersen',
				  'Rafael',  'Jason Denayer', 'Marcelo', 'Martin Terrier',
				  'Houssem Aouar',  'Moussa Dembélé', 'Bertrand Traoré',
				  'Memphis Depay', 'Thiago Mendes', 'Léo Dubois', 'Oumar Solet',
				  'Jeff Reine-Adélaïde', 'Rayan Cherki', 'Bruno Guimarães',
				  'Amine Gouiri', 'Marçal', 'Karl Toko Ekambi', 'Jean Lucas',
				  'Kenny Tete', 'Maxence Caqueret', 'Camilo Reijers de Oliveira',
				  'Maxwel Cornet', 'Youssouf Koné', 'Lucas Tousart',
				  'Ciprian Tătărușanu', 'Boubacar Fofana']
		types = info.types(pages)
		self.assertEqual(len(pages), len(types))
		self.assertEqual(set(pages), set(list(types.keys())))
		self.assertEqual(info.ArticleType.DISAMBIGUATION, types['Rafael'])
