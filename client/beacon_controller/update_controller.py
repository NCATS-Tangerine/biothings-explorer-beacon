import requests

from swagger_server.models.beacon_statement import BeaconStatement
from swagger_server.models.beacon_statement_with_details import BeaconStatementWithDetails
from swagger_server.models.beacon_statement_object import BeaconStatementObject
from swagger_server.models.beacon_statement_predicate import BeaconStatementPredicate
from swagger_server.models.beacon_statement_subject import BeaconStatementSubject

from beacon_controller.utils import safe_get, lookup_category

_uri_pattern = 'http://biothings.io/explorer/api/v2/semanticquery?input_prefix={input_prefix}&output_prefix={output_prefix}&input_value={input_value}'

def update(
    index,
    input_prefix,
    output_prefix,
    input_value=None,
    subject_category=None,
    object_category=None,
    predicate=None
    ):

    try:
        index = int(index)
    except:
        raise Exception('Index "{}" is not a string'.format(index))

    uri = _uri_pattern.format(
        input_prefix=input_prefix,
        output_prefix=output_prefix,
        input_value=input_value
    )

    response = requests.get(uri)

    if response.ok:
        data = response.json()
    else:
        raise Exception('URI {} responsed with status code {}'.format(uri, response.status_code))

    mappings = data['data']

    if len(mappings) <= index:
        raise Exception('Tried to access index {} when there are only {} many'.format(index, len(mappings)))

    mapping = mappings[index]

    if len(mapping) < 1:
        raise Exception('The semantic query at {} is empty'.format(index))

    subject_id = safe_get(mapping[0], 'input')
    object_id = safe_get(mapping[-1], 'output', 'object', 'id')
    object_secondary_id = safe_get(mapping[-1], 'output', 'object', 'secondary-id')

    e = {
        'subject_id' : safe_get(mapping[0], 'input'),
        'object_id' : safe_get(mapping[-1], 'output', 'object', 'id'),
        'predicate' : predicate
    }


    return {'apis' : mapping, 'example' : e, 'uri' : uri}
