"""
Test the functionality of the :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` class.
"""

from datetime import datetime
import json
import os
import sys
import unittest

paths = [ os.path.join(os.path.dirname(__file__), '..', '..', '..') ]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)

from attributes.extractors import LinguisticExtractor
from attributes import Profile
from modeling import EventModel
from modeling.modelers import UnderstandingModeler
import nlp
from nlp import Document
from summarization.timeline import Timeline
from summarization.timeline.nodes import DocumentNode

class TestUnderstandingModeler(unittest.TestCase):
    """
    Test the functionality of the :class:`~modeling.modelers.understanding_modeler.UnderstandingModeler` class.
    """

    def mock_concepts(self):
        """
        Create a list of mock concepts that represent the What.

        :return: A list of concepts, each of which is a list of strings.
        :rtype: list of list of string
        """

        return [
            [ 'engine', 'failure' ],
            [ 'win' ],
            [ 'tyre', 'pit', 'stop' ]
        ]

    def mock_participants(self):
        """
        Create a list of mock participants that represent the Who and the Where.

        :return: A dictionary with the participant names as keys and the profiles as values.
        :rtype: dict
        """

        corpus = {
            "Max Verstappen": "Max Emilian Verstappen (born 30 September 1997) is a Belgian-Dutch racing driver and the 2021 Formula One World Champion.",
            "Pierre Gasly": "Pierre Gasly (French pronunciation: ​[pjɛʁ ɡasli]; born 7 February 1996) is a French racing driver, currently competing in Formula One under the French flag, racing for Scuderia AlphaTauri.",
            "Carlos Sainz Jr.": "Carlos Sainz Vázquez de Castro (Spanish pronunciation: [ˈkaɾlos ˈsajnθ ˈβaθkeθ ðe ˈkastɾo] (listen); born 1 September 1994), otherwise known as Carlos Sainz Jr. or simply Carlos Sainz[a], is a Spanish racing driver currently competing in Formula One for Scuderia Ferrari.",
            "George Russell (racing driver)": "George William Russell (/rʌsəl/; born 15 February 1998) is a British racing driver currently competing in Formula One for Mercedes.",
            "FIA": "The Fédération Internationale de l'Automobile (FIA; English: International Automobile Federation) is an association established on 20 June 1904 to represent the interests of motoring organisations and motor car users.",
            "Circuit Gilles Villeneuve": "The Circuit Gilles Villeneuve (also spelled Circuit Gilles-Villeneuve in French) is a 4.361 km (2.710 mi) motor racing circuit in Montreal, Quebec, Canada.",
            "Circuit de Monaco": "Circuit de Monaco is a 3.337 km (2.074 mi) street circuit laid out on the city streets of Monte Carlo and La Condamine around the harbour of the Principality of Monaco.",
            "Montreal": "Montreal (/ˌmʌntriˈɔːl/ (listen) MUN-tree-AWL; officially Montréal, French: [mɔ̃ʁeal] (listen)) is the second-most populous city in Canada and most populous city in the Canadian province of Quebec.",
            "Quebec (Canada)": "Quebec (/kəˈbɛk/ kə-BEK, sometimes /kwəˈbɛk/ kwə-BEK; French: Québec [kebɛk] (listen))[8] is one of the thirteen provinces and territories of Canada.",
            "Canada": "Canada is a country in North America.",
            "Mogyoród Hungary": "Mogyoród is a small traditional village in Pest County, Hungary.",
            "Nico Hülkenberg": "Nicolas Hülkenberg (German pronunciation: [ˈniːko ˈhʏlkənbɛɐ̯k], born 19 August 1987) is a German professional racing driver who currently serves as the reserve driver in Formula One for the Aston Martin F1 Team."
        }

        extractor = LinguisticExtractor()
        return { name: extractor.extract(text, name=name) for name, text in corpus.items() }

    def test_init_saves_concepts(self):
        """
        Test that on initialization, the class saves the concepts if given.
        """

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        self.assertEqual(concepts, modeler.concepts)

    def test_init_saves_no_concepts(self):
        """
        Test that on initialization, the class creates an empty list if no concepts are given.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ ], modeler.concepts)

    def test_init_saves_participants(self):
        """
        Test that on initialization, the class saves the participants if given.
        """

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        for participant, copy in zip(participants.values(), modeler.participants.values()):
            self.assertTrue(all( copy.attributes[attribute] == participant.attributes[attribute] for attribute in participant.attributes ))

    def test_init_saves_participants_as_dicts(self):
        """
        Test that on initialization, the class saves the participants as dictionaries if given.
        """

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        self.assertEqual(dict, type(modeler.participants))

    def test_init_preprocesses_participants(self):
        """
        Test that on initialization, the class pre-processes the participants if given.
        """

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        self.assertTrue(any( '(' in participant.name and not '(' in copy.name
                             for participant, copy in zip(participants.values(), modeler.participants.values()) ))
        self.assertTrue(all( participant.name.strip() == participant.name for participant in modeler.participants.values() ))

    def test_init_preprocesses_participants_converted_to_dicts(self):
        """
        Test that on initialization, the class pre-processes participant profiles if converted to dictionaries.
        """

        # convert the participants to a format similar to the participants tool's
        participants = [ { 'participant': participant.name, 'details': participant } for participant in self.mock_participants().values() ]
        modeler = UnderstandingModeler(participants=participants)
        self.assertTrue(any( '(' in participant['details'].name and not '(' in copy.name
                             for participant, copy in zip(participants, modeler.participants.values()) ))
        self.assertTrue(all( participant.name.strip() == participant.name for participant in modeler.participants.values() ))

    def test_init_preprocesses_participants_as_dict(self):
        """
        Test that on initialization, the class pre-processes participants if they are given as simple dictionaries without profiles.
        """

        # convert the participants to a format similar to the participants tool's
        participants = [ { 'participant': participant.name } for participant in self.mock_participants().values() ]
        modeler = UnderstandingModeler(participants=participants)
        self.assertTrue(any( '(' in participant['participant'] and not '(' in copy.name
                             for participant, copy in zip(participants, modeler.participants.values()) ))
        self.assertTrue(all( participant.name.strip() == participant.name for participant in modeler.participants.values() ))

    def test_init_preprocesses_participants_creates_profiles(self):
        """
        Test that on initialization, the class pre-processes participants and creates profiles for them even if they are given as simple dictionaries.
        """

        # convert the participants to a format similar to the participants tool's
        participants = [ { 'participant': participant.name } for participant in self.mock_participants().values() ]
        modeler = UnderstandingModeler(participants=participants)
        self.assertTrue(all( Profile == type(participant) for participant in modeler.participants.values()))

    def test_init_preprocesses_participants_with_types(self):
        """
        Test that on initialization, the class pre-processes participants and tags them with their entity types.
        """

        # convert the participants to a format similar to the participants tool's
        participants = [ { 'participant': participant.name } for participant in self.mock_participants().values() ]
        modeler = UnderstandingModeler(participants=participants)
        self.assertTrue(all( participant.attributes['is_person'] == participant.is_person()
                             for participant in modeler.participants.values() ))
        self.assertTrue(all( participant.attributes['is_location'] == participant.is_location()
                             for participant in modeler.participants.values() ))
        self.assertTrue(all( participant.attributes['is_organization'] == participant.is_organization()
                             for participant in modeler.participants.values() ))

    def test_init_copies_participants(self):
        """
        Test that on initialization, the class makes a copy of the participants if given.
        """

        participants = self.mock_participants()
        participant = participants['Max Verstappen']
        original = participant.copy()

        modeler = UnderstandingModeler(participants=participants.values())
        copy = modeler.participants['Max Verstappen']

        copy.attributes['test'] = { True }
        self.assertFalse('test' in participant.attributes)

        participant.attributes['test'] = { False }
        self.assertTrue(copy.test)

    def test_init_with_ner(self):
        """
        Test that on initialization, the class saves the preference of whether to use NER to identify participants, in addition to the understanding.
        """

        modeler = UnderstandingModeler(with_ner=False)
        self.assertFalse(modeler.with_ner)

        modeler = UnderstandingModeler(with_ner=True)
        self.assertTrue(modeler.with_ner)

    def test_init_saves_threshold(self):
        """
        Test that on initialization, the class saves the threshold.
        """

        modeler = UnderstandingModeler(threshold=0.67)
        self.assertEqual(0.67, modeler.threshold)

    def test_init_threshold_0_exclusive(self):
        """
        Test that on initialization, the modeler rejects a threshold of 0.
        """

        self.assertRaises(ValueError, UnderstandingModeler, threshold=0)

    def test_init_threshold_1_inclusive(self):
        """
        Test that on initialization, the modeler accepts a threshold of 1.
        """

        modeler = UnderstandingModeler(threshold=1)
        self.assertEqual(1, modeler.threshold)

    def test_who_returns_list(self):
        """
        Test that the Who returns a list of profiles.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(list, type(models))
        self.assertTrue(all( list == type(model.who) for model in models ))
        self.assertTrue(all( Profile == type(profile) for model in models for profile in model.who ))

    def test_who_no_participants(self):
        """
        Test that when there are no participants, the Who returns nothing.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( [ ] == model.who for model in models ))

    def test_who_no_documents(self):
        """
        Test that when there are no documents, the Who returns nothing.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( [ ] == model.who for model in models ))

    def test_who_matches_participants_beginning(self):
        """
        Test that the Who correctly identifies participants at the beginning of the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Max Verstappen wins the Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen' }, { participant.name for participant in models[0].who })

    def test_who_matches_participants_middle(self):
        """
        Test that the Who correctly identifies participants in the middle of the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen' }, { participant.name for participant in models[0].who })

    def test_who_matches_participants_end(self):
        """
        Test that the Who correctly identifies participants at the end of the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="The second Grand Prix of the season goes for Max Verstappen.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen' }, { participant.name for participant in models[0].who })

    def test_who_matches_possessives(self):
        """
        Test that the Who correctly identifies participants in the text even when used in possessives.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen's lead extended with latest Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen' }, { participant.name for participant in models[0].who })

    def test_who_count_participants(self):
        """
        Test that the Who correctly identifies participants in the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix."),
            Document(text="Max Verstappen wins the first Grand Prix of the season."),
            Document(text="France's Pierre Gasly finishes second despite slow start."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen' }, { participant.name for participant in models[0].who })

    def test_who_unrecognized_participants(self):
        """
        Test that if no participant matches the Who, the function returns an empty list.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Yuki Tsunoda wins the Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].who)

    def test_who_threshold_inclusive(self):
        """
        Test that the Who's 50% threshold is inclusive.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix."),
            Document(text="The Dutch wins the first Grand Prix of the season.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(1, len(models[0].who))
        self.assertTrue(any( 'Max Verstappen' == model.name for model in models[0].who ))

    def test_who_threshold_low(self):
        """
        Test that a low threshold accepts more participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix."),
            Document(text="Max Verstappen wins the first Grand Prix of the season."),
            Document(text="France's Pierre Gasly finishes second despite slow start."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), threshold=0.3)
        models = modeler.model(timeline)
        self.assertEqual(2, len(models[0].who))
        self.assertTrue(any( 'Max Verstappen' == model.name for model in models[0].who ))
        self.assertTrue(any( 'Pierre Gasly' == model.name for model in models[0].who ))

    def test_who_threshold_high(self):
        """
        Test that a high threshold accepts fewer participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix."),
            Document(text="Max Verstappen wins the first Grand Prix of the season."),
            Document(text="France's Pierre Gasly finishes second despite slow start."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), threshold=0.8)
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].who)

    def test_who_threshold_all(self):
        """
        Test that a high threshold accepts participants that appear in all documents.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix."),
            Document(text="Max Verstappen wins the first Grand Prix of the season."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), threshold=1)
        models = modeler.model(timeline)
        self.assertEqual(1, len(models[0].who))
        self.assertEqual('Max Verstappen', models[0].who[0].name)

    def test_who_repeated_participant(self):
        """
        Test that if a participant appears multiple times in one document, it is only counted once.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Max Verstappen's done it! Max Verstappen wins the Grand Prix."),
            Document(text="The Dutch wins the first Grand Prix of the season."),
            Document(text="The inaugural Grand Prix is over, and it goes Dutch.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].who)

    def test_who_multiple(self):
        """
        Test that a model's Who may have several participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix, Pierre Gasly the runner-up."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen', 'Pierre Gasly' },
                         { participant.name for participant in models[0].who })

    def test_who_with_parentheses(self):
        """
        Test that identifying the Who ignores parentheses.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix, George Russell the runner-up."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen', 'George Russell' },
                         { participant.name for participant in models[0].who })

    def test_who_case_fold_checks(self):
        """
        Test that identifying the Who ignores the case.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="max verstappen wins the grand prix, george russell the runner-up."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen', 'George Russell' },
                         { participant.name for participant in models[0].who })

    def test_who_whole_word(self):
        """
        Test that identifying the Who only checks against whole words.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Imagine FIAT racing here."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertFalse(models[0].who)

    def test_who_checks_known_as(self):
        """
        Test that identifying the Who also uses the `known_as` attribute if it exists.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Carlos Sainz crashes out with engine failure."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Carlos Sainz Jr.' }, { participant.name for participant in models[0].who })

    def test_who_checks_referred_to(self):
        """
        Test that identifying the Who also uses the `referred_to` attribute if it exists.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Carlos Sainz crashes out with engine failure."),
        ]))

        participants = self.mock_participants()
        for participant in [ participant for participant in participants.values() if participant.known_as ]:
            participant.attributes['referred_to'] = participant.known_as
            del participant.attributes['known_as']
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Carlos Sainz Jr.' }, { participant.name for participant in models[0].who })

    def test_who_checks_aliases_case_folds(self):
        """
        Test that identifying the Who also uses the alias attributes if they exist, and it folds the case.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="carlos sainz crashes out with engine failure"),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Carlos Sainz Jr.' }, { participant.name for participant in models[0].who })

    def test_who_checks_aliases_whole_word(self):
        """
        Test that identifying the Who's aliases only checks against whole words.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Imagine Carlos Sainzo racing here."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertFalse(models[0].who)

    def test_who_aliases_like_name(self):
        """
        Test that identifying the Who, mentions of the alias attributes are treated exactly the same as if the full name is mentioned.
        In other words, they count to the 50% threshold too.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Carlos Sainz crashes out with engine failure."),
            Document(text="Max Verstappen wins the grand prix, George Russell the runner-up."),
            Document(text="Engine failure marks Carlos Sainz Jr.'s Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Carlos Sainz Jr.' }, { participant.name for participant in models[0].who })

    def test_who_accepts_persons(self):
        """
        Test that identifying the Who accepts persons.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Carlos Sainz crashes out with engine failure."),
            Document(text="Max Verstappen wins the grand prix, George Russell the runner-up."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Carlos Sainz Jr.', 'Max Verstappen', 'George Russell' }, { participant.name for participant in models[0].who })
        self.assertTrue(all( participant.is_person() for participant in models[0].who ))

    def test_who_accepts_organizations(self):
        """
        Test that identifying the Who accepts organizations.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="FIA outlines rule changes ahead of new season."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'FIA' }, { participant.name for participant in models[0].who })
        self.assertTrue(all( participant.is_organization() for participant in models[0].who ))

    def test_who_rejects_locations(self):
        """
        Test that identifying the Who rejects locations.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Quebec, Canada: everything set for the Montreal Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(set(), { participant.name for participant in models[0].who })

    def test_who_type_mix(self):
        """
        Test that identifying the Who accepts only persons or locations even when there are locations.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Quebec, Canada: Max Verstappen wins the Montreal Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Max Verstappen' }, { participant.name for participant in models[0].who })
        self.assertTrue(all( participant.is_person() or participant.is_organization() for participant in models[0].who ))

    def test_who_entity_subset(self):
        """
        Test that identifying the Who maps named entities that appear in the text and as a substring of a participant.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Canada: Carlos wins the Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Carlos Sainz Jr.' }, { participant.name for participant in models[0].who })

    def test_who_entity_subset_known_as_case_folds(self):
        """
        Test that identifying the Who maps named entities that appear in the text and as a substring of a participant, and it folds the case.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Carlos Sainz crashes out with engine failure"), # extracts 'Carlos' as entity
        ]))

        participants = self.mock_participants()
        participants['Carlos Sainz Jr.'].name = 'Sainz'
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Sainz' }, { participant.name for participant in models[0].who })

    def test_who_entity_subset_whole_word(self):
        """
        Test that identifying the Who only checks against whole words.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Could you imagine Carl racing here."),
        ]))

        self.assertTrue(('Carl', 'PERSON') in nlp.entities(timeline.nodes[0].get_all_documents()[0].text, [ "PERSON" ]))
        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertFalse(models[0].who)

    def test_who_with_ner(self):
        """
        Test that identifying the Who with NER returns participants that do not appear in the understanding.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="In Canada, the Canadian Grand Prix ends without much fanfare."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=True)
        models = modeler.model(timeline)
        self.assertEqual({ 'grand prix' }, { participant.name for participant in models[0].who })

    def test_who_with_ner_only_unresolved(self):
        """
        Test that identifying the Who with NER only returns named entities that do not resolve to a participant from the understanding.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Canada: Carlos wins the Grand Prix followed by Verstappen."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=True)
        models = modeler.model(timeline)
        self.assertEqual({ 'Carlos Sainz Jr.', 'Max Verstappen', 'grand prix' }, { participant.name for participant in models[0].who })

    def test_who_with_ner_only_persons_and_organizations(self):
        """
        Test that identifying the Who with NER only returns persons and organizations.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="In Canada, Hamilton and Leclerc repeat the Spain double in the today's Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=True)
        models = modeler.model(timeline)
        self.assertEqual({ 'hamilton', 'leclerc', 'grand prix' }, { participant.name for participant in models[0].who })

    def test_who_with_ner_no_participants(self):
        """
        Test that identifying the Who with NER returns all persons and orgaizations if there are no participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(text="In Canada, Hamilton and Leclerc repeat the Spain double in the today's Grand Prix.")
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(with_ner=True)
        entities = nlp.entities(document.text, netype=[ 'PERSON', 'ORGANIZATION', 'FACILITY' ])

        models = modeler.model(timeline)
        entities = { entity.lower() for entity, _ in entities }
        who = { participant.name for participant in models[0].who }
        self.assertEqual(entities, who)

    def test_who_transliterates_participants(self):
        """
        Test that identifying the Who transliterates participants.
        This test addresses the first condition, which checks for the participant's name or aliases in the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(text="It seems likely that Nico Hulkenberg will remain a replacement")
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=False)
        models = modeler.model(timeline)
        self.assertTrue(models[0].who, [ participants['Nico Hülkenberg'] ])

    def test_who_transliterates_entities(self):
        """
        Test that identifying the Who transliterates entities.
        This test addresses the first condition and the second condition, which checks for entities that are subsets of the entity or its aliases.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(text="It seems likely that Hulkenberg will remain a replacement")
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=False)
        models = modeler.model(timeline)
        self.assertTrue(models[0].who, [ participants['Nico Hülkenberg'] ])

    def test_what_returns_list(self):
        """
        Test that the What returns a list of concepts.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(dimensions=[ 'leclerc', 'engine' ])
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)

        self.assertTrue(models[0].what)
        self.assertEqual(list, type(models[0].what))
        self.assertTrue(all( list == type(concept) for concept in models[0].what ))

    def test_what_no_concepts(self):
        """
        Test that the What returns an empty list when it has no concepts.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(dimensions=[ 'leclerc', 'engine' ])
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].what)

    def test_what_no_documents(self):
        """
        Test that the What returns an empty list when it has no documents.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ ]))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].what)

    def test_what_in_concepts(self):
        """
        Test that whatever the What returns exists is a given concept.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(dimensions=[ 'leclerc', 'win', 'failure', 'engine' ])
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertTrue(all( concept in concepts for concept in models[0].what ))

    def test_what_ignores_text(self):
        """
        Test that the What ignores the text and only looks for terms in the dimensions.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document("Leclerc crashes out with engine failure")
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].what)

    def test_what_counts_terms(self):
        """
        Test that the What correctly counts the number of concepts that appear in documents.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'engine', 'failure' ]),
            Document(dimensions=[ 'pit', 'stop', 'engine', 'failure' ]),
            Document(dimensions=[ 'leclerc' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual([[ 'engine', 'failure' ]], models[0].what)

    def test_what_counts_document_frequency(self):
        """
        Test that the What counts the document frequency of concepts to decide the subject.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'engine', 'failure', 'engine', 'failure' ]),
            Document(dimensions=[ 'pit', 'stop' ]),
            Document(dimensions=[ 'leclerc' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].what)

    def test_what_subset_of_concept(self):
        """
        Test that a few words are enough to capture a concept, as opposed to needing all terms to be present.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'engine' ]),
            Document(dimensions=[ 'pit', 'stop', 'failure' ]),
            Document(dimensions=[ 'leclerc' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual([[ 'engine', 'failure' ]], models[0].what)

    def test_what_allows_mixed_terms(self):
        """
        Test that different words from the same concept contribute to the concept's score.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'failure' ]),
            Document(dimensions=[ 'pit', 'stop', 'engine' ]),
            Document(dimensions=[ 'leclerc' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual([[ 'engine', 'failure' ]], models[0].what)

    def test_what_threshold_inclusive(self):
        """
        Test that the 50% threshold is inclusive when identifying the What.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'failure' ]),
            Document(dimensions=[ 'pit', 'stop', 'engine' ]),
            Document(dimensions=[ 'leclerc' ]),
            Document(dimensions=[ 'win', 'grand', 'prix' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual(1, len(models[0].what))
        self.assertEqual([ 'engine', 'failure' ], models[0].what[0])

    def test_what_threshold_low(self):
        """
        Test that a low threshold accepts more concepts.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'failure' ]),
            Document(dimensions=[ 'pit', 'stop', 'engine' ]),
            Document(dimensions=[ 'leclerc', 'tyre' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts, threshold=0.3)
        models = modeler.model(timeline)
        self.assertEqual(2, len(models[0].what))
        self.assertTrue([ 'engine', 'failure' ] in models[0].what)
        self.assertTrue([ 'tyre', 'pit', 'stop' ] in models[0].what)

    def test_what_threshold_high(self):
        """
        Test that a high threshold accepts fewer concepts.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'failure' ]),
            Document(dimensions=[ 'pit', 'stop', 'engine' ]),
            Document(dimensions=[ 'leclerc', 'tyre' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts, threshold=0.8)
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].what)

    def test_what_threshold_all(self):
        """
        Test that a high threshold accepts concepts that appear in all documents.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'failure' ]),
            Document(dimensions=[ 'pit', 'stop', 'engine' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts, threshold=1)
        models = modeler.model(timeline)
        self.assertEqual(1, len(models[0].what))
        self.assertTrue([ 'engine', 'failure' ] in models[0].what)

    def test_what_multiple_concepts(self):
        """
        Test that multiple concepts can be identified in one node.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'failure' ]),
            Document(dimensions=[ 'pit', 'stop', 'engine' ]),
            Document(dimensions=[ 'leclerc', 'win' ]),
            Document(dimensions=[ 'win', 'grand', 'prix' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual(2, len(models[0].what))
        self.assertTrue([ 'engine', 'failure' ] in models[0].what)
        self.assertTrue([ 'win' ] in models[0].what)

    def test_what_unrecognized_terms(self):
        """
        Test that unrecognized terms are excluded from the What.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'hamilton' ]),
            Document(dimensions=[ 'leclerc', 'hamilton' ]),
            Document(dimensions=[ 'leclerc', 'hamilton' ]),
            Document(dimensions=[ 'hamilton' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].what)

    def test_what_case_insensitive(self):
        """
        Test that extracting the What performs case-insensitive checks.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'FAILURE' ]),
            Document(dimensions=[ 'PIT', 'STOP', 'ENGINE' ]),
            Document(dimensions=[ 'LECLERC', 'WIN' ]),
            Document(dimensions=[ 'WIN', 'GRAND', 'PRIX' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual(2, len(models[0].what))
        self.assertTrue([ 'engine', 'failure' ] in models[0].what)
        self.assertTrue([ 'win' ] in models[0].what)

    def test_what_case_insensitive_reverse(self):
        """
        Test that extracting the What performs case-insensitive checks.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        documents = [
            Document(dimensions=[ 'failure' ]),
            Document(dimensions=[ 'pit', 'stop', 'engine' ]),
            Document(dimensions=[ 'leclerc', 'win' ]),
            Document(dimensions=[ 'win', 'grand', 'prix' ]),
        ]
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), documents))

        concepts = self.mock_concepts()
        concepts = [ [ term.upper() for term in concept ] for concept in concepts ]
        modeler = UnderstandingModeler(concepts=concepts)
        models = modeler.model(timeline)
        self.assertEqual(2, len(models[0].what))
        self.assertTrue([ 'ENGINE', 'FAILURE' ] in models[0].what)
        self.assertTrue([ 'WIN' ] in models[0].what)

    def test_where_returns_list(self):
        """
        Test that the Where returns a list of profiles.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Uneventful Montreal Grand Prix ends with a Dutch flair.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(list, type(models))
        self.assertTrue(all( list == type(model.where) for model in models ))
        self.assertTrue(all( Profile == type(profile) for model in models for profile in model.where ))

    def test_where_no_participants(self):
        """
        Test that when there are no participants, the Where returns nothing.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Uneventful Montreal Grand Prix ends with a Dutch flair.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( [ ] == model.where for model in models ))

    def test_where_no_documents(self):
        """
        Test that when there are no documents, the Where returns nothing.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( [ ] == model.where for model in models ))

    def test_where_matches_participants_beginning(self):
        """
        Test that the Where correctly identifies participants at the beginning of the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Montreal Grand Prix ends with a Dutch flair.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Montreal' }, { participant.name for participant in models[0].where })

    def test_where_matches_participants_middle(self):
        """
        Test that the Where correctly identifies participants in the middle of the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Uneventful Montreal Grand Prix ends with a Dutch flair.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Montreal' }, { participant.name for participant in models[0].where })

    def test_where_matches_participants_end(self):
        """
        Test that the Where correctly identifies participants at the beginning of the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Dutch flair in Montreal.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Montreal' }, { participant.name for participant in models[0].where })

    def test_where_matches_possessives(self):
        """
        Test that the Where correctly identifies participants in the text even when used in possessives.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Uneventful Montreal's Grand Prix ends with a Dutch flair.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Montreal' }, { participant.name for participant in models[0].where })

    def test_where_count_participants(self):
        """
        Test that the Where correctly identifies participants in the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Uneventful Montreal Grand Prix ends with a Dutch flair."),
            Document(text="Max Verstappen wins the Montreal Grand Prix."),
            Document(text="France's Pierre Gasly finishes second despite slow start."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Montreal' }, { participant.name for participant in models[0].where })

    def test_where_unrecognized_participants(self):
        """
        Test that if no participant matches the Where, the function returns an empty list.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Yuki Tsunoda wins the Imola Grand Prix.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].where)

    def test_where_threshold_inclusive(self):
        """
        Test that the Where's 50% threshold is inclusive.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Uneventful Montreal Grand Prix ends with a Dutch flair."),
            Document(text="The Dutch wins the first Grand Prix of the season.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(1, len(models[0].where))
        self.assertTrue(any( 'Montreal' == model.name for model in models[0].where ))

    def test_where_threshold_low(self):
        """
        Test that a low threshold accepts more participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix in Montreal."),
            Document(text="Max Verstappen wins the Montreal Grand Prix."),
            Document(text="France's Pierre Gasly finishes second in Canada despite slow start."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), threshold=0.3)
        models = modeler.model(timeline)
        self.assertEqual(2, len(models[0].where))
        self.assertTrue(any( 'Montreal' == model.name for model in models[0].where ))
        self.assertTrue(any( 'Canada' == model.name for model in models[0].where ))

    def test_where_threshold_high(self):
        """
        Test that a high threshold accepts fewer participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix in Montreal."),
            Document(text="Max Verstappen wins the Montreal Grand Prix."),
            Document(text="France's Pierre Gasly finishes second in Canada despite slow start."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), threshold=0.8)
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].where)

    def test_where_threshold_all(self):
        """
        Test that a high threshold accepts participants that appear in all documents.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix in Montreal."),
            Document(text="Max Verstappen wins the Montreal Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), threshold=1)
        models = modeler.model(timeline)
        self.assertEqual(1, len(models[0].where))
        self.assertEqual('Montreal', models[0].where[0].name)

    def test_where_repeated_participant(self):
        """
        Test that if a participant appears multiple times in one document, it is only counted once.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Montreal regales! Max Verstappen wins the Montreal Grand Prix."),
            Document(text="The Dutch wins the first Grand Prix of the season."),
            Document(text="The inaugural Grand Prix is over, and it goes Dutch.")
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual([ ], models[0].where)

    def test_where_multiple(self):
        """
        Test that a model's Where may have several participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="It's all over in Canada. The Montreal Grand Prix goes to the Dutch leader."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Montreal', 'Canada' },
                         { participant.name for participant in models[0].where })

    def test_where_with_parentheses(self):
        """
        Test that identifying the Where ignores parentheses.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Yuki Tsunoda finishes first in Quebec."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Quebec' }, { participant.name for participant in models[0].where })

    def test_where_case_fold_checks(self):
        """
        Test that identifying the Where ignores the case.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="it's all over in canada as the montreal grand prix goes to the dutch leader."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Montreal', 'Canada' },
                         { participant.name for participant in models[0].where })

    def test_where_whole_word(self):
        """
        Test that identifying the Where only checks against whole words.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Plenty of Montrealers here for the Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertFalse(models[0].where)

    def test_where_rejects_persons(self):
        """
        Test that identifying the Where rejects persons.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Carlos Sainz crashes out with engine failure."),
            Document(text="Max Verstappen wins the grand prix, George Russell the runner-up."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(set( ), { participant.name for participant in models[0].where })

    def test_where_rejects_organizations(self):
        """
        Test that identifying the Where rejects organizations.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="FIA outlines rule changes ahead of new season."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual(set( ), { participant.name for participant in models[0].where })

    def test_where_accepts_locations(self):
        """
        Test that identifying the Where accepts locations.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Quebec, Canada: everything set for the Montreal Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Quebec', 'Canada', 'Montreal' }, { participant.name for participant in models[0].where })
        self.assertTrue(all( participant.is_location() for participant in models[0].where ))

    def test_where_type_mix(self):
        """
        Test that identifying the Where accepts only locations even when there are several types of participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Quebec, Canada: Max Verstappen wins the Montreal Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Quebec', 'Canada', 'Montreal' }, { participant.name for participant in models[0].where })
        self.assertTrue(all( participant.is_location() for participant in models[0].where ))

    def test_where_entity_subset(self):
        """
        Test that identifying the Where maps named entities that appear in the text and as a substring of a participant.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Monaco: Carlos wins the Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Circuit de Monaco' }, { participant.name for participant in models[0].where })

    def test_where_entity_subset_whole_word(self):
        """
        Test that identifying the Where only checks against whole words.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="We're off for the race in Hungar."),
        ]))

        self.assertTrue(('Hungar', 'GPE') in nlp.entities(timeline.nodes[0].get_all_documents()[0].text, [ "GPE" ]))
        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertFalse(models[0].where)

    def test_where_with_ner(self):
        """
        Test that identifying the Where with NER returns participants that do not appear in the understanding.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="In Spain, the Grand Prix ends without much fanfare."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=True)
        models = modeler.model(timeline)
        self.assertEqual({ 'spain' }, { participant.name for participant in models[0].where })

    def test_where_with_ner_only_unresolved(self):
        """
        Test that identifying the Where with NER only returns named entities that do not resolve to a participant from the understanding.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="Spain: Carlos wins the Grand Prix followed by Verstappen, like they did in Canada."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=True)
        models = modeler.model(timeline)
        self.assertEqual({ 'spain', 'Canada' }, { participant.name for participant in models[0].where })

    def test_where_with_ner_only_locations(self):
        """
        Test that identifying the Where with NER only returns locations.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="In Canada, Hamilton and Leclerc repeat the Spain double in the today's Grand Prix."),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=True)
        models = modeler.model(timeline)
        self.assertEqual({ 'spain', 'Canada' }, { participant.name for participant in models[0].where })

    def test_where_with_ner_no_participants(self):
        """
        Test that identifying the Where with NER returns all locations if there are no participants.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(text="In Canada, Hamilton and Leclerc repeat the Spain double in the today's Grand Prix.")
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(with_ner=True)
        entities = nlp.entities(document.text, netype=[ 'GPE', 'GSP', "LOCATION" ])

        models = modeler.model(timeline)
        entities = { entity.lower() for entity, _ in entities }
        where = { location.name for location in models[0].where }
        self.assertEqual(entities, where)

    def test_where_transliterates_participants(self):
        """
        Test that identifying the Where transliterates participants.
        This test addresses the first condition, which checks for the participant's name or aliases in the text.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(text="In Mogyorod Hungary, the race is ready to start.")
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=False)
        models = modeler.model(timeline)
        self.assertTrue(models[0].where, [ participants['Mogyoród Hungary'] ])

    def test_where_transliterates_entities(self):
        """
        Test that identifying the Where transliterates entities.
        This test addresses the first condition and the second condition, which checks for entities that are subsets of the entity or its aliases.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        document = Document(text="In Mogyorod, the race is ready to start.")
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ document ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values(), with_ner=False)
        models = modeler.model(timeline)
        self.assertTrue(models[0].where, [ participants['Mogyoród Hungary'] ])

    def test_when_uses_created_at(self):
        """
        Test that extracting the When simply uses the node's `created_at` attribute.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ ]))

        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( model.when[0] == node.created_at for model, node in zip(models, timeline.nodes) ))

    def test_preprocess_node_all_documents(self):
        """
        Test that when pre-processing a node, the function creates a copy.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        modeler = UnderstandingModeler()
        self.assertNotEqual(timeline.nodes[0], modeler._preprocess_node(timeline.nodes[0]))
        self.assertTrue(all( original != document for original, document in zip(timeline.nodes[0].get_all_documents(), modeler._preprocess_node(timeline.nodes[0]).get_all_documents()) ))
        self.assertNotEqual(timeline.nodes[0], modeler._preprocess_node(timeline.nodes[0]))

    def test_preprocess_node_returns_node(self):
        """
        Test that when pre-processing a node, the function returns another node.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        modeler = UnderstandingModeler()
        self.assertEqual(type(timeline.nodes[0]), type(modeler._preprocess_node(timeline.nodes[0])))

    def test_preprocess_node_with_simplified_text(self):
        """
        Test that when pre-processing a node, the function stores each document's simplified (transliterated) text as an attribute.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        modeler = UnderstandingModeler()
        self.assertTrue(all( nlp.transliterate(original.text) == document.simplified_text
                             for original, document in zip(timeline.nodes[0].get_all_documents(), modeler._preprocess_node(timeline.nodes[0]).get_all_documents()) ))

    def test_preprocess_node_with_entities(self):
        """
        Test that when pre-processing a node, the function stores each document's entities as an attribute.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="He's done it! Max Verstappen wins the Grand Prix.")
        ]))

        modeler = UnderstandingModeler()
        entities = { entity: _type for entity, _type in nlp.entities(timeline.nodes[0].get_all_documents()[0].text) }
        node = modeler._preprocess_node(timeline.nodes[0])
        self.assertEqual(entities, node.get_all_documents()[0].entities)

    def test_matches_empty_reference(self):
        """
        Test that an empty reference matches no text.
        """

        modeler = UnderstandingModeler()
        self.assertFalse(modeler._matches('', "He's done it! Max Verstappen wins the Grand Prix."))

    def test_matches_empty_text(self):
        """
        Test that a reference never matches empty text.
        """

        modeler = UnderstandingModeler()
        self.assertFalse(modeler._matches('Max Verstappen', ""))

    def test_matches_returns_bool(self):
        """
        Test that matches always return True or False.
        """

        modeler = UnderstandingModeler()
        self.assertEqual(bool, type(modeler._matches('Gasly', "He's done it! Max Verstappen wins the Grand Prix.")))
        self.assertEqual(bool, type(modeler._matches('Verstappen', "He's done it! Max Verstappen wins the Grand Prix.")))

    def test_matches_start(self):
        """
        Test that matches in the beginning return True.
        """

        modeler = UnderstandingModeler()
        self.assertTrue(modeler._matches('Max', "Max Verstappen wins the Grand Prix."))

    def test_matches_middle(self):
        """
        Test that matches in the middle return True.
        """

        modeler = UnderstandingModeler()
        self.assertTrue(modeler._matches('Verstappen', "Max Verstappen wins the Grand Prix."))

    def test_matches_end(self):
        """
        Test that matches in the end return True.
        """

        modeler = UnderstandingModeler()
        self.assertTrue(modeler._matches('Prix', "Max Verstappen wins the Grand Prix"))

    def test_matches_whole_words(self):
        """
        Test that matches only perform whole-word searches.
        """

        modeler = UnderstandingModeler()
        self.assertFalse(modeler._matches('Vers', "Max Verstappen wins the Grand Prix."))

    def test_matches_whole_words_multiple(self):
        """
        Test that matches may include multiple words.
        """

        modeler = UnderstandingModeler()
        self.assertTrue(modeler._matches('Max Verstappen', "Max Verstappen wins the Grand Prix."))

    def test_matches_next_to_punctuation(self):
        """
        Test that punctuation is considered a word boundary when looking for matches.
        """

        modeler = UnderstandingModeler()
        self.assertTrue(modeler._matches('Grand Prix', "Max Verstappen wins the Grand Prix!"))

    def test_matches_with_plus(self):
        """
        Test that plus signs are escaped when looking for matches.
        Plus signs are word boundaries, so the search matches nothing, but it doesn't crash either.
        """

        modeler = UnderstandingModeler()
        self.assertFalse(modeler._matches('C++', "Languages such as C++ are on the decline!"))

    def test_matches_escapes_asterisks(self):
        """
        Test that matching escapes asterisk signs.
        Asterisks are word boundaries, so the search matches nothing, but it doesn't crash either.
        """

        modeler = UnderstandingModeler()
        self.assertFalse(modeler._matches('****', "Max Verstappen: What a **** race!"))

    def test_split_keeps_mentions(self):
        """
        Test that splitting the text retains mentions.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Well', 'done', 'ElfaDosInsetos' ],
                         modeler._split("Well done, @ElfaDosInsetos"))

    def test_split_keeps_hashtags(self):
        """
        Test that splitting the text retains hashtags.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Well', 'done', 'elfadosinsetos' ],
                         modeler._split("Well done, #elfadosinsetos"))

    def test_split_keeps_hashtags_whole(self):
        """
        Test that splitting the text retains hashtags whole, without splitting them.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Well', 'done', 'ElfaDosInsetos' ],
                         modeler._split("Well done, #ElfaDosInsetos"))

    def test_split_does_not_normalize_words(self):
        """
        Test that splitting the text does not normalize repeated characters.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Goooool' ],
                         modeler._split("Goooool"))

    def test_split_does_not_case_fold(self):
        """
        Test that splitting the text does not case-fold the text.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Four', 'of', 'Virgil', 'van', 'Dijk', 's', 'six', 'goals', 'for', 'the', 'Netherlands', 'were', 'headers', 'from', 'corners' ],
                         modeler._split("Four of Virgil van Dijk’s six goals for the Netherlands were headers from corners"))

    def test_split_keeps_stopwords(self):
        """
        Test that splitting the text keeps stopwords.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Four', 'of', 'Virgil', 'van', 'Dijk', 's', 'six', 'goals', 'for', 'the', 'Netherlands', 'were', 'headers', 'from', 'corners' ],
                         modeler._split("Four of Virgil van Dijk’s six goals for the Netherlands were headers from corners"))

    def test_split_keeps_accents(self):
        """
        Test that splitting the text keeps accents.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Federer', 's', 'class', 'unmatched', 'says', 'Björn', 'Borg' ],
                         modeler._split("Federer's class unmatched, says Björn Borg"))

    def test_split_keeps_short_tokens(self):
        """
        Test that splitting the text keeps short words.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Lacazette', 'named', 'a', 'man', 'of', 'the', 'match' ],
                         modeler._split("Lacazette named a man of the match"))

    def test_split_does_not_stem(self):
        """
        Test that splitting the text does not stem them.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'The', 'Mexican', 'army', 's', 'role', 'in', 'the', 'disappearance', 'of', '43', 'college', 'students' ],
                         modeler._split("The Mexican army’s role in the disappearance of 43 college students"))

    def test_split_keeps_numbers(self):
        """
        Test that splitting the text retains numbers.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Uganda', 's', 'Ebola', 'caseload', 'rises', 'to', '16', 'as', 'outbreak', 'spreads' ],
                         modeler._split("Uganda’s Ebola caseload rises to 16 as outbreak spreads"))

    def test_split_removes_punctuation(self):
        """
        Test that splitting the text also removes all punctuation.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'Bodies', 'everywhere', 'Survivors', 'recount', 'Lebanon', 'boat', 'disaster' ],
                         modeler._split("‘Bodies everywhere’: Survivors recount Lebanon boat disaster."))

        self.assertEqual([ 'Wales', '0', '1', 'Poland', 'A', 'moment', 'of', 'class', 'from', 'Poland', 'won', 'the', 'game', 'in', 'what', 'was', 'an', 'even', 'battle' ],
                         modeler._split("Wales 0-1 Poland: A moment of class from Poland won the game in what was an even battle."))

        self.assertEqual([ 'Russia', 'sought', 'to', 'defend', 'its', 'seven', 'month', 'old', 'war', 'at', 'the', 'UN', 'with', 'Foreign', 'Minister', 'Sergei', 'Lavrov', 'saying', 'that', 'regions', 'of', 'Ukraine', 'where', 'widely', 'derided', 'referendums', 'are', 'being', 'held', 'would', 'be', 'under', 'Russia', 's', 'full', 'protection', 'if', 'annexed', 'by', 'Moscow' ],
                         modeler._split("Russia sought to defend its seven-month old war at the UN, with Foreign Minister Sergei Lavrov saying that regions of Ukraine where widely-derided referendums are being held would be under Russia's 'full protection' if annexed by Moscow"))

    def test_split_separates_possessives(self):
        """
        Test that splitting the text also separates possessives.
        """

        modeler = UnderstandingModeler()
        self.assertEqual([ 'what', 's', 'pissing', 'me', 'off', 'right', 'now' ],
                         modeler._split("what's pissing me off right now"))
