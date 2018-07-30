"""
Ideas:

I am using 'http://mychem.info/v1/query?q=keyword&dotfield=true' for a general
keyword query. This appears to return cliques of concepts. Some of those concepts
have identifiers and names, some do not. But everything can be presumed to be
a chemical, seemingly a drug.

Each overarching clique has an ID that can be plugged into mychem to get this
data. The sub-responses that their own id and name should be saved to the
database as their own node. But those that do not should simply have all their
data dumped into the main mychem node.

pubchem, for example, does not appear to ever give ids or names. And ndc does but
it's "ndc.nonproprietaryname"

"""

import requests
from collections import defaultdict

def get_best_key(substring:str, d:dict):
    optimal = []
    size = float('inf')
    for k, v in d.items():
        keys = k.split('.')
        if (substring == keys[-1] or '_{}'.format(substring) in keys[-1]) and isinstance(v, str):
            if len(keys) < size:
                optimal = [k]
                size = len(keys)
            elif len(keys) == size:
                optimal.append(k)
                size = len(keys)

    size = float('inf')
    best_key = None
    for k in optimal:
        if len(k) < size:
            best_key = k
            size = len(k)

    return best_key


def get(q):
    uri = 'http://mychem.info/v1/query?q={}&dotfield=true'.format(q)
    response = requests.get(uri).json()

    results = []

    for hit in response['hits']:
        _id = hit.pop('_id')
        score = hit.pop('_score')

        d = defaultdict(dict)
        for key, value in hit.items():
            source = key.split('.')[0]
            d[source][key] = value

        results.append(d)

    for source_dict in results:
        for source, d in source_dict.items():
            best_key = get_best_key('name', d)

            d['_name_key'] = best_key
            d['_name_value'] = d[best_key] if best_key != None else None

            best_key = get_best_key('id', d)

            d['_id_key'] = best_key
            d['_id_value'] = d[best_key] if best_key != None else None

    return results
