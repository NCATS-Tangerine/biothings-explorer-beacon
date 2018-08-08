import re, requests, yaml, json

from swagger_server.models.beacon_statement import BeaconStatement
from swagger_server.models.beacon_statement_with_details import BeaconStatementWithDetails
from swagger_server.models.beacon_statement_object import BeaconStatementObject
from swagger_server.models.beacon_statement_predicate import BeaconStatementPredicate
from swagger_server.models.beacon_statement_subject import BeaconStatementSubject

from beacon_controller import utils

from typing import List
from collections import defaultdict

from beacon_controller.utils import safe_get
from beacon_controller import crawler

def get_statement_details(statementId, keywords=None, size=None):
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

def get_statements(s, edge_label=None, relation=None, t=None, keywords=None, categories=None, size=None, enforce_biolink_model=None, ignore_incomplete_data=None):  # noqa: E501
    statements = []

    for subject_id in s:
        data = crawler.crawl(subject_id)

        if data == {}:
            continue

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
                        if 'name' in object_prefix.lower():
                            subject_names.append(object_local_id)

        predicate_longest_under_sixty = lambda n: (len(n) > 60, -len(n))
        subject_names.sort(key=predicate_longest_under_sixty)

        subject_name = None if len(subject_names) == 0 else subject_names[0]

        prefix, _ = subject_id.split(':', 1)
        for category, associations in data.items():
            if 'name' in prefix.lower() or 'description' in prefix.lower():
                continue

            category = None if category == "null" else category

            if object_name == None:
                taxonomy = safe_get(a, 'object', 'taxonomy')
                secondary_id = safe_get(a, 'object', 'secondary-id')
                symbol = secondary_id.split(':', 1)[1] if secondary_id != None and ':' in secondary_id else None

                if symbol != None:
                    if taxonomy != None and len(taxonomy) >= 0:
                        taxonomy = ', '.join(t for t in taxonomy if ':' not in t)
                        object_name = '{} ({})'.format(taxonomy)
                    else:
                        object_name = symbol

            for a in associations:
                beacon_subject = BeaconStatementSubject(
                    id=subject_id,
                    name=subject_name,
                    category=utils.lookup_category(prefix)
                )

                object_id = safe_get(a, 'object', 'id')
                if object_id != None and ':' in object_id:
                    object_prefix, _ = object_id.split(':', 1)
                    object_prefix = object_prefix.lower()
                    if 'name' in object_prefix or 'description' in object_prefix:
                        continue

                beacon_object = BeaconStatementObject(
                    id=object_id,
                    name=safe_get(a, 'object', 'label'),
                    category=category
                )

                edge_label = safe_get(a, 'edge', 'label')
                if edge_label == None:
                    edge_label = safe_get(a, 'predicate')
                if edge_label == 'EquivalentAssociation':
                    edge_label = 'same as'
                edge_label = edge_label.replace(' ', '_')

                beacon_predicate = BeaconStatementPredicate(
                    edge_label=edge_label,
                    relation=safe_get(a, 'edge', 'id'),
                    negated=None
                )

                beacon_statement = BeaconStatement(
                    id=None,
                    source=None,
                    subject=beacon_subject,
                    predicate=beacon_predicate,
                    object=beacon_object
                )

                statements.append(beacon_statement)

    return statements

def get_statements2(s, edge_label=None, relation=None, t=None, keywords=None, categories=None, size=None):
    biothings_apis = get_apis(sources=s, targets=t, relation=relation, categories=categories)

    for api in biothings_apis:
        parser = json_parser.Parser('../endpoints.yaml')
        records = parser.perform_requst_and_parse_response(api['endpoint'], )

    with open('../endpoints.yaml', 'r') as stream:
        endpoint_mappings = yaml.load(stream)
        endpoint_mappings = {e['uri'] : e for e in endpoint_mappings}

    biothings_apis = get_apis(sources=s, targets=t, relation=relation, categories=categories)

    statements = []
    used_endpoints = []

    for global_id in s:
        prefix, local_id = global_id.split(':', 1)
        for api in biothings_apis:
            if api['subject']['prefix'] == prefix.lower() and api['endpoint'] not in used_endpoints:
                used_endpoints.append(api['endpoint'])
                if not api['endpoint'].startswith('http://mydisease.info/v1/disease/'):
                    continue

                try:
                    response, response_uri = perform_get_request(api['endpoint'], global_id)
                except Exception as e:
                    print(e)
                    continue

                mapping = endpoint_mappings[api['endpoint']]
                results = {}
                for key, decoder in mapping.items():
                    if key == 'uri' or key == 'example':
                        continue
                    results[key] = get_value(response.json(), decoder)

                if results['subject_id'] == None:
                    results['subject_id'] = global_id

                results['subject_category'] = api['subject']['semantic_type']
                results['object_category'] = api['object']['semantic_type']

                if results['predicate'] == None:
                    results['predicate'] = api['predicate']

                results['source_uri'] = response_uri
                s = construct_statements(results)
                statements.extend(s)

    if size != None:
        statements = statements[:size]
