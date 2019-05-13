# -*- coding: utf-8 -*-

"""
    Effect: To manage resource of test bed configured
"""

import traceback

from Framework.Utils.Validate import validate
from UserControlLib.AndroidPhone import AndroidPhone
from Framework import Log
from Framework.Exception import ATException


class Resource(object):
    """The needed test resources when the test executing
    """
    OPERATIONAL_KIND = ['phones']

    @validate(testBedData=dict)
    def __init__(self, testBedData):
        self.logger = Log.getLogger(str(self.__module__))

        # To get the AndroidPhone data
        self.testBedMetaData = testBedData
        self.rawResourceData = {}
        for kind in Resource.OPERATIONAL_KIND:
            if kind in testBedData:
                self.rawResourceData[kind] = testBedData[kind]

        self.globalEnviromentiInfo = {}
        if 'global_environment_info' in testBedData:
            self.globalEnviromentiInfo = testBedData['global_environment_info']

        self.initState = 'incomplete'
        self.initErrors = []
        self.testEngine = None
        self.phone = {}

        self.initialize()
        # self.setDeviceResource()


    def initialize(self):
        """To init all the operational objects
        """
        params = self.getRawResourceData()
        initErrors = []

        if 'phones' in params and params['phones'] and 'Android' in params['phones'] and params['phones']['Android']:
            rawPhones = self.__changeParamToList(params['phones']['Android'])
            try:
                self.phone = self.__createPhones(rawPhones)
            except ATException as e:
                initErrors.append('%s\n%s' % (e.message, traceback.format_exc()))


        self.initErrors = initErrors
        if len(self.initErrors)>0:
            self.initState = 'failed'
            errors = '\n'.join(initErrors)
            self.logger.error('There were errors creating thre resource object:\n%s' % errors)
            return

        # if self.globalEnviromentiInfo:
        #     allDevices = self.getAllDevices()
        #     for device in allDevices:
        #         if device.environmentInfo:
        #             for env in self.globalEnviromentiInfo:
        #                 if env not in device.environmentInfo:
        #                     device.environmentInfo[env] = self.globalEnviromentiInfo[env]
        #         else:
        #             device.environmentInfo = self.globalEnviromentiInfo

        self.initState = 'complete'

    def getRawResourceData(self):
        """To get the raw dict of the testbed xml file
        """
        if self.rawResourceData:
            return self.rawResourceData
        else:
            self.logger.info('testbed dose not be specified.')
            return {}

    def setTestbedFile(self, path):
        """To set the absolute path to the testbed xml file

        Args:
            path    (str): Absolute path of the testbed xml file
        """
        self.testbedFile = None

    def getTestbedFile(self):
        """To get the absolute path of the testbed xml file

        Args:
            path    (str): Absolute path of the testbed xml file
        """
        return self.testbedFile

    def getInitState(self):
        """To get the resource object init state
        """
        return self.initState

    def getInitErrors(self):
        """To get the resource object init error message list, when initialize() execute failed
        """
        return self.initErrors

    def setTestEngine(self, engine):
        """To set the ATFramework.Engine.Engine
        """
        self.testEngine = engine

    def getTestEngine(self):
        """To get the ATFramework.Engine.Engine
        """
        return self.testEngine

    @validate(raw=dict)
    def __createPhone(self, raw):
        """To create a phone instance
        """
        template = {
            'platformName': {'types': str, 'optional': False},
            'platformVersion': {'types': str, 'optional': False},
            'deviceName': {'types': str, 'optional': False},
            'app': {'types': str, 'optional': False},
            'appPackage': {'types': str, 'optional': False},
            'command_executor': {'types': str, 'optional': False},
            'id': {'types': str, 'optional': False},
            'account': {'types': dict, 'optional': False}
        }
        temp = raw
        command_executor = temp.pop('command_executor')
        phone = AndroidPhone(command_executor=command_executor, params=temp)
        if phone:
            return phone
        else:
            raise ATException('Create AndroidPhone failed...')

    @validate(raw=list)
    def __createPhones(self, raw):
        """To create all phones instance
        """
        phones = {}

        for item in raw:
            phoneObj = self.__createPhone(item)
            phones[phoneObj.getPhoneId()] = phoneObj

        return phones

    @staticmethod
    def __changeParamToList(param):
        """
        """
        if isinstance(param, list):
            return param

        if isinstance(param, dict):
            return [param]

    @validate(id=str)
    def getAndroidPhone(self, id=None):
        if id:
            if id in self.phone:
                self.logger.info('Accessed to The exist AndroidPhone instance [ID: %s].' % id)
                return self.phone[id]
            self.logger.info('The specified AndroidPhone instance [ID: %s] is not exist .' % id)
            return None
        else:
            self.logger.info('Accessed to The exist AndroidPhone instance [ID: %s].' % str(self.phone.keys()))
            return self.phone.values()