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
    :ivar fetch: The maximum number of candidates to fetch.
    :vartype fetch: int
    :ivar extractor: The extractor to use to build profiles.
                     By default, the extractor extracts only the head noun or entity.
    :vartype extractor: :class:`~attributes.extractors.linguistic.LinguisticExtractor`
    """

    def __init__(self, prune=0, fetch=200, head_only=True, *args, **kwargs):
        """
        Create the :class:`~WikipediaAttributeExtrapolator`.

        :param prune: The threshold at which attributes are removed.
                      If an attribute appears this many times or fewer, the extrapolator removes it.
                      By default, a threshold of 0 retains all attributes.
        :type prune: int
        :param fetch: The maximum number of candidates to fetch.
        :type fetch: int
        :param head_only: A boolean indicating whether to keep only the head nouns or named entities of attribute values.
        :type head_only: bool

        :raises ValueError: If the prune value is not zero or a natural number.
        :raises ValueError: If the fetch value is not a natural number.
        """

        if prune < 0 or prune % 1:
            raise ValueError(f"The prune value must be zero or a natural number; received { prune }")

        if fetch < 1 or fetch % 1:
            raise ValueError(f"The fetch value must be zero or a natural number; received { fetch }")

        self.prune = prune
        self.fetch = fetch
        self.extractor = LinguisticExtractor(head_only=head_only)

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

        extrapolated = { }
        participants = list(participants.values()) if type(participants) is dict else participants

        resolved = self._build_profiles(participants)
        resolved = self._prune(resolved)
        resolved = self._remove_duplicates(resolved, policy=any, reverse=True)
        candidates = self._generate_candidates(list(participants))
        candidates = self._trim(candidates, resolved)
        scores = self._score_and_rank(candidates, resolved)
        extrapolated = { candidate: score for candidate, score in scores.items()
                                          if score > 0 }
        extrapolated = { candidate: score for candidate, score in extrapolated.items()
                                          if candidate not in participants }

        return extrapolated

    def _build_profiles(self, titles):
        """
        Build attribute profiles from the given Wikipedia articles.

        For each article, the function returns a :class:`~attributes.profile.Profile`.
        The profile considers only the first sentence of the article, since it usually refers unambiguously to the article's subject.

        .. note:

            The function builds profiles in bulk, rather than one-by-one, to minimize the number of requests and maximize throughput.

        :param titles: The Wikipedia article titles.
        :type titles: list of str

        :return: A dictionary with the Wikipedia titles as keys and the corresponding :class:`~attributes.profile.Profile` instances as values.
        :rtype: dict
        """

        # create the empty profiles in case some pages are missing
        profiles = { title: Profile(name=title) for title in titles }

        definitions = text.collect(titles, introduction_only=True)
        definitions = { title: text for title, text in definitions.items()
                                    if title in titles }
        definitions = { title: nltk.sent_tokenize(text)[0] if text else text
                        for title, text in definitions.items() }
        profiles.update({ title: self.extractor.extract(text, name=title)
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
                 Each profile is returned as a dictionary, with the profile names as keys and their profiles as values.
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

    def _remove_duplicates(self, profiles, policy=any, reverse=False):
        """
        Remove duplicate participant profiles by checking whether a profile shares its attribute values with any other.

        The function is used to diversify the seed set and avoid overfitting.

        :param profiles: The profiles to de-duplicate.
                         The dictionary should have the profile names (the article titles) as keys, and the profiles as values.
        :type profiles: dict
        :param policy: The policy with which to de-duplicate profiles.
                       If the policy is `all`, the function considers two profiles to be duplicates if they share all attributes and all attribute values.
                       If the policy is `any`, the function considers two profiles to be duplicates if they share all attributes and at least one value in each attribute.
        :type policy: function
        :param reverse: A boolean indicating whether to remove the profiles.
                        If set to ``True``, the tail of the participants are more likely to be retained, and vice-versa.
                        Thus, setting the parameter to ``True`` can help reduce the bias.
        :type reverse: bool

        :return: A new dictionary of profiles with no duplicates.
                 The dictionary has the profile names (the article titles) as keys, and the profiles as values.
        :rtype: dict
        """

        deduplicated = { }

        profiles = { name: profile.copy() for name, profile in profiles.items() }

        for name, profile in list(profiles.items())[::(-1 if reverse else 1)]:
            is_duplicate = any([ set(profile.matching(other, policy=policy)) == set(self._all_attributes({ profile.name: profile, other.name: other }))
                                 for other in deduplicated.values() ])
            if not is_duplicate:
                deduplicated[name] = profile

        return { name: profile for name, profile in list(deduplicated.items())[::-1] } if reverse else deduplicated

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
        :type profiles: dict
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
        if reference:
            scores = { candidate: sum( self._jaccard(profile, other) for other in reference.values() ) / len(reference)
                       for candidate, profile in candidates.items() }

        ranked = sorted(scores, key=scores.get, reverse=True)
        scores = { candidate: scores[candidate] for candidate in ranked }
        return scores

    def _jaccard(self, p1, p2):
        """
        Calculate the Jaccard similarity between the two profiles.

        Jaccard similarity is symmetric and bound between 0 and 1.
        In case one or both profiles have more than one value for an attribute, the function calculates Jaccard similarity between their values.

        :param p1: The first profile to calculate similarity for.
        :type p1: :class:`~attributes.profile.Profile`
        :param p2: The second profile to calculate similarity for.
        :type p2: :class:`~attributes.profile.Profile`

        :return: The Jaccard similarity between the two profiles.
        :rtype: float
        """

        """
        .. note::

            After trimming, both profiles, the participant and the candidate, will have only the acceptable, pruned attributes.
            Therefore we can assume that all attributes are valid, and the participant and the candidate must agree on all of them.
            That is why, at the end, the function divides by the number of all attributes.
        """

        # if neither profile has attributes, the Jaccard similarity is taken to be zero
        attr = self._all_attributes({ 'p1': p1, 'p2': p2 })
        if not attr:
            return 0

        # if an attribute does not appear in both profiles, the Jaccard similarity will be 0 anyway, so we skip the attribute if it does not appear in both
        scores = [ self._jaccard_attr(p1.attributes[_attr], p2.attributes[_attr]) for _attr in p1.common(p2) ]
        return sum(scores)/len(attr)

    def _jaccard_attr(self, a1, a2):
        """
        Calculate the Jaccard similarity of two attribute value sets.

        :param a1: The first attribute value set with which to calculate similarity.
        :type a1: set of str
        :param a2: The second attribute value set with which to calculate similarity.
        :type a2: set of str

        :return: The Jaccard similarity between the two attribute value sets.
        :rtype: float
        """

        if not a1 or not a2:
            return 0

        return len(a1.intersection(a2))/len(a1.union(a2))
