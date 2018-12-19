from swagger_server.models.beacon_concept import BeaconConcept  # noqa: E501
from swagger_server.models.beacon_concept_with_details import BeaconConceptWithDetails  # noqa: E501
from swagger_server.models.exact_match_response import ExactMatchResponse  # noqa: E501

from beacon_controller.utils import safe_get, lookup_category, fix_curie
from beacon_controller import crawler

import re, requests, yaml, json

def get_concept_details(conceptId):
    data = crawler.crawl(conceptId)

    if data == {}:
        return BeaconConceptWithDetails()

    names, descriptions, xrefs = [], [], []

    for category, associations in data.items():
        for a in associations:
            predicate = a.get('predicate')
            if predicate == 'EquivalentAssociation' or predicate == 'HasDescriptionAssociation':
                object_id = safe_get(a, 'object', 'id')
                prefix, local_id = object_id.split(':', 1)

                if 'name' in prefix.lower() or 'symbol' in prefix.lower():
                    names.append(local_id)
                if 'description' in prefix.lower():
                    descriptions.append(local_id)
                if not 'name' in prefix.lower() and not 'description' in prefix.lower():
                    xrefs.append(fix_curie(object_id))

    names = list(set(names))
    predicate_longest_under_sixty = lambda n: (len(n) > 60, -len(n))
    names.sort(key=predicate_longest_under_sixty)

    prefix, _ = conceptId.split(':', 1)

    c = BeaconConceptWithDetails(
        id=fix_curie(conceptId),
        name=names[0] if len(names) >= 1 else None,
        synonyms=names[1:],
        exact_matches=xrefs,
        categories=[lookup_category(prefix)],
        description='; '.join(descriptions)
    )

    return c

def get_concepts(keywords, categories=None, offset=None, size=None):
    return []

def get_exact_matches_to_concept_list(c):
    response = []

    for curie in c:
        if not isinstance(curie, str) or ':' not in curie:
            continue

        exact_matches = []

        data = crawler.crawl(curie)

        for category, associations in data.items():
            for a in associations:
                if a.get('predicate') == 'EquivalentAssociation':
                    object_id = safe_get(a, 'object', 'id')

                    prefix, local_id = object_id.split(':', 1)

                    if 'name' not in prefix.lower():
                        exact_matches.append(fix_curie(object_id))

        response.append(ExactMatchResponse(
            id=curie,
            within_domain=data != {},
            has_exact_matches=exact_matches
        ))

    return response
