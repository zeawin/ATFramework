# -*- coding: utf-8 -*-

"""
Effect : public resource such as function
"""
from Framework.Exception import ATException


def listMap(func, seq):
    """override map(), deal with the situation that seq(list) has list element

    Args:
        func    (function): a recursive function
        seq     (list)    : the data list
    """
    seqDict = {}
    if not hasattr(func, '__call__'):
        raise ATException('The first argument[%s] must be a function.' % 'func')
    if not isinstance(seq, list):
        raise ATException('The second argument[%s] must be a list.' % 'seq')

    def childMap(childFunc, childSeq, childDict):
        for child in childSeq:
            if isinstance(child, list):
                childMap(childFunc, childSeq, childDict)
            else:
                if not isinstance(childFunc(child), dict):
                    raise ATException('listMap() failed, the childFunc() return is not a dict.')
                childDict.update(childFunc(child))
        return childDict
    return childMap(func, seq, seqDict)