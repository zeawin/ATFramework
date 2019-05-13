# -*- coding: utf-8 -*-

"""
Effect : Select
"""


from Framework.Utils.ParamType.ParamTypeBase import ParamTypeBase
from Framework.Exception.ATException import ATException
from Framework.Utils.Common import listMap


class Select(ParamTypeBase):
    """Select
    """
    def __init__(self, typeAndValidation):
        super(Select, self).__init__(typeAndValidation)

        if self.validation is None:
            raise ATException('Select object create failed, validation should not be None.')

        if 'valid_values' not in self.validation:
            raise ATException('Select object create failed, validation has not key named \'valid_values\'.')
        self.validationValue = self.validation['valid_values']
        if self.validationValue is None:
            raise ATException('Select object create failed, validation[\'valid_values\'] should not be None.')

        def func(validValueMember):
            validationDict = {validValueMember: 1}
            return validationDict

        self.validation = listMap(func, self.validationValue)

    def hasValidation(self):
        """
        """
        if self.validation:
            return True
        return False

    def getValidation(self):
        """
        """
        if self.hasValidation():
            return {'valid_values': self.getValidationValues()}
        return None

    def getValidationValues(self):
        """
        """
        if self.hasValidation():
            return self.validation.keys()
        return None

    def getValidInput(self, defauled):
        """
        """
        if defauled not in self.validation:
            raise ATException('Select object getValidInput() failed, defaulted[%s] is not in validation valid_values.'
                              % defauled)
        return defauled