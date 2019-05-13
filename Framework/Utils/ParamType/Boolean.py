#!/user/bin/python
# -*- coding: utf-8 -*-

"""
功能    :
修改记录 :
"""

import re

from Framework.Exception import ATException
from ParamTypeBase import ParamTypeBase


class Boolean(ParamTypeBase):

    def __init__(self, typeAndValidation):
        super(Boolean, self).__init__(typeAndValidation)

    def getValidInput(self, defaultBoolean):
        if defaultBoolean is None or defaultBoolean == 'None':
            return None
        if defaultBoolean is True or defaultBoolean == 1:
            return True
        if defaultBoolean is False or defaultBoolean == 0:
            return False
        if re.match('Y|True|1|Yes', str(defaultBoolean), re.IGNORECASE):
            return True
        if re.match('N|False|0|No', str(defaultBoolean), re.IGNORECASE):
            return False

        raise ATException('Boolean object getValueInput() failed. \ndefaultBoolean(%s) is not bool.' % str(defaultBoolean))


