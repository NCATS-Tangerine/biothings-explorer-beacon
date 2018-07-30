import re, requests, yaml, json

from swagger_server.models.beacon_statement import BeaconStatement
from swagger_server.models.beacon_statement_with_details import BeaconStatementWithDetails
from swagger_server.models.beacon_statement_object import BeaconStatementObject
from swagger_server.models.beacon_statement_predicate import BeaconStatementPredicate
from swagger_server.models.beacon_statement_subject import BeaconStatementSubject

from beacon_controller import utils
from beacon_controller.models import Association

from typing import List
from collections import defaultdict

def get_statement_details(statementId, keywords=None, size=None):
    from biothings_explorer_test import MetaData
    metadata = MetaData()
    return metadata.list_all_api_resources()

    from biothings_explorer import BioThingsExplorer

    b = BioThingsExplorer()

    x = b.show_available_bioentities()

    return None

def get_apis(sources:List[str], targets:List[str]=None, relation:str=None, categories:List[str]=None):
    """
    Returns the API's that fulfill the given search constraints
    """

    pattern = re.compile('\{.*\}')

    from biothings_explorer_test import APILocator
    locator = APILocator()

    source_apis = []

    for source_id in sources:
        prefix, identifier = source_id.split(':', 1)
        source_apis.extend(locator.locate_apis_by_input_prefix_only(input_prefix=prefix.lower()))

    if categories != None:
        source_apis = [a for a in source_apis if a['object']['semantic_type'] in categories]

    if relation != None:
        source_apis = [a for a in source_apis if a['predicate'] == relation]

    if targets != None:
        target_prefixes = [t.split(':')[0].lower() for t in targets if ':' in t]
        source_apis = [a for a in source_apis if a['object']['prefix'] in target_prefixes]

    return source_apis

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

def parse(parse_dict, data):
    if isinstance(parse_dict, dict):
        key = list(parse_dict.keys())[0]
        return parse(parse_dict[key], data[key])
    elif isinstance(parse_dict, list):
        return [parse(parse_dict[0], item) for item in data]
    elif isinstance(parse_dict, str):
        if parse_dict == '*':
            if isinstance(data, list):
                return ', '.join(data)
            elif isinstance(data, str):
                return data
            else:
                return str(data)
    else:
        raise Exception('could not parse {} with {}'.format(data, parse_dict))

def get_value(data, endpoint, field_name):
    s = endpoint[field_name]

    if s == None:
        return None

    s = re.sub(r'(\w+|\*)', r'"\1"', s)
    parse_dict = json.loads(s)
    return parse(parse_dict, data)

def construct_statements(d):
    def _construct_statements(d):
        statements = []
        flat_dict = {}
        for key, value in d.items():
            if not isinstance(value, list):
                flat_dict[key] = value
                continue

            for i, item in enumerate(value):
                if len(statements) < i + 1:
                    statements.append({
                        key: item
                    })
                else:
                    statements[i][key] = item

        for statement in statements:
            statements.extend(_construct_statements(statement))

        for statement in statements:
            for key, value in flat_dict.items():
                statement[key] = value

        return [s for s in statements if not any(isinstance(value, list) for value in s.values())]

    if all(not isinstance(value, list) for value in d.values()):
        return [d]
    else:
        return _construct_statements(d)

def get_statements(s, edge_label=None, relation=None, t=None, keywords=None, categories=None, size=None):
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

                try:
                    response, response_uri = perform_get_request(api['endpoint'], global_id)
                except Exception as e:
                    print(e)
                    continue

                fields = ['subject_name', 'subject_id', 'object_name', 'object_id', 'predicate', 'statement_id']
                results = {}
                endpoint = endpoint_mappings[api['endpoint']]
                for field in fields:
                    results[field] = get_value(response.json(), endpoint, field)

                if results['subject_id'] == None:
                    results['subject_id'] = global_id

                results['subject_category'] = api['subject']['semantic_type']
                results['object_category'] = api['object']['semantic_type']

                if results['predicate'] == None:
                    results['predicate'] = api['predicate']

                results['source_uri'] = response_uri
                s = construct_statements(results)
                for ss in s:
                    if ':' not in ss['object_id']:
                        ss['object_id'] = '{}:{}'.format(api['object']['prefix'], ss['object_id'])
                statements.extend(s)

    if size != None:
        statements = statements[:size]

    beacon_statements = []
    for statement in statements:
        beacon_subject = BeaconStatementSubject(
            id=statement['subject_id'],
            name=statement['subject_name'],
            category=statement['subject_category']
        )

        beacon_object = BeaconStatementObject(
            id=statement['object_id'],
            name=statement['object_name'],
            category=statement['object_category']
        )

        beacon_predicate = BeaconStatementPredicate(
            edge_label=statement['predicate'],
            relation=statement['predicate'],
            negated=None
        )

        beacon_statement = BeaconStatement(
            id=statement['statement_id'],
            subject=beacon_subject,
            predicate=beacon_predicate,
            object=beacon_object
        )

        beacon_statements.append(beacon_statement)

    return beacon_statements
