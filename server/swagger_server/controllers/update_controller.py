import connexion
import six

from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501
from swagger_server import util

import beacon_controller

def update(index, input_prefix, output_prefix, input_value=None, subject_category=None, object_category=None, predicate=None):  # noqa: E501
    """update

    Allows the user to annotate an identifier mapping with semantic data  # noqa: E501

    :param index: The index of the semantic query (http://biothings.io/explorer/api/v2/semanticquery?input_prefix&#x3D;{prefix}&amp;output_prefix&#x3D;{prefix}&amp;input_value&#x3D;{value}) to annotate
    :type index: str
    :param input_prefix:
    :type input_prefix: str
    :param output_prefix:
    :type output_prefix: str
    :param input_value:
    :type input_value: str
    :param subject_category:
    :type subject_category: str
    :param object_category:
    :type object_category: str
    :param predicate:
    :type predicate: str

    :rtype: InlineResponse200
    """
    return beacon_controller.update(index, input_prefix, output_prefix, input_value, subject_category, object_category, predicate)
