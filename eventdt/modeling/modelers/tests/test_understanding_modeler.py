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
            self.assertEqual(participant.attributes, copy.attributes)

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

    def test_who_checks_known_as_case_folds(self):
        """
        Test that identifying the Who also uses the `known_as` attribute if it exists, and it folds the case.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [
            Document(text="carlos sainz crashes out with engine failure"),
        ]))

        participants = self.mock_participants()
        modeler = UnderstandingModeler(participants=participants.values())
        models = modeler.model(timeline)
        self.assertEqual({ 'Carlos Sainz Jr.' }, { participant.name for participant in models[0].who })

    def test_who_known_as_like_name(self):
        """
        Test that identifying the Who, mentions of the `known_as` attribute are treated exactly the same as if the full name is mentioned.
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
        Test that identifying the Where with NER returns all persons and orgaizations if there are no participants.
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

    def test_when_uses_created_at(self):
        """
        Test that extracting the When simply uses the node's `created_at` attribute.
        """

        timeline = Timeline(DocumentNode, expiry=60, min_similarity=0.5)
        timeline.nodes.append(DocumentNode(datetime.now().timestamp(), [ ]))

        modeler = UnderstandingModeler()
        models = modeler.model(timeline)
        self.assertTrue(all( model.when[0] == node.created_at for model, node in zip(models, timeline.nodes) ))
