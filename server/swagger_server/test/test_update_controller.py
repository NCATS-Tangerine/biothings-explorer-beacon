# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.update_response import UpdateResponse  # noqa: E501
from swagger_server.test import BaseTestCase


class TestUpdateController(BaseTestCase):
    """UpdateController integration test stubs"""

    def test_update(self):
        """Test case for update

        
        """
        query_string = [('input_prefix', 'input_prefix_example'),
                        ('output_prefix', 'output_prefix_example'),
                        ('input_value', 'input_value_example'),
                        ('subject_category', 'subject_category_example'),
                        ('object_category', 'object_category_example'),
                        ('predicate', 'predicate_example')]
        response = self.client.open(
            '//update/{index}'.format(index='index_example'),
            method='POST',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
