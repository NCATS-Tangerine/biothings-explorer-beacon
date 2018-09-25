from swagger_server.models.beacon_concept_category import BeaconConceptCategory  # noqa: E501
from swagger_server.models.beacon_knowledge_map_statement import BeaconKnowledgeMapStatement  # noqa: E501
from swagger_server.models.beacon_knowledge_map_object import BeaconKnowledgeMapObject
from swagger_server.models.beacon_knowledge_map_subject import BeaconKnowledgeMapSubject
from swagger_server.models.beacon_knowledge_map_predicate import BeaconKnowledgeMapPredicate
from swagger_server.models.beacon_predicate import BeaconPredicate  # noqa: E501

from collections import defaultdict
from functools import lru_cache
from beacon_controller.utils import safe_get

from beacon_controller import biolink_model as blm

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
            if key in blm.schema().classes:
                category_id=f'blm:{key}'
                category=key
                uri=blm.class_uri(key)
            else:
                category_id=f'blm:{blm.DEFAULT_CATEGORY}'
                category=blm.DEFAULT_CATEGORY
                uri=blm.class_uri(blm.DEFAULT_CATEGORY)

            categories.append(BeaconConceptCategory(
                id=category_id,
                category=category,
                uri=uri,
                local_category=key,
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

            k = f'{subject_category}{predicate}{object_category}'

            d[k]['subject_prefix'].add(subject_prefix)
            d[k]['object_prefix'].add(object_prefix)
            d[k]['subject_category'] = subject_category
            d[k]['object_category'] = object_category
            d[k]['predicate'] = predicate
            d[k]['endpoint'] = endpoint

        for p in d.values():
            object_category = p['object_category']
            subject_category = p['subject_category']

            if object_category not in blm.schema().classes:
                object_category = blm.DEFAULT_CATEGORY

            if subject_category not in blm.schema().classes:
                subject_category = blm.DEFAULT_CATEGORY

            if p['predicate'].replace('_', ' ') in blm.schema().slots:
                edge_label = p['predicate'].replace(' ', '_')
                relation = edge_label
            else:
                edge_label = blm.DEFAULT_EDGE_LABEL
                relation = p['predicate']


            o = BeaconKnowledgeMapObject(
                category=object_category,
                prefixes=list(p['object_prefix'])
            )
            s = BeaconKnowledgeMapSubject(
                category=subject_category,
                prefixes=list(p['subject_prefix'])
            )

            r = BeaconKnowledgeMapPredicate(
                edge_label=edge_label,
                relation=relation,
                negated=False
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
            if p.replace('_', ' ') in blm.schema().slots:
                edge_label = p.replace(' ', '_')
                predicate_id=f'blm:{edge_label}'
                relation = edge_label
                uri=blm.slot_uri(edge_label)
            else:
                predicate_id=f'blm:{blm.DEFAULT_EDGE_LABEL}'
                edge_label=blm.DEFAULT_EDGE_LABEL
                relation=p
                uri=blm.slot_uri(blm.DEFAULT_EDGE_LABEL)

            predicates.append(BeaconPredicate(
                id=predicate_id,
                edge_label=edge_label,
                relation=relation,
                uri=uri,
                local_relation=relation
            ))

    return predicates
