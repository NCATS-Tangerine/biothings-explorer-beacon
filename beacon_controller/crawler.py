import requests
import logging

from typing import Dict, List
from functools import lru_cache

from flask import abort

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_uri_pattern = 'http://biothings.io/explorer/api/v2/crawler?input_type={prefix}&input_value={local_id}'

@lru_cache(maxsize=128)
def crawl(curie:str) -> Dict[str, List[dict]]:
    """
    Retreives a dictionary mapping categories onto a list of associations that
    involve the given CURIE identifier.

    :param curie: a CURIE identifier of concept of interest
    """
    prefix, local_id = curie.split(':', 1)
    uri = _uri_pattern.format(prefix=prefix.lower(), local_id=local_id)

    response = requests.get(uri)

    if response.ok:
        data = response.json()
        return data['linkedData']
    else:
        abort(500, 'Could not connect to: {}'.format(uri))
