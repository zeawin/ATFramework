# -*- coding: utf-8 -*-

"""
Effect : Test set xml tags defined
"""

import collections

# test set tags
TEST_SET_NAME_SPACE = collections.namedtuple(
    'TEST_SET', (
        'TEST_SET', 'OPT', 'DOC_TYPE', 'VERSION'
    )
)

TEST_SET = TEST_SET_NAME_SPACE('test_set', 'opt', 'doc_type', 'version')

# test case tags
TEST_NAME_SPACE = collections.namedtuple(
    'TEST', (
        'TESTS', 'TEST', 'TYPE', 'NAME', 'VALUE', 'PARAM', 'PARAMETERS',
        'ID', 'LOCATION',  'IDENTITY', 'IDENTITIES'
    )
)
TEST_PARAM = TEST_NAME_SPACE(
    'tests', 'test', 'type', 'name', 'value', 'param', 'parameters',
    'id', 'location', 'identity', 'identities'
)