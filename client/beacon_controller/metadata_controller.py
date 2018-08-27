from swagger_server.models.beacon_concept_category import BeaconConceptCategory  # noqa: E501
from swagger_server.models.beacon_knowledge_map_statement import BeaconKnowledgeMapStatement  # noqa: E501
from swagger_server.models.beacon_knowledge_map_object import BeaconKnowledgeMapObject
from swagger_server.models.beacon_knowledge_map_subject import BeaconKnowledgeMapSubject
from swagger_server.models.beacon_knowledge_map_predicate import BeaconKnowledgeMapPredicate
from swagger_server.models.beacon_predicate import BeaconPredicate  # noqa: E501

from collections import defaultdict
from functools import lru_cache
from beacon_controller.utils import safe_get

import requests

@lru_cache(maxsize=128)
def get_concept_categories():  # noqa: E501
    """get_concept_categories

    Get a list of concept categories and number of their concept instances documented by the knowledge source. These types should be mapped onto the Translator-endorsed Biolink Model concept type classes with local types, explicitly added as mappings to the Biolink Model YAML file.  # noqa: E501


    :rtype: List[BeaconConceptCategory]
    """
    response = requests.get('http://biothings.io/explorer/api/v2/metadata/bioentities')

    categories = []

    if response.ok:
        data = response.json()

        for key in data['bioentity'].keys():
            categories.append(BeaconConceptCategory(
                category=key
            ))

    return categories

@lru_cache(maxsize=128)
def get_knowledge_map():  # noqa: E501
    """get_knowledge_map

    Get a high level knowledge map of the all the beacons by subject semantic type, predicate and semantic object type  # noqa: E501


    :rtype: List[BeaconKnowledgeMapStatement]
    """
    response = requests.get('http://biothings.io/explorer/api/v2/knowledgemap')

    d = defaultdict(lambda: defaultdict(set))

    statements = []

    if response.ok:
        data = response.json()

        for a in data['associations']:
            subject_category = safe_get(a, 'subject', 'semantic_type')
            subject_prefix = safe_get(a, 'subject', 'prefix')
            predicate = safe_get(a, 'predicate')
            object_category = safe_get(a, 'object', 'semantic_type')
            object_prefix = safe_get(a, 'object', 'prefix')
            endpoint = safe_get(a, 'endpoint')

            k = '{}{}{}'.format(subject_category, predicate, object_category)

            d[k]['subject_prefix'].add(subject_prefix)
            d[k]['object_prefix'].add(object_prefix)
            d[k]['subject_category'] = subject_category
            d[k]['object_category'] = object_category
            d[k]['predicate'] = predicate
            d[k]['endpoint'] = endpoint

        for p in d.values():
            o = BeaconKnowledgeMapObject(
                category=p['object_category'],
                prefixes=list(p['object_prefix'])
            )
            s = BeaconKnowledgeMapSubject(
                category=p['subject_category'],
                prefixes=list(p['subject_prefix'])
            )
            if p['predicate'] == p['predicate'].lower():
                args = {'edge_label' : p['predicate']}
            else:
                args = {'relation' : p['predicate']}

            r = BeaconKnowledgeMapPredicate(
                negated=False,
                **args
            )
            statements.append(BeaconKnowledgeMapStatement(
                subject=s,
                object=o,
                predicate=r
            ))

    return statements

@lru_cache(maxsize=128)
def get_predicates():  # noqa: E501
    """get_predicates

    Get a list of predicates used in statements issued by the knowledge source  # noqa: E501


    :rtype: List[BeaconPredicate]
    """
    response = requests.get('http://biothings.io/explorer/api/v2/knowledgemap')

    predicates = []

    if response.ok:
        data = response.json()

        s = set()
        for a in data['associations']:
            s.add(safe_get(a, 'predicate'))

        for p in s:
            if p == p.lower():
                predicates.append(BeaconPredicate(edge_label=p))
            else:
                predicates.append(BeaconPredicate(relation=p))

    return predicates
