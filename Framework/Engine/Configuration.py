#!/user/bin/python
# -*- coding: utf-8 -*-

"""
Effect: Case configuration based class
"""
from Framework.Engine.Base import Base


class Configuration(Base):

    def __init__(self, validation):
        self.configParams = validation.pop('config_param', None)
        self.deConfigParams = validation.pop('de_config_param', None)
        Base.__init__(self, validation)

    def configure(self):
        """excute the test configuration's configure operation
        """

        self.logInfo('configure dose not be implements')

    def excuteConfigure(self):
        """called configure() or deConfigure() by Engine
        """
        if self.configParams:
            self.setParameter(self.configParams)
        self.configure()

        if self.deConfigParams:
            self.setParameter(self.deConfigParams)

    def deConfigure(self):
        """excute the test configuration's cleared configure operation
        """

        self.logInfo('deConfigure dose not be implements')
        # 2:55