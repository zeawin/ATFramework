# -*- coding: utf-8 -*-

"""
Effect : The parameters' function of case
"""
import re

from Framework.Exception import ATException
from Framework.Utils.Validate import validate
from Framework.Utils.ParamType import ParamTypeBase

class Parameter:
    """Parameter
    Args:
        param   (dict): example follow
                        name            (str): parameter name, mandatory
                        display_name    (str): parameter displayed name, optional
                        description     (str): parameter description, optional
                        default_value   (str): parameter type, optional
                        type            (str): parameter name
                        identity        (str): parameter identity
                        assigned_value  (str): parameter name, mandatory
                        optional        (str): parameter name, mandatory
                        validation      (str): parameter name, mandatory

    """

    @validate(param=dict)
    def __init__(self, param):
        self.parameter = param

        if 'type' not in self.parameter or 'name' not in self.parameter:
            raise ATException('Parameter create failed, param: [param] do not have key [\'type\'] or [\'name\']')

        typeAndValidation = {'type': self.parameter.pop('type', None)}
        if 'validation' in self.parameter:
            typeAndValidation['validation'] = self.parameter.pop('validation', None)

        self.type = ParamTypeBase.create(typeAndValidation)
        self.parameter['type'] = self.type

        if 'default_value' in self.parameter:
            self.parameter['default_value'] = self.type.getValidInput(self.parameter['default_value'])

        if 'assigned_value' in self.parameter:
            self.parameter['assigned_value'] = self.type.getValidInput(self.parameter['assigned_value'])

        self.name = self.parameter['name']

        self.identity = None
        if 'identity' in self.parameter:
            self.identity = self.parameter['identity']

        self.displayName = None
        if 'display_name' in self.parameter:
            self.displayName = self.parameter['display_name']

        self.description = None
        if 'description' in self.parameter:
            self.description = self.parameter['description']

        self.optional = None
        if 'optional' in self.parameter:
            self.optional = self.parameter['optional']

        self.validationValues = self.type.getValidationValues()
        self.validation = self.type.getValidation()

    def isOptional(self):
        """check this parameter whether optional
        """
        if 'optional' in self.parameter:
            return self.parameter['optional']
        return False

    def hasAssignedValue(self):
        """check this parameter whether has 'assigned_value'
        """
        return 'assigned_value' in self.parameter

    def hasDefaultValue(self):
        """check this parameter whether has 'assigned_value'
        """
        return 'default_value' in self.parameter

    def getAssignedValue(self):
        """To get this parameter property named 'assigned_value'
        """
        if self.hasAssignedValue():
            return self.parameter['assigned_value']
        return None

    def getDefaultValue(self):
        """To get this parameter property named 'default_value'
        """
        if self.hasDefaultValue():
            return self.parameter['default_value']
        return None

    def getValue(self):
        """To get this parameter property named 'value'
        """
        if self.hasAssignedValue():
            return self.getAssignedValue()
        return self.getDefaultValue()

    def getParamKey(self):
        """To trans value to a dict and return
        """
        param = {
            'name': self.name,
            'value': self.getValue()
        }
        return param

    def hasValue(self):
        """check this parameter whether has 'value'
        """
        return self.hasAssignedValue() or self.hasDefaultValue()

    def getParamInstanceData(self):
        """To get a parameter used by TestSet
        """
        data = {
            'name': self.name,
            'identities': {'identity': [{'name': 'ax_id', 'value': self.identity}]}
        }
        if re.match('multiple|list', self.type.name):
            data['value'] = {}
            data['value'].update({'values': self.getValue()})
        else:
            data['value'] = self.getValue()

        return data

    def getMetaData(self):
        """To get this parameter raw data in case
        """
        data = {
            'type': self.type.name,
            'name': self.name
        }

        if 'identity' in self.parameter:
            data['identity'] = self.identity

        if 'display_name' in self.parameter:
            data['display_name'] = self.displayName

        if 'description' in self.parameter:
            data['description'] = self.description
        if 'optional' in self.parameter:
            data['optional'] = self.parameter['optional']

        if 'default_value' in self.parameter:
            data['default_value'] = self.parameter['default_value']

        return data

    def setAssinedValue(self, assigned):
        """To set the assigned_value of this parameter after validated
        """
        self.parameter['assigned_value'] = self.type.getValidInput(assigned)

    def setDefaultValue(self, defauted):
        """To set the default_value of this parameter after validated
        """
        self.parameter['default_value'] = self.type.getValidInput(defauted)

    def setValue(self, param):
        """To set the value of this parameter after validated
        """
        self.setAssinedValue(param)