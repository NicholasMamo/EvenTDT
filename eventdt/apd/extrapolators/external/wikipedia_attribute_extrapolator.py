"""
The :class:`~WikipediaAttributeExtrapolator` is an extrapolator that extracts participants that have the same attributes as those resolved.
The extrapolator revolves closely around the :class:`~attributes.extractors.linguistic.LinguisticExtractor` to build profiles for participants and candidates.

.. note::

    The algorithm assumes that all resolved participants map to a Wikipedia page.
    Therefore Wikipedia-based resolvers make for good candidates before extrapolation.
    Both the :class:`~apd.resolvers.external.wikipedia_name_resolver.WikipediaNameResolver` and the :class:`~apd.resolvers.external.wikipedia_search_resolver.WikipediaSearchResolver` return participants as Wikipedia concepts.
"""

import nltk
import os
import sys

path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
if path not in sys.path:
    sys.path.append(path)

from ..extrapolator import Extrapolator
from attributes import Profile
from attributes.extractors import LinguisticExtractor
from wikinterface import info, links, text

class WikipediaAttributeExtrapolator(Extrapolator):
    """
    The :class:`~WikipediaAttributeExtrapolator` relies on understanding to extrapolate participants.
    Understanding, here, means what makes a participant a participant.
    The class uses the :class:`~attributes.extractors.linguistic.LinguisticExtractor` to create profiles of resolved participants and looks for other participants with similar attributes.

    :ivar prune: The threshold at which attributes are removed.
                 If an attribute appears this many times or fewer, the extrapolator removes it.
                 By default, a threshold of 0 retains all attributes.
    :vartype prune: int
    """

    def __init__(self, prune=0, fetch=200):
        """
        Create the :class:`~WikipediaAttributeExtrapolator`.

        :param prune: The threshold at which attributes are removed.
                      If an attribute appears this many times or fewer, the extrapolator removes it.
                      By default, a threshold of 0 retains all attributes.
        :type prune: int
        :param fetch: The maximum number of candidates to fetch.
        :type fetch: int

        :raises ValueError: If the prune value is not zero or a natural number.
        :raises ValueError: If the fetch value is not a natural number.
        """

        if prune < 0 or prune % 1:
            raise ValueError(f"The prune value must be zero or a natural number; received { prune }")

        if fetch < 1 or fetch % 1:
            raise ValueError(f"The fetch value must be zero or a natural number; received { fetch }")

        self.prune = prune
        self.fetch = fetch

    def extrapolate(self, participants, *args, **kwargs):
        """
        Extrapolate the given participants.

        Extrapolation performs the following steps:

        - Build profiles for each resolved participant
        - Fetch all pages linked from the resolved participants' pages as candidates and build their profiles
        - Score and rank the candidates' profiles by comparing them with the resolved participants' profiles

        :param participants: The participants to extrapolate.
                             It is assumed that all participants were resolved using a Wikipedia resolver.
                             This means that all participants map to a Wikipedia page.

                             If the participants have a ``dict`` type, then the Wikipedia titles should be in the values
        :type participants: list of str or dict

        :return: The new participants and their scores.
        :rtype: dict
        """

        extrapolated = [ ]
        participants = list(participants.values()) if type(participants) is dict else participants

        resolved = self._build_profiles(participants)
        resolved = self._prune(resolved)
        candidates = self._generate_candidates(list(resolved))
        candidates = self._trim(candidates, resolved)
        extrapolated = self._score_and_rank(candidates, resolved)
        # TODO: Remove duplicates

        return extrapolated

    def _build_profiles(self, titles):
        """
        Build attribute profiles from the given Wikipedia articles.

        For each article, the function returns a :class:`~attributes.profile.Profile`.
        The profile considers only the first sentence of the article, since it usually refers unambiguously to the article's subject.

        :param titles: The Wikipedia article titles.
        :type titles: list of str

        :return: A dictionary with the Wikipedia titles as keys and the corresponding :class:`~attributes.profile.Profile` instances as values.
        :rtype: dict
        """

        # create the empty profiles in case some pages are missing
        profiles = { title: Profile(name=title) for title in titles }

        extractor = LinguisticExtractor()
        definitions = text.collect(titles, introduction_only=True)
        definitions = { title: text for title, text in definitions.items()
                                    if title in titles }
        definitions = { title: nltk.sent_tokenize(text)[0] if text else text
                        for title, text in definitions.items() }
        profiles.update({ title: extractor.extract(text, name=title)
                          for title, text in definitions.items() })

        return profiles

    def _prune(self, profiles):
        """
        Prune the attributes from the given profiles.

        This function removes attributes that appear below the given threshold.
        The function only considers attribute names, not values, when calculating the frequency.

        :param profiles: The profiles to prune.
                         The dictionary should have the profile names (the article titles) as keys, and the profiles as values.
        :type profiles: dict

        :return: Copies of the profiles with infrequent attributes removed.
                 Each profile is returned as a dictionary, with the profile names as keys and their scores as values.
        :rtype: dict

        :raises ValueError: If the number of profiles is lower than the prune threshold, which would remove all attributes.
        """

        profiles = { name: profile.copy() for name, profile in profiles.items() }

        if self.prune and self.prune >= len(profiles):
            raise ValueError(f"The number of profiles ({ len(profiles) }) is less than the prune threshold ({ self.prune }) and will remove all attributes")

        # calculate attribute frequency and remove infrequent attributes
        freq = self._attribute_frequency(profiles)
        freq = { attr for attr, _freq in freq.items()
                      if _freq > self.prune }

        # update the profile attributes
        for profile in profiles.values():
            profile.attributes = { attr: value for attr, value in profile.attributes.items()
                                               if attr in freq }

        return profiles

    def _all_attributes(self, profiles):
        """
        Extract the set of all attributes from the profiles.

        :param profiles: The profiles from where to extract attributes.
                         The dictionary should have the profile names (the article titles) as keys, and the profiles as values.
        :type profiles: dict

        :return: A set of attribute names in the profiles.
        :rtype: set of str
        """

        return set([ attribute for profile in profiles.values() for attribute in profile.attributes ])

    def _attribute_frequency(self, profiles):
        """
        Count the frequency of attributes in all profiles.

        :param profiles: The profiles from where to count attribute frequency.
                         The dictionary should have the profile names (the article titles) as keys, and the profiles as values.
        :type profiles: dict

        :return: A dictionary with attribute names as keys and their profile frequency as values.
        :rtype: dict
        """

        freq = dict.fromkeys(self._all_attributes(profiles), 0)
        freq = { attribute: sum( attribute in profile.attributes for profile in profiles.values())
                 for attribute in freq }
        return freq

    def _generate_candidates(self, participants):
        """
        Generate a list of candidates from the resolved participants.

        The function looks for outgoing links using Wikipedia and builds profiles for them.
        It only considers as candidates normal pages, removing help pages and other types of pages.

        :param participants: A list of resolved or extrapolated participants from which to generate candidates.
        :type participants: list of str

        :return: The candidates as a dictionary.
                 The keys are the Wikipedia article titles and the values are the corresponding :class:`~attributes.profile.Profile` instances.
        :rtype: dict
        """

        profiles = { }

        # keep the links separate and then flatten them to retain duplicate links
        related = links.collect(participants, separate=True, introduction_only=False)
        related = [ link for links in related.values() for link in links ]

        # fetch the link types and retain only normal pages
        types = info.types(list(related))
        related = [ page for page in related if types[page] == info.ArticleType.NORMAL ]
        related = self._rank_links(related)[:self.fetch]

        # build the profiles
        profiles = self._build_profiles(related)
        return profiles

    def _rank_links(self, links):
        """
        Rank links in descending order of popularity.

        :param links: The list of links to rank, which may include duplicates.
        :type links: list of str

        :return: The links without duplicates and sorted in descending order of frequency.
        :rtype: list of str
        """

        freq = { link: links.count(link) for link in links }
        return sorted(freq.keys(), key=freq.get, reverse=True)

    def _trim(self, profiles, reference):
        """
        Trim the attributes that do not appear in the reference profiles from the given profiles.

        Trimming makes the comparison between profiles fairer.
        Intuitively, it does not make sense to penalize candidate profiles for having attributes that are not present in the reference profiles.
        The attributes in candidate profiles may be valid and relevant despite not being in the reference profiles.
        If we do not remove them, we could needlessly punish candidates for having comprehensive definitions.
        Without knowing whether they are valid, it is safer to exclude those attributes.

        :param profiles: The profiles to trim.
                         The dictionary should have the profile names (the article titles) as keys, and the profiles as values.
        :type profiles: list of :class:`~attributes.profile.Profile`
        :param reference: The reference profiles against which to trim the profiles.
                          The dictionary should have the profile names (the article titles) as keys, and the profiles as values.
        :type reference: dict

        :return: Copies of the profiles with only the attributes that appear in the reference profiles.
                 Each profile is returned as a dictionary, with the profile names as keys and their scores as values.
        :rtype: dict
        """

        profiles = { name: profile.copy() for name, profile in profiles.items() }

        attributes = self._all_attributes(reference)

        # update the profile attributes
        for profile in profiles.values():
            profile.attributes = { attr: value for attr, value in profile.attributes.items()
                                               if attr in attributes }

        return profiles

    def _score_and_rank(self, candidates, reference):
        """
        Score the given profiles by comparing them with the reference profiles.

        The comparison calculates the Jaccard similarity between each profile and all other reference profiles.
        The final score of a profile is its average similarity with all other reference profiles

        :param candidates: The profiles for which to calculate the score, representing candidates.
                           The dictionary should have the profile names (the article titles) as keys, and the profiles as values.
        :type candidates: dict
        :param reference: The reference profiles against which to calculate the score of the candidates.
                          The dictionary should have the profile names (the article titles) as keys, and the profiles as values.
        :type reference: dict

        :return: The scores for each candidate profile as a dictionary, with the profile names as keys and their scores as values.
        :rtype: dict
        """

        scores = { candidate: 0 for candidate in candidates }
        scores = { candidate: score for candidate, score in scores.items() if score > 0 }
        return scores
