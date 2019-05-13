#!/user/bin/python
# -*- coding: utf-8 -*-

"""
功  能: 测试用例基类, Case、Configuration父类
"""

import re
import threading

from Framework import Log
from Framework.Engine.Parameter import Parameter
from Framework.Exception import ATException
from Status import TEST_STATUS

# 测试套中创建case时传入的数据，默认如下:

TEST_VALIDATION = {
    'name': {'types': str, 'optional': False},
    'path': {'types': str, 'optional': True},
    'resource': {'types': isinstance, 'optional': False},
    'params': {'types': list, 'optional': False},
    'description': {'types': str, 'optional': False},
    'tags': {'types': list, 'optional': False},
    'required_equipment': {'types': list, 'optional': False},
    'steps_to_perform': {'types': list, 'optional': False},
    'shareable_equipment': {'types': str, 'optional': False},
    'identities': {'types': list, 'optional': False},
    'instance_id': {'types': str, 'optional': True},
    'order': {'types': int, 'optional': True},
    'dependencies': {'types': dict, 'optional': False}
}


class Base(object):
    """Case's base class
    """

    # todo validaton
    def __init__(self, caseValidation):
        super(Base, self).__init__()
        self.logger = Log.getLogger(self.__module__)
        self.requirement = {'requirement_configuration': []}
        self.cleanUpConfiguration = True

        # thread counter
        self.errorCount = 0
        self.warnCount = 0
        self.errorCountSemaphore = threading.Semaphore()
        self.warnCountSemaphore = threading.Semaphore()

        # handle exception
        self.handleErrorCount = 0
        self.handleWarnCount = 0
        self.handleErrorMsg = ''
        self.handleWarnMsg = ''

        self.caseStatus = 'Not_Run'
        self.name = caseValidation['name']
        self.path = caseValidation['location']
        self.resource = caseValidation['resource']
        self.customParams = caseValidation['params']
        self.description = caseValidation['description']
        self.tags = caseValidation['tags']
        self.requiredEquipment = caseValidation['required_equipment']
        self.testSteps = caseValidation['steps_to_perform']
        self.shareableEquipment = caseValidation['shareable_equipment']
        self.identities = caseValidation['identities']
        self.instanceID = caseValidation['instance_id']
        self.order = caseValidation['order']
        self.dependencies = caseValidation['dependencies']

        self.parameters = {}
        self.cleanUpStack = []
        self.testSet = None
        self.casePackage = re.sub(r'/|\\', ',', self.path)
        self.failureReason = ''

        self.startTime = '1971-00-00 00:00:00'
        self.endTime = '1971-00-00 00:00:00'

        # add test data begin test
        self.createMetaData()

        # give Set's case parameters to this case
        self.setParameter(self.customParams)

        # self.configEnvCreateComponent = []
        self.createRequirement()

    def setDescription(self, description):
        self.description = description

    # def logCaseDescription(self, description):
    #     self.logger.info(description)

    def setTestCaseName(self, name):
        self.name = name

    def setTestSet(self, setObj):
        self.testSet = setObj

    def createMetaData(self):
        pass

    def createRequirement(self):
        pass

    def setTestTags(self, *args):
        self.tags.extends(args)

    def logCaseDetails(self):
        if hasattr(self, '__doc__') and self.__doc__:
            self.logger.info('Case Details:\n    %s\n' % str(self.__doc__).strip())

    def logStep(self, msg):
        self.logger.tcStep(msg)

    def addStep(self, **args):
        self.testSteps.append(args)

    def addParameter(self, **args):
        paramObj = Parameter(args)
        if paramObj.name in self.parameters:
            raise ATException('%s add parameter fail, parameter: %s already exists.' % (self.name, paramObj.name))
        if not paramObj.isOptional() and paramObj.getValue() is None:
            raise ATException('%s add parameter fail, parameter: %s is optional.' % (self.name, paramObj.name))
        self.parameters[paramObj.name] = paramObj

    def getParameter(self, *args):
        paramTemp = {}
        if not args:
            for key in self.parameters:
                paramTemp[key] = self.parameters[key].getValue()
            return paramTemp

        for name in args:
            if name not in self.parameters:
                raise ATException('parameter name: \'%s\' dose not exist.' % name)
            paramTemp[name] = self.parameters[name].getValue()

        return paramTemp

    def getParameterObj(self, *args):
        paramObj = {}
        if not args:
            return self.parameters

        for key in args:
            if key not in self.parameters:
                raise ATException('parameter name: \'%s\' dose not exist.' % key)
            paramObj[key] = self.parameters[key]
        return paramObj

    def getTestSetData(self, *args):
        """get the specified data in Set saved by Case
        """
        return self.testSet.getData(args)

    def saveData(self, data):
        """Save data from this case to Set for other Cases
        """
        self.testSet.SaveData(data)

    def logParameter(self):
        self.logger.info('Parameter: %s' % self.getParameter())

    def setParameter(self, paramList=None):
        """Save params witch get from xml into self.parameters
        """
        if not paramList:
            return
        if not isinstance(paramList, list):
            raise ATException('Input parameter: \'%s\' type error, should be a list' % paramList)

        hasInvalid = False
        for param in paramList:
            if param['name'] in self.parameters:
                paramObj = self.parameters[param['name']]
                try:
                    if 'values' in param:
                        if isinstance(param['values'], dict):
                            paramObj.setValue(param['values']['values'])
                        if isinstance(param['values'], list):
                            tempValue = []
                            for key in param['values']:
                                if isinstance(key['value'], dict):
                                    key['value'] = [key['value']]
                                tempValue.append(key['value'])
                            paramObj.setValue(tempValue)
                    else:
                        paramObj.setValue(param['value'])
                except ATException:
                    msg = 'Test Set Parameter: {name} has been set to an invalid value'.format(name=param['name'])
                    self.logger.error(msg)
                    hasInvalid = True
                if not paramObj.getValue() and paramObj.isOptional():
                    msg = 'A vale for:{name} must be specified.'.format(name=param['name'])
                    self.logger.error(msg)
                    hasInvalid = True
        if hasInvalid:
            raise ATException('One or more parameters are invalid, please check log for more information.')

    def setEquipmentShareable(self, shareable):
        """set the TestDevice shareable
        """
        self.shareableEquipment = shareable

    def isFailed(self):
        """is this case failed
        """
        return self.caseStatus == 'FAILD'

    def isPassed(self):
        """is this case pass
        """
        return self.caseStatus == 'PASS'

    def setCaseStatus(self, status):
        """set this case status
        """
        if status not in TEST_STATUS._fields:
            raise ATException('Case Status: %s is undefined.' % status)
        # 循环并发时，一次失败则结果失败
        if self.caseStatus == 'FAILD' or self.caseStatus == 'CONFIG_ERROR':
            return
        self.caseStatus = status

    def setFailureReason(self, reason):
        """set the failure reason of this case fail
        """
        self.failureReason = reason

    def getErrorCount(self):
        """get the ErrorCount of this case
        """
        self.errorCountSemaphore.acquire()
        count = self.errorCount
        self.errorCountSemaphore.release()
        return count

    def getWarnCount(self):
        """get the WarnCount of this case
        """
        self.warnCountSemaphore.acquire()
        count = self.warnCount
        self.warnCountSemaphore.release()
        return count

    def incrErrorCount(self):
        """set the ErrorCount of this case increment 1
        """
        self.errorCountSemaphore.acquire()
        self.errorCount += 1
        self.errorCountSemaphore.release()

    def incrWarnCount(self):
        """set the WarnCount of this case increment 1
        """
        self.warnCountSemaphore.acquire()
        self.warnCount += 1
        self.warnCountSemaphore.release()

    def __logStepAndStatus(self, msg):
        """set a step and its status
        """
        status = dict()
        status['name'] = self.name

    def addCleanUpStack(self, cleanAction):
        """add the clean stack at the end of case
        """
        if isinstance(cleanAction, list):
            for key in cleanAction:
                if not hasattr(key, '__call__') and not isinstance(key, str):
                    raise ATException('Only callable str object may be passed addCleanUpStack()')
            self.cleanUpStack.extend(cleanAction)
        elif isinstance(cleanAction, dict):
            raise ATException('Only callable str object may be passed addCleanUpStack()')
        else:
            self.cleanUpStack.append(cleanAction)

    def addToPostTestSet(self, postSetAction):
        """set the clean operation for Set
        """
        self.testSet.addPostSetAction(postSetAction)

    def removeFormCleanUpStatck(self):
        """remove the clean stack at the last of self.cleanUpStack
        """
        self.cleanUpStack.pop()

    def performCleanUp(self):
        errorCount = self.getErrorCount()
        if self.cleanUpStack:
            self.logger.info('Performing test defined cleanup actions.')
        else:
            self.logger.warn('Test have not clean actions.')

        while len(self.cleanUpStack):
            cleanAction = self.cleanUpStack.pop()
            if hasattr(cleanAction, '__call__'):
                try:
                    cleanAction()
                except ATException as e:
                    self.logger.error('Clean up action threw an exception %s' % e)
            elif isinstance(cleanAction, str):
                try:
                    exec cleanAction
                except ATException as e:
                    self.logger.error('Clean up action threw an exception %s' % e)
                    # elif isinstance(cleanAction, componentBase)
        if (self.getErrorCount() - errorCount) > 0:
            raise ATException('%s errors occurred when performing cleanup action, '
                              'please check above logs for details' % (self.getErrorCount() - errorCount))

    def hasIdentity(self, identity):
        """check the case whether has identity
        Args:
            identity(dict):
                identity={'name': 'DY'}
        """
        if self.identities is None:
            return False

        for child in self.identities['identity']:
            if identity['name'].lower() == child['name'].lower():
                return True

        return False

    def getIdentity(self, reqIdentity=None):
        """get the specified identity
        Args:
            reqIdentity (dict or None):
                like reqIdentity={'name': 'example'}
        """
        if reqIdentity is None:
            return self.identities['identity']

        identities = []
        if not self.hasIdentity(reqIdentity):
            raise ATException('The identity: %s has not been provided for the test: %s.'
                              % (reqIdentity, self.name))
        for identity in self.identities['identity']:
            if reqIdentity['name'] == identity['name']:
                identities.append(identity)
        return identities

    def addIdentity(self, identity):
        """add identity to case

        Args:
            identity(dict):
                identity={'name': 'DY', 'id': 'TC_001'}
        """
        if self.hasIdentity({'name': identity['name']}):
            raise ATException('The identity: %s already exists in this case.' % identity['name'])

        self.identities['identity'].append(identity)

    def logInfo(self, msg):
        self.logger.info(msg)

    def logError(self, msg):
        self.logger.error(msg)

    def logDebug(self, msg):
        self.logger.debug(msg)

    def logWarn(self, msg):
        self.logger.warn(msg)

    def logTrace(self, msg):
        self.logger.trace(msg)

    def stopOnError(self):
        """when case failed, stop case
        """
        if re.match('FAIL|ConfigError$', self.caseStatus):
            self.testSet.Engine.setStopOnError(True)
            raise ATException('This case failed with stop_on_error. '
                              'Test Set will stop here and psotTestCase will not contine.')

    @classmethod
    def acquireWaitPoint(cls, point, timeout=None):
        """set case pause point
        """
        globals()[point] = threading.Event()
        globals()[point].wait(timeout=timeout)

    @classmethod
    def releaseWaitPoint(cls, point):
        """release the case pause point
        """
        try:
            globals()[point].set()
            globals()[point] = None
            del globals()[point]
        except ATException:
            # Log.getLogger(cls.__module__).warn('Release Point: %s Failed, wait totimeout.'
            #                                    'if you didn\'t define timeout, it will be hung.'%point)
            pass

    # def addCreateConfigEnvComponent(self, compObj):
    #     """Save Component object created by ConfigureEnv into this case
    #     """
    #
    #     if isinstance(compObj, list):
    #         for obj in compObj:
    #             if isinstance(obj, ComponentBase):
    #                 self.configEnvCreateComponent.append(obj)
    #             else:
    #                 self.logger.warn('%s is not component instance, add failed'%compObj)
    #     elif isinstance(compObj, ComponentBase):
    #         self.configEnvCreateComponent.append(obj)
    #     else:
    #         self.logger.warn('%s is not component instance, add failed'%compObj)

    # def getNextCraeteConfigEnvComponent(self):
    #     """pop the list of end index component
    #     """
    #     if not self.configEnvCreateComponent:
    #         cmpObj = None
    #     else:
    #         cmpObj = self.configEnvCreateComponent.pop()
    #     return cmpObj

    # def clearValidatedByConfigEnvComponent(self):
    #     """clear all component objects' validated sign in all devices
    #     """
    #     device = self.resource.getAllDevice()
    #     for dType in device:
    #         if re.match('block|file|unified', dType):
    #             dev = device[dType]
    #             for ID in dev:
    #                 dev[ID].removeValidatedByEngine()

    # def addRequirement(self, params):
    #     """add the require info, config and so on
    #     """
    #     for key in params:
    #         if key == 'requirement_configuration':
    #             configInfoParams = params[key]
    #             self.__addConfigureInfoRequirement(params)

    # def removeRequirement(self, params):
    #     """remove the require info, config and so on
    #     """
    #     devices = self.resource.getAllDevice()
    #
    #     def threadSub(dev, case=None):
    #         wipeConfig(dev, case=case)
    #
    #     threads = list()
    #     for dev in devices:
    #         if hasattr(dev, 'type') and re.match('block|file|unified', dev.type):
    #             th = threading.Thread(target=threadSub, args=(dev, self))
    #             threads.append(th)
    #     for th in threads:
    #         th.start()
    #
    #     for th in threads:
    #         if th.isAlive():
    #             th.join()

    # def __addConfigureInfoRequirement(self, params):
    #     """add configuration requiement on array
    #     """
    #     for param in params:
    #         if 'clean_up' in param:
    #             self.cleanUpConfigration = param['clean_up']
    #             continue
    #         deviceID = param.get('device_id')
    #         deviceType = param.get('device_type')
    #         requireDict = param.get('requirement')
    #         if not deviceID and not deviceType and not re.match('unified', deviceType) and not requireDict:
    #             raise ATException("Add requirement parameter failed.")
    #         tmpRequirement = ConfigureInfoBase(self, deviceType, deviceID, requireDict)
    #         self.requirement['requirement_configuration'].append(())

    def clearConfigredKeyOnDevices(self):
        """clear the validated by engine reference on all know device components
        """
        devices = []

        devices.extend(self.resource.getAllDevice())
        for dev in devices:
            if hasattr(dev, 'configred'):
                dev.configured = False
            if hasattr(dev, 'configID'):
                dev.configured = False

    def getDevice(self, deviceType, deviceID):
        return self.resource.getDevice(deviceType, deviceID)

    def handleException(self, types, msg, trace):
        """hold exception
        Args:
            types   (str): error type, 'warning' or 'error'
            msg     (str): error info
            trace   (str): trace point
        """
        if types == 'warning':
            self.handleWarnCount += 1
            self.handleWarnMsg += msg + ':\n' + trace + '\n'
        elif types == 'error':
            self.handleErrorCount += 1
            self.handleErrorMsg += msg + ':\n' + trace + '\n'

    def logHandleReport(self):
        self.logError('\nThe error count: %s\nThe error message: %s\n' % (self.handleErrorCount, self.handleErrorMsg))
        self.logError('\nThe warn count: %s\nThe warn message: %s\n' % (self.handleWarnCount, self.handleWarnMsg))

    def releaseHandleException(self):
        """clear all holded exception info
        """
        self.handleErrorCount = 0
        self.handleWarnCount = 0
        self.handleErrorMsg = ''
        self.handleWarnMsg = ''
