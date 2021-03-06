# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class BeaconStatementPredicate(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    def __init__(self, edge_label: str=None, relation: str=None, negated: bool=None):  # noqa: E501
        """BeaconStatementPredicate - a model defined in Swagger

        :param edge_label: The edge_label of this BeaconStatementPredicate.  # noqa: E501
        :type edge_label: str
        :param relation: The relation of this BeaconStatementPredicate.  # noqa: E501
        :type relation: str
        :param negated: The negated of this BeaconStatementPredicate.  # noqa: E501
        :type negated: bool
        """
        self.swagger_types = {
            'edge_label': str,
            'relation': str,
            'negated': bool
        }

        self.attribute_map = {
            'edge_label': 'edge_label',
            'relation': 'relation',
            'negated': 'negated'
        }

        self._edge_label = edge_label
        self._relation = relation
        self._negated = negated

    @classmethod
    def from_dict(cls, dikt) -> 'BeaconStatementPredicate':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BeaconStatementPredicate of this BeaconStatementPredicate.  # noqa: E501
        :rtype: BeaconStatementPredicate
        """
        return util.deserialize_model(dikt, cls)

    @property
    def edge_label(self) -> str:
        """Gets the edge_label of this BeaconStatementPredicate.

        The predicate edge label associated with this statement, which should be as published by the /predicates API endpoint and must be taken from the minimal predicate ('slot') list of the [Biolink Model](https://biolink.github.io/biolink-model).   # noqa: E501

        :return: The edge_label of this BeaconStatementPredicate.
        :rtype: str
        """
        return self._edge_label

    @edge_label.setter
    def edge_label(self, edge_label: str):
        """Sets the edge_label of this BeaconStatementPredicate.

        The predicate edge label associated with this statement, which should be as published by the /predicates API endpoint and must be taken from the minimal predicate ('slot') list of the [Biolink Model](https://biolink.github.io/biolink-model).   # noqa: E501

        :param edge_label: The edge_label of this BeaconStatementPredicate.
        :type edge_label: str
        """

        self._edge_label = edge_label

    @property
    def relation(self) -> str:
        """Gets the relation of this BeaconStatementPredicate.

        The predicate relation associated with this statement, which should be as published by the /predicates API endpoint with the preferred format being a CURIE where one exists, but strings/labels acceptable. This relation may be equivalent to the edge_label (e.g. edge_label: has_phenotype, relation: RO:0002200), or a more specific relation in cases where the source provides more granularity (e.g. edge_label: molecularly_interacts_with, relation: RO:0002447)  # noqa: E501

        :return: The relation of this BeaconStatementPredicate.
        :rtype: str
        """
        return self._relation

    @relation.setter
    def relation(self, relation: str):
        """Sets the relation of this BeaconStatementPredicate.

        The predicate relation associated with this statement, which should be as published by the /predicates API endpoint with the preferred format being a CURIE where one exists, but strings/labels acceptable. This relation may be equivalent to the edge_label (e.g. edge_label: has_phenotype, relation: RO:0002200), or a more specific relation in cases where the source provides more granularity (e.g. edge_label: molecularly_interacts_with, relation: RO:0002447)  # noqa: E501

        :param relation: The relation of this BeaconStatementPredicate.
        :type relation: str
        """

        self._relation = relation

    @property
    def negated(self) -> bool:
        """Gets the negated of this BeaconStatementPredicate.

        (Optional) a boolean that if set to true, indicates the edge statement is negated i.e. is not true   # noqa: E501

        :return: The negated of this BeaconStatementPredicate.
        :rtype: bool
        """
        return self._negated

    @negated.setter
    def negated(self, negated: bool):
        """Sets the negated of this BeaconStatementPredicate.

        (Optional) a boolean that if set to true, indicates the edge statement is negated i.e. is not true   # noqa: E501

        :param negated: The negated of this BeaconStatementPredicate.
        :type negated: bool
        """

        self._negated = negated
