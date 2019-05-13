#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
Set类，测试套接口定义，测试用例管理
"""

import re
from threading import Semaphore

from Parameter import Parameter
from Framework import Log
from Framework.Utils.Validate import validate
from Framework.Exception import ATException
# from ATFramework.Utils.ParamUtil import TYPE
from Status import TEST_STATUS


class Set(object):
    """
    """

    @validate(testSetParameter=dict)
    def  __init__(self, testSetParameter):
        self.caseData = {}
        self.engine = None

        self.customParams = testSetParameter["test_set_params"]
        self.parameters = {}
        if self.customParams:
            self.setParameter(self.customParams)

        self.identities = testSetParameter["identities"]
        self.logDir = testSetParameter["log_dir"]
        self.name = testSetParameter["name"]
        self.testCases = testSetParameter["tests"]
        self.hooks = testSetParameter["hooks"]

        for hook in self.hooks:
            hook.setTestSet(self)

        self.postSetActions = []
        self.preSetActions = []
        self.runningTest = None
        self.runHistory = []
        self.status = TEST_STATUS.NOT_RUN

        for tc in self.testCases:
            tc.setTestSet(self)

        self.logger = Log.getLogger(self.__class__.__name__)
        self.caseDataSemaphore = Semaphore()

    def setEngine(self, testEngine):
        """ 设置test set的controller
        """
        self.engine = testEngine

    @validate(history=list)
    def setRunHistory(self, history):
        """设置test set中已经运行的test
        """
        self.runHistory.extend(history)

    @validate(testSetStatus=str)
    def setStatus(self, testSetStatus):
        """设置test set的状态
        """
        if not re.match(r'^(Runing|NotRun|Complete|Incomplete)',testSetStatus, re.IGNORECASE):
            raise ATException("status(%s) Error." % testSetStatus)
        self.status = testSetStatus


    def setParameter(self, customParams=None):
        """设置test set的parameter
        """
        # todo instead
        # self.addParameter(
        #     name='duration',
        #     description='Duration to run for',
        #     default_value='1H',
        #     type=TYPE.TIME,
        #     display_name='Duration',
        # )
        # self.addParameter(
        #     name='parallel',
        #     description='if to run tests in parallel',
        #     default_value='False',
        #     type=TYPE.BOOLEAN,
        #     display_name='Parallel',
        # )
        self.addParameter(
            name='duration',
            description='Duration to run for',
            default_value='1H',
            type='time',
            display_name='Duration'
        )
        self.addParameter(
            name='parallel',
            description='if to run tests in parallel',
            default_value='False',
            type='boolean',
            display_name='Parallel'
        )
        if not customParams:
            return

        has_invalid_param = False

        for param in customParams:
            if param["name"] in self.parameters:
                paramter_obj = self.parameters[param["name"]]
                try:
                    paramter_obj.setValue(param["value"])
                except ATException:
                    logMessage = "Test Set ParamUtil: [name] has been set to " \
                                 "an invalid value. ".format(name=param["name"])
                    # self.logger.error(logMessage)
                    has_invalid_param = True

        if has_invalid_param:
            raise ATException('One or more Test Set parameters are invalid. please check log '
                                 'for more informaton.')

    def getParameter(self, *args):
        """获取指定名字的parameter的value,未指定名字时返回全部
        """
        paramValue = {}

        if not args:
            for key in self.parameters:
                paramValue[key] = self.parameters[key].getValue()
            return paramValue

        for reqName in args:
            if reqName not in self.parameters:
                raise ATException("parameter name: '%s' does not exist." % reqName)
            paramValue[reqName] = self.parameters[reqName].getValue()
        return paramValue

    def addParameter(self, **kwargs):
        """添加test set的parameter
        """
        paramObj = Parameter(kwargs)

        if paramObj.name in self.parameters:
            raise ATException("%s: add parameter Fail. "
                                 "parameter: '%s' already exists. " % (self.name, paramObj.name))

        if not paramObj.isOptional() and paramObj.getValue() is None:
            raise ATException("%s: add parameter Fail, parameter: '%s' "
                                 "is optional parameter. must be set a value. " % (self.name, paramObj.name))

        self.parameters[paramObj.name] = paramObj

    @validate(identityName=str)
    def getIdentity(self, identityName):
        """获取指定类型的identity
        """
        if self.identities is None:
            return None
        elif identityName in self.identities:
            return self.identities[identityName]
        else:
            self.logger.trace("Hequested identitiy: %s does not "
                              "exist in the test set. " % identityName)

    @validate(saveData=dict)
    def saveData(self, saveData):
        """保存test case的测试数据，test case中调用
        """
        # saveData 控制Case 保存caseData, 同一时间只允许一个Case保存数据
        self.caseDataSemaphore.acquire()

        for key in saveData:
            self.caseData[key] = saveData[key]

        self.caseDataSemaphore.release()

    @validate(dataNameList=tuple)
    def getData(self, dataNameList):
        """获取caseData中指定名称key的数据
        """
        tmpData=[]
        self.caseDataSemaphore.acquire()

        for key in dataNameList:
            if key in self.caseData:
                tmpData[key] = self.caseData[key]

        self.caseDataSemaphore.release()

        return tmpData

    @validate(postActons=list)
    def addPostSetActions(self, postActons):
        """添加需要在test set结束时执行的操作
        """
        self.postSetActions.extend(postActons)

    @validate(preActions=list)
    def addPreSetActions(self,preActions):
        """添加需要在test set开始时执行的操作
        """
        self.preSetActions.extend(preActions)

    def runPreSetActions(self):
        """执行test set执行前需要执行的操作"""
        # todo执行前的其他操作
        # 执行preSetActions

        if self.preSetActions:
            self.logger.info("Performing Test Defined Pro Test Set Actions.")
        else:
            self.logger.info("Test Set have not Pre Test Set Actions.")
            return

        while len(self.preSetActions):
            preAction = self.preSetActions.pop()

            # preAction 为函数
            if hasattr(preAction, '__call__'):
                try:
                    preAction()
                except ATException, error:
                    self.logger.error("Pre Test Aciton threw an exception: %s" % error)

            # preAction 为可执行的代码段
            elif isinstance(preAction, str):
                try:
                    exec preAction
                except ATException, error:
                    self.logger.error("Pre Test Aciton threw an exception: %s" % error)

    def runPostSetActions(self):
        """执行test set执行后需要执行的操作
        """
        # todo执行前的其他操作
        # 执行postSetActions
        if self.postSetActions:
            self.logger.info("Performing Test Defined Post Test Set Actions.")
        else:
            self.logger.info("Test Set have not Post Test Set Actions.")
            return

        while len(self.postSetActions):
            postAction = self.postSetActions.pop()

            # postAction 为函数
            if hasattr(postAction, '__call__'):
                try:
                    postAction()
                except ATException, error:
                    self.logger.error("Post Test Aciton threw an exception: %s" % error)

            # postAction 为可执行的代码段
            elif isinstance(postAction, str):
                try:
                    exec postAction
                except ATException, error:
                    self.logger.error("Post Test Aciton threw an exception: %s" % error)

    def setCurrentlyRunningTest(self):
        """设置当前测试套中正在执行的测试用例
        """
        self.runningTest = self.engine.currentRunningTest

    def addHooks(self, hookObjectList):
        """添加hook对象到测试套对象中
        """
        for hook in hookObjectList:
            hook.setTestSet(self)
            if hook not in self.hooks:
                self.hooks.append(hook)