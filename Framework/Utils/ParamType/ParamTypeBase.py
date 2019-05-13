# -*- coding: utf-8 -*-

"""
Effect:
"""
import re

from Framework.Utils.Validate import validate
from Framework.Exception import ATException


class ParamTypeBase(object):
    def __init__(self, typeAndValidation):
        super(ParamTypeBase, self).__init__()
        self.validation = None
        if 'validation' in typeAndValidation:
            self.validation = typeAndValidation['validation']
        self.name = typeAndValidation['type']

    def hasValidation(self):
        """Check whether this parameter has 'validation'
        """
        return False

    def getValidation(self):
        """To get this parameter 'validation'
        """
        return None

    def getValidationValues(self):
        """To get this parameter 'validation'.'valid_values'
        """
        return None

    def getValidInput(self, defauled):
        """
        """
        pass


def __boolean(inputs):
    """Generate a Boolean instance
    """
    from Framework.Utils.ParamType.Boolean import Boolean
    return Boolean(inputs)


def __ipAddress(inputs):
    """Generate a Boolean instance
    """
    from Framework.Utils.ParamType.IPAddress import IPAddress
    return IPAddress(inputs)


def __time(inputs):
    """Generate a Boolean instance
    """
    from Framework.Utils.ParamType.Time import Time
    return Time(inputs)

def __size(inputs):
    """Generate a Boolean instance
    """
    from Framework.Utils.ParamType.Size import Size
    return Size(inputs)


def __select(*args):
    """Generate a Boolean instance
    """
    from Framework.Utils.ParamType.Select import Select
    return Select(*args)


@validate(inputs=dict)
def create(inputs):
    """create ParamTypeBase sub class instance
    """
    if 'type' not in inputs:
        raise ATException('Create ParamType object failed')

    typeName = inputs['type'].lower()

    isMultiple = False

    multipleRGX = 'multiple_(ip_address|boolean|time|select|size)$'

    if re.match(multipleRGX, typeName):
        typeName = re.sub('multiple_', '', typeName)
        isMultiple = True
        inputs['type'] = typeName

    paramType = {
        'boolean': __boolean,
        'ip_address': __ipAddress,
        'time': __time,
        'select': __select,
        'size': __size
    }
    typeObjFunc = paramType[typeName]
    if typeName not in paramType:
        raise ATException('Create ParamType object failed')

    if isMultiple is True:
        from Framework.Utils.ParamType.MultpleThing import MultipleThing

        mutipleParam = {
            'factory_method': typeObjFunc,
            'type': typeName
        }
        if 'validation' in inputs:
            mutipleParam['validation'] = inputs['validation']
        typeObj = MultipleThing(mutipleParam)
    else:
        typeObj = typeObjFunc(inputs)

    return typeObj
