import re, requests, yaml, json

from swagger_server.models.beacon_statement import BeaconStatement
from swagger_server.models.beacon_statement_with_details import BeaconStatementWithDetails
from swagger_server.models.beacon_statement_annotation import BeaconStatementAnnotation
from swagger_server.models.beacon_statement_object import BeaconStatementObject
from swagger_server.models.beacon_statement_predicate import BeaconStatementPredicate
from swagger_server.models.beacon_statement_subject import BeaconStatementSubject

from beacon_controller import utils

from typing import List
from collections import defaultdict

from beacon_controller.utils import safe_get, simplify_curie
from beacon_controller import crawler

def get_statement_details(statementId, keywords=None, size=None):
    if ':' not in statementId:
        return BeaconStatementWithDetails()

    p = statementId.split(':')

    if len(p) != 5:
        return BeaconStatementWithDetails()

    subject_id = '{}:{}'.format(p[0], p[1])
    predicate = '{}'.format(p[2])
    object_id = '{}:{}'.format(p[3], p[4])

    data = crawler.crawl(subject_id)

    for category, assocations in data.items():
        for a in assocations:
            object_match = object_id == simplify_curie(safe_get(a, 'object', 'id'))
            predicate_match = predicate == safe_get(a, 'predicate')

            edge_label = safe_get(a, 'edge', 'label')
            if edge_label is not None:
                edge_label = edge_label.replace(' ', '_')
                predicate = predicate.replace(' ', '_')

            label_match = predicate == edge_label

            if object_match and (label_match or predicate_match):
                provided_by = safe_get(a, 'edge', 'provided_by')
                probability = safe_get(a, 'edge', 'probability')
                predicate = safe_get(a, 'predicate')
                is_defined_by = safe_get(a, 'api')
                endpoint = safe_get(a, 'endpoint')

                annotations = []

                if probability is not None:
                    annotations.append(BeaconStatementAnnotation(tag='probability', value=probability))
                if predicate is not None:
                    annotations.append(BeaconStatementAnnotation(tag='predicate', value=predicate))
                if endpoint is not None:
                    annotations.append(BeaconStatementAnnotation(tag='endpoint', value=endpoint))
                    annotations.append(BeaconStatementAnnotation(tag='endpoint_input', value=subject_id))

                return BeaconStatementWithDetails(
                    provided_by=provided_by,
                    is_defined_by=is_defined_by,
                    annotation=annotations
                )

    return BeaconStatementWithDetails()


def perform_get_request(uri_pattern, identifier):
    pattern = re.compile('\{.*\}')

    uri = pattern.sub(identifier, uri_pattern)
    response = requests.get(uri)

    if response.status_code != 200:
        prefix, local_id = identifier.split(':', 1)

        uri = pattern.sub(identifier, uri_pattern)
        response = requests.get(uri)

        if response.status_code != 200:
            raise Exception(
                "URI pattern '{}' could not be resolved with identifier {}, status code: {}".format(uri_pattern, identifier, response.status_code)
            )

    return response, uri

def find_subject_name(data:dict):
    subject_names = []
    for category, associations in data.items():
        for a in associations:
            if a.get('predicate') == 'EquivalentAssociation':
                object_id = safe_get(a, 'object', 'id')
                object_name = safe_get(a, 'object', 'label')

                if object_name != None:
                    subject_names.append(object_name)

                else:
                    object_prefix, object_local_id = object_id.split(':', 1)
                    if 'name' in object_prefix.lower() or 'symbol' in object_prefix.lower():
                        subject_names.append(object_local_id)

    predicate_longest_under_sixty = lambda n: (len(n) > 60, -len(n))

    subject_names.sort(key=predicate_longest_under_sixty)

    return next((name for name in subject_names), None)

def build_statement(
    object_id,
    object_name,
    object_category,
    subject_id,
    subject_name,
    subject_category,
    predicate_id,
    predicate_name
    ):
    beacon_subject = BeaconStatementSubject(
        id=subject_id,
        name=subject_name,
        categories=[subject_category]
    )
    beacon_object = BeaconStatementObject(
        id=object_id,
        name=object_name,
        categories=[object_category]
    )
    beacon_predicate = BeaconStatementPredicate(
        edge_label=predicate_name,
        relation=predicate_id,
        negated=None
    )
    statement_id = '{}:{}:{}'.format(subject_id, predicate_name, object_id)
    return BeaconStatement(
        id=statement_id,
        subject=beacon_subject,
        predicate=beacon_predicate,
        object=beacon_object
    )

def lower(s:str):
    if isinstance(s, str):
        return s.lower()
    else:
        return None

def apply_filters(statements, edge_label=None, relation=None, t=None, keywords=None, categories=None):
    results = []
    for statement in statements:
        o = statement.object
        p = statement.predicate

        if t != None and not any(lower(o.id) == lower(target_id) for target_id in t):
            continue

        if categories != None and not any(lower(o.category) == lower(category) for category in categories):
            continue

        if keywords != None:
            if o.name == None or not any(lower(keyword) in lower(o.name) for keyword in keywords):
                continue

        if relation != None and lower(p.relation) != lower(relation):
            continue

        if edge_label != None and lower(p.edge_label) != lower(edge_label):
            continue

        results.append(statement)

    return results

def remove_duplicates(l:list):
    """
    This method can remove duplicates for lists of objects that implement _eq_
    but do not implement _hash_. For such cases l = list(set(l)) wont work.
    """
    return [obj for index, obj in enumerate(l) if obj not in l[index + 1:]]

def get_statements(s, edge_label=None, relation=None, t=None, keywords=None, categories=None, size=None, enforce_biolink_model=None, ignore_incomplete_data=None):  # noqa: E501
    statements = []

    for subject_id in s:
        if ':' not in subject_id:
            continue

        data = crawler.crawl(subject_id)

        if data == {}:
            continue

        subject_name = find_subject_name(data)

        for category, associations in data.items():
            if category == 'null':
                category = None

            for a in associations:
                object_id = safe_get(a, 'object', 'id')
                if object_id != None and ':' in object_id:
                    object_prefix, _ = object_id.split(':', 1)
                    object_prefix = object_prefix.lower()
                    if 'name' in object_prefix or 'description' in object_prefix:
                        continue

                object_name = safe_get(a, 'object', 'label')
                if object_name == None:
                    secondary_id = safe_get(a, 'object', 'secondary-id')
                    if secondary_id != None and ':' in secondary_id:
                        secondary_prefix, symbol = secondary_id.split(':', 1)
                        object_name = symbol
                        if 'symbol' in secondary_prefix.lower():
                            taxonomy = safe_get(a, 'object', 'taxonomy')
                            if taxonomy != None:
                                taxonomy = ', '.join(t for t in taxonomy if ':' not in t)
                                object_name += ' (taxonomy: {})'.format(taxonomy)

                subject_prefix, _ = subject_id.split(':', 1)

                predicate_name = safe_get(a, 'edge', 'label')
                if predicate_name == None:
                    predicate_name = safe_get(a, 'predicate')
                if predicate_name == 'EquivalentAssociation':
                    predicate_name = 'same_as'
                predicate_name = predicate_name.replace(' ', '_')

                object_id = simplify_curie(object_id)
                subject_id = simplify_curie(subject_id)

                statements.append(build_statement(
                    object_id=object_id,
                    object_name=object_name,
                    object_category=category,
                    subject_id=subject_id,
                    subject_name=subject_name,
                    subject_category=utils.lookup_category(subject_prefix),
                    predicate_id=safe_get(a, 'edge', 'id'),
                    predicate_name=predicate_name
                ))

    statements = apply_filters(
        statements,
        edge_label=edge_label,
        relation=relation,
        t=t,
        keywords=keywords,
        categories=categories
    )

    statements = remove_duplicates(statements)

    return statements
