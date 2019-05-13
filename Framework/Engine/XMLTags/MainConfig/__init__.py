# -*- coding: utf-8 -*-

"""
Effect : 配置文件中的tags常量定义
"""

import collections
# mainConfig标签定义.
MAIN_CONFIG_NAMESPACE = collections.namedtuple(
    'MAIN_CONFIG', (
        'LOCAL_BASE_LOG_PATH', 'LOCAL_EXECUTION_LOG_PATH', 'PARAM', 'OPT', 'NAME', 'VALUE',
        'TEST_SET_FILE', 'TESTBED_FILE', 'EXECUTION_PARAMETERS', 'VERSTION', 'DOC_TYPE'
    )
)

MAIN_CONFIG = MAIN_CONFIG_NAMESPACE(
    'local_base_log_path', 'local_execution_log_path', 'param', 'opt', 'name', 'value',
    'test_set_file', 'testbed_file', 'execution_parameters', 'version', 'doc_type'
)

# defined workspace tags
WORKSPACE = 'workspace'