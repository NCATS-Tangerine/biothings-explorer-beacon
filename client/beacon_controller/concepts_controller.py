from swagger_server.models.beacon_concept import BeaconConcept  # noqa: E501
from swagger_server.models.beacon_concept_with_details import BeaconConceptWithDetails  # noqa: E501
from swagger_server.models.exact_match_response import ExactMatchResponse  # noqa: E501

from beacon_controller import utils
from beacon_controller.models import Association
from beacon_controller import mychem_client

import re, requests

uri = 'http://{base_uri}/{version}/query?q={query}&size=10'

id_pattern = re.compile('\{.*\}')

category_mapper = {
    'gene' : {
        'base_uri' : 'mygene.info',
        'version' : 'v3'
    },
    'chemical' : {
        'base_uri' : 'mychem.info',
        'version' : 'v1'
    },
    'variant' : {
        'base_uri' : 'myvariant.info',
        'version' : 'v1'
    }
}

import biothings_explorer_test as bte

def get_concept_details(conceptId):
    prefix, identifier = conceptId.split(':')
    return bte.fetch_output(
        input_prefix=prefix,
        input_value=identifier,
        output_prefix=prefix,
        enable_semantic_search=True
    )

    return mychem_client.get(conceptId)

    prefix, identifier = conceptId.split(':')

    associations = Association.concept_assocations(prefix)
    print(len(associations))
    responses = {}

    for association in associations:
        endpoint = association.endpoint
        uri = id_pattern.sub(conceptId, endpoint)

        print(uri)

        response = requests.get(uri)

        responses[endpoint] = response.json()

    return responses

def get_concepts(keywords, categories=None, size=None):
    if categories == None:
        categories = ['gene', 'chemical', 'variant']

    q = ', '.join('{}'.format(k) for k in keywords)
    results = {}
    if categories != None:
        for category in categories:
            _uri = uri.format(query=q, **category_mapper[category])
            results[_uri] = requests.get(_uri).json()

    return results

import yaml, json
import requests

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
        import pudb; pu.db

def get_value(data, endpoint, field_name):
    s = endpoint[field_name]

    if s == None:
        return None

    s = re.sub(r'(\w+|\*)', r'"\1"', s)
    parse_dict = json.loads(s)
    return parse(parse_dict, data)

def construct_statements2(**kwargs):
    statements = []
    for key, values in kwargs.items():
        for i, value in enumerate(values):
            if len(statements) < i + 1:
                statements.append({
                    key: value
                })
            else:
                statements[i][key] = value
    return statements

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






def get_exact_matches_to_concept_list(c):
    pattern = re.compile('\w+')
    with open('../endpoints.yaml', 'r') as stream:
        endpoints = yaml.load(stream)

        Y = {}

        for endpoint in endpoints:
            results = {}

            if endpoint['example'] == None: continue

            response = requests.get(endpoint['example'])

            if response.status_code != 200:
                raise Exception(endpoint.example + ' failed with code ' + str(response.status_code))

            data = response.json()

            fields = ['subject_name', 'subject_id', 'object_name', 'object_id', 'predicate', 'statement_id']

            for field in fields:
                results[field] = get_value(data, endpoint, field)

            Y[endpoint['example']] = construct_statements(results)

        return Y
