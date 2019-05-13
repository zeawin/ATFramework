# -*- coding: utf-8 -*-

"""
    Effect: The log enum
"""

import collections

ConsoleLogLevelEnum = collections.namedtuple(
    'ConsoleLogLevel', ('Trace', 'Debug', 'Info', 'Main', 'Error')
)
LogTypeEnum = collections.namedtuple(
    'LogType', ('PreTestSet', 'PostTestSet', 'TestCase', 'Main')
)
FileLogLevelEnum = collections.namedtuple(
    'FileLogLevel', (
        'Trace', 'TcStatus', 'TcStep', 'TcStart', 'Section', 'TcEnd', 'PreSet', 'PostSet', 'Debug', 'Cmd', 'CmdResponse',
        'Info', 'Warn', 'Error', 'ConfigError', 'Fail', 'PassInfo'
    )
)
ConsoleLogLevel = ConsoleLogLevelEnum(0, 10, 20, 30, 40)
LogType = LogTypeEnum('Pre_TestSet', 'Post_TestSet', 'TestCase', 'Main')
FileLogLevel = FileLogLevelEnum(1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 20, 30, 40, 41, 42, 43)