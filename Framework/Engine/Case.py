#!/user/bin/python
# -*- coding: utf-8 -*-

"""
Effect : Case configuration based class
"""

from Framework.Engine.Base import Base
from Framework.Exception import ATException


class Case(Base):
    """test case base class
    """

    def __init__(self, validation):
        super(Case, self).__init__(validation)

    def preHandle(self):
        """mainly used for call addParameter() to set parameters of this case
        """
        pass
    def testHandle(self):
        """mainly used for call detailed operation of this case
        """
        pass

    def postHandle(self):
        """mainly used for call cleanup() to clean data of this case
        """
        self.logInfo('This is post test case ...')
        try:
            self.performCleanUp()
        except ATException as e:
            raise ATException('An exception occurred during the post test case.\nDetails: %s' % e)