"""
Test the different cleaners' functionality.
"""

import os
import sys
import unittest

path = os.path.dirname(__file__)
path = os.path.join(path, '../')
if path not in sys.path:
    sys.path.append(path)

from libraries.vector.nlp.cleaners.tweet_cleaner import TweetCleaner

class TestCleaners(unittest.TestCase):
	"""
	Test the implementation and results of the different cleaners.
	"""

	def test_tweet_cleaner(self):
		"""
		Test :class:`summarization.cleaner.tweet_cleaner.TweetCleaner`
		"""

		tweet_cleaner = TweetCleaner()

		"""
		Test the basic cleaning functionality.
		"""
		tweet = "Penalty for Leganes after a foul by Casemiro"
		self.assertEqual(tweet_cleaner.clean(tweet), "Penalty for Leganes after a foul by Casemiro.")
		tweet = "Penalty for Leganes after a foul by Casemiro."
		self.assertEqual(tweet_cleaner.clean(tweet), "Penalty for Leganes after a foul by Casemiro.")
		tweet = "Penalty for Leganes after a foul by Casemiro!"
		self.assertEqual(tweet_cleaner.clean(tweet), "Penalty for Leganes after a foul by Casemiro!")
		tweet = "Penalty for Leganes after a foul by Casemiro?"
		self.assertEqual(tweet_cleaner.clean(tweet), "Penalty for Leganes after a foul by Casemiro?")

		tweet = "Penalty for Leganes after a foul by Casemiro.\nLeganes transform!"
		self.assertEqual(tweet_cleaner.clean(tweet), "Penalty for Leganes after a foul by Casemiro. Leganes transform!")
		tweet = "Penalty for Leganes after a foul by Casemiro.\nLeganes  transform!"
		self.assertEqual(tweet_cleaner.clean(tweet), "Penalty for Leganes after a foul by Casemiro. Leganes transform!")

		"""
		Test hashtag cleaning functionality.
		"""
		tweet = "Ndombele says the crossbar has stopped trembling. #PSG #TanguyNdombele."
		self.assertEqual(tweet_cleaner.clean(tweet), "Ndombele says the crossbar has stopped trembling. Tanguy Ndombele.")

		"""
		Test emoji removal functionality.
		"""
		tweet = "RT @KriiCamilleri92: #SouthKorea win the U23 Asian Games final! Which means #HeungMinSon will only have to serve 4 weeks in the military! So happy for the lad :D"
		self.assertEqual(tweet_cleaner.clean(tweet), "South Korea win the U23 Asian Games final! Which means Heung Min Son will only have to serve 4 weeks in the military! So happy for the lad.")
		tweet = "RT @KriiCamilleri92: #SouthKorea win the U23 Asian Games final! Which means #HeungMinSon will only have to serve 4 weeks in the military! So happy for the lad :)"
		self.assertEqual(tweet_cleaner.clean(tweet), "South Korea win the U23 Asian Games final! Which means Heung Min Son will only have to serve 4 weeks in the military! So happy for the lad.")

		"""
		Test URL removal functionality.
		"""
		tweet = "RT @Footy_JokesOG: Manchester United fans right now... https://t.co/7m3bysitgk"
		self.assertEqual(tweet_cleaner.clean(tweet), "Manchester United fans right now...")

		"""
		Other test cases.
		"""
		tweet = "RT @SquawkaNews: Eden Hazard on the summer transfer window: “I will tell you the truth, after the World Cup I wanted to leave, because my d…"
		self.assertEqual(tweet_cleaner.clean(tweet), "Eden Hazard on the summer transfer window: “I will tell you the truth, after the World Cup I wanted to leave, because my d…")
