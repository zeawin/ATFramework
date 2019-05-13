# -*- coding: utf-8 -*-

"""
Effect :
"""

import collections


def convertToUtf8(data):
    """trans string to utf-8 codec
    """
    if isinstance(data, basestring):
        return data.encode('utf-8')
    elif isinstance(data, collections.Mapping):
        return dict(map(convertToUtf8, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convertToUtf8, data))
    return data