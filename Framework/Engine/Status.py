# -*- coding: utf-8 -*-

"""
Effect : Define case status
"""
import collections

# difined custom role
STATUS = collections.namedtuple(
    'STATUS', (
        'RUNNING', 'COMPLETE', 'PASS', 'FAILED', 'INCOMPLETE', 'NOT_RUN', 'CONFIG_ERROR', 'CONFIGURED', 'KILLED',
        'DE_CONFIGURED'
    )
)
TEST_STATUS = STATUS(
    'RUNNING', 'COMPLETE', 'PASS', 'FAILED', 'INCOMPLETE', 'NOT_RUN', 'CONFIG_ERROR', 'CONFIGURED', 'KILLED',
    'DECONFIGURED'
)

STATUS_UNITS = (
    TEST_STATUS.RUNNING, TEST_STATUS.COMPLETE, TEST_STATUS.PASS, TEST_STATUS.FAILED, TEST_STATUS.INCOMPLETE,
    TEST_STATUS.NOT_RUN, TEST_STATUS.CONFIG_ERROR, TEST_STATUS.CONFIGURED, TEST_STATUS.KILLED, TEST_STATUS.DE_CONFIGURED
)