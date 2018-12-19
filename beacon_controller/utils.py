"""
These are utility methods that can be used within the controller methods to
parse the json responses from the various knowledge sources. Each knowledge
source returns a different json structured response, and we do not want our
response parser to be agnostic about which knowledge source we're retreiving.
These methods are fallible heuristics for pulling the relevant information out
of those variable responses.
"""

import requests
from typing import List
from flask import abort

from beacon_controller import biolink_model as blm

bioentities_endpoint = 'http://biothings.io/explorer/api/v2/metadata/bioentities'

_category_map = None

def lookup_category(prefix:str) -> str:
    """
    Returns the category that this prefix belongs to
    """
    global _category_map

    if _category_map == None:
        response = requests.get(bioentities_endpoint)

        if response.ok:
            _category_map = {}
            data = response.json()
            for category, prefixes in data['bioentity'].items():
                for prefix in prefixes:
                    _category_map[prefix.lower()] = category
        else:
            abort(500, 'Could not connect to: {}'.format(bioentities_endpoint))

    category = _category_map.get(prefix.lower())

    if category in blm.schema().classes:
        return category
    else:
        return blm.DEFAULT_CATEGORY

bioentities = None
kmap = None

def load_bioentities() -> dict:
    global bioentities

    if bioentities is None:
        bioentities = requests.get('http://biothings.io/explorer/api/v2/metadata/bioentities').json()

    return bioentities

def load_kmap() -> dict:
    global kmap

    if kmap is None:
        kmap = requests.get('http://biothings.io/explorer/api/v2/knowledgemap').json()

    return kmap

def fix_curie(curie:str) -> str:
    """
    Biothings explorer has some very weird curie prefixes, like "HP:HP:0012092"
    and "MESH.DISEASE:ICD10CM:E11.8". This method chooses the first prefix that
    appears in the response of the bioentities endpoint. If it can't fix the
    curie then it returns it.

    Example:
    fix_curie("HP:HP:0012092")
    >>> "hp:0012092"
    fix_curie("MESH.DISEASE:ICD10CM:E11.8")
    >>> "mesh.disease:E11.8"
    """
    components = curie.split(':')

    bioentities = load_bioentities()['bioentity']

    if len(components) == 2:
        return curie
    else:
        local_id = components.pop(-1)
        for prefix in components:
            prefix = prefix.lower()
            for category, prefixes in bioentities.items():
                if prefix in prefixes:
                    return f'{prefix.upper()}:{local_id}'
        else:
            return curie

def simplify_curie(curie:str) -> str:
    """
    Ensures that there are no duplicate components in the curie. Biothings
    explorer has a bug where curies appear like: HP:HP:0001959, when it should
    just be HP:0001959.
    """
    if curie is None:
        return None
    else:
        components = curie.split(':')
        unique_components = [c for i, c in enumerate(components) if c not in components[:i]]
        return ':'.join(unique_components)

def safe_get(d:dict, *vkeys) -> object:
    """
    Chains together multiple dict.get calls safely, returning None if they
    cannot be performed.

    >> d = {'x' : {'y' : 'z'}}
    >> safe_get(d, 'x', 'y')
    'z'
    """
    try:
        for key in vkeys:
            d = d.get(key)
        return d
    except:
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

# @deprecated
def is_object(obj):
    """
    A json object will be an object if it has a:
        - id
        - name (or label)

    *Remember, we're assuming the category from the endpoint used.

    If a json object contains keys that contain all three fields, then it will
    be chosen. We also want to extract these values (as well as others, e.g.
    a description if possible). If there are multiple keys that contain the term
    "name", then we will take the shortest match. E.g. between keys:
        - "chebi_name"
        - "iupac_names"
    we will take "chebi_name".
    """
    if isinstance(obj, dict):
        is_identified = any('id' in k.lower() for k in obj.keys())
        is_named = any('name' in k.lower() for k in obj.keys())

        return is_identified and is_named
    else:
        return False

# @deprecated
def collect_objects(obj, identifiers=('id', '_id')):
    """
    Recursively searches for the highest level json objects containing a given
    identifier as a key, and returns them all. This is intended to cut through
    extra metadata in json responses that do not contain identified objects.

    Note: In the future should we require that identifiers not only be strings
          but also be curies? A number of the knowledge sources do not work with
          curies, though.
    """
    if isinstance(obj, (list, tuple, set)):
        generator = (collect_objects(item, identifiers) for item in obj)
        return [item for item in generator if item != None and item != []]
    elif isinstance(obj, dict):
        if is_object(obj):
            return obj
        else:
            for key, value in obj.items():
                result = collect_objects(value, identifiers)
                if result != None and result != []:
                    return result
    return []

# @deprecated
def get_recursive(d, key, default=None):
    """
    Gets the value of the highest level key in a json structure.

    key can be a list, will match the first one
    """
    if isinstance(key, (list, tuple, set)):
        for k in key:
            value = get_recursive(d, k)
            if value != None:
                return value
    else:
        if isinstance(d, dict):
            return d[key] if key in d else get_recursive(list(d.values()), key)

        elif isinstance(d, (list, tuple, set)):
            for item in d:
                value = get_recursive(item, key)
                if value != None:
                    return value

    return default
