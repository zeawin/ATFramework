# -*- coding: utf-8 -*-

"""
Effect : Case and Set controller or control excute
"""

import os
import sys
import datetime
import time
import yaml
import threading
import re
import traceback

from Framework.Utils.Threads import Threads
from Framework.Utils.Validate import validate
from Framework.Engine.Parameter import Parameter
from Framework.Exception import ATException
from Framework.Engine.Configuration import Configuration
from Framework.Engine.Case import Case
from Framework.Engine.Base import Base
from Framework.Engine.Status import *
# from ATFramework.Utils.HostMonitor import HostMonitor
# from ATFramework.Utils.Units import Units
from Framework import Log


class Engine(object):
    """Test Engine

    Args:
        param   (dict): Test Engine Param, include set object and engine configuration, like follow
                        test_set    (Set)   : Test set instance
                        params      (list)  : Engine param, default empty
    """

    def __init__(self, param):
        super(Engine, self).__init__()
        self.testSet = param['test_set']
        self.testSetId = self.testSet.getIdentity('id')

        self.customParams = param['params']
        self.parameters = {}

        self.testCases = self.testSet.testCases

        self.startTime = None
        self.statusYamlLock = threading.Lock()

        self.stopOnError = False
        self.logRotationSize = None
        self.configStopOnError = False
        self.monitorInterval = None
        self.logMaxSize = None
        self.runTestInParallelFlag = False
        self.isTestSetError = False
        self.totalTestCounter = 0

        # The map of thread id and case name
        self.tidToTcName = {}
        # The map of thread id and case object
        self.tidToTcObject = {}
        # The test case's global status
        self.globalTestStatus = {}
        # The map of thread id and case log file
        self.tidToTcLogs = {}

        self.timeLineLogFileHandler = None
        self.EngineLogFileName = None
        self.currentRunningTestThreads = []
        self.currentRunningTest = None
        self.postTestSetExecuted = 0
        self.testSetStartTime = None
        self.statusLogFileHandler = self.__open_status_log_file()

        self.logger = Log.getLogger(self.__module__)
        self.setParameter(self.customParams)
        self.logLevel = self.getParameter('logging_level').get('logging_level')
        self.testSet.setEngine(self)
        self.__init_status_log_file()

    def __open_status_log_file(self):
        """open the status.yaml file
        """
        fh = None
        try:
            path = os.path.join(Log.LogFileDir, 'status.yaml')
            fh = open(path, 'a+')
        except IOError as e:
            self.logger.debug('Unable to setup status loggin: \n', e)
        return fh

    def __close_status_log_file(self):
        """close the status.yaml file
        """
        self.statusLogFileHandler.flush()
        self.statusLogFileHandler.close()

    def __init_status_log_file(self):
        """Init and write status.yaml
        """
        status = {
            'current_stage': 'init',
            'current_running_test': 'init_test_set',
            'process_id': os.getpid(),
            'program_name': 'ATFramework'
        }
        test_set_status_to_write = {
            'what': 'test_set',
            'id': self.testSetId,
            'name': self.testSet.name,
            'status': status
        }

        self.writeStatus(test_set_status_to_write)

        # To write the status of test case
        for tc in self.testCases:
            status_case = {'current_stage': TEST_STATUS.NOT_RUN}
            if isinstance(tc, Configuration):
                what = 'test_config'
            elif isinstance(tc, Case):
                what = 'test_case'
            else:
                what = None

            test_to_write_cache = {
                'what': what,
                'id': self._getIdentityOfTest(tc),
                'name': tc.name,
                'status': status_case
            }
            self.writeStatus(test_to_write_cache)

    def apply_requirement(self, configuration, case):
        if not configuration.device:
            raise ATException('Have not invalid device to applayConfig')
        applyConfig(configuration, case)

    def __runTest(self, case, caseLogFile):
        """run test case single
        """
        self.logger.tcStart()
        case.startTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        case.setCaseStatus(TEST_STATUS.RUNNING)
        self.globalTestStatus[case.name]['status'] = TEST_STATUS.RUNNING

        configs = case.requirement['requirement_configuration']

        # write into status.yaml
        tmpStatus = {'current_stage': 'pre'}
        testCaseWriteStatus = {
            'id': self._getIdentityOfTest(case),
            'name': case.name,
            'what': 'test_case',
            'status': tmpStatus
        }
        self.writeStatus(testCaseWriteStatus)
        testCaseWriteStatus.pop('status')

        case.logger.info('====== Pre Handle of Case: %s ======' % case.name)

        # create configuration
        threads = []
        for config in configs:
            th = Threads(self.apply_requirement, config, configObject=config, tcObject=case)
            threads.append(th)

        for th in threads:
            th.start()

        # execute preHandle, case will be failed while failed
        preTestCasePassFlag = True
        try:
            tmpError = ''
            for th in threads:
                th.join()
                if th.errorMsg:
                    tmpError += '%s' % os.linesep + th.errorMsg
            if tmpError:
                raise ATException(tmpError)
            case.preHandle()
            self.runHooks('afterPreHandle')
        except ATException as e:
            preTestCasePassFlag = False
            self._handleException(case, e, 'pre')
            Log.MainLogger.fail('%s Pre Handle failed' % case.name)
            self.runHooks('afterPreHandle')

        if preTestCasePassFlag is True:
            case.logger.passInfo('%s Pre Handle Passed.' % case.name)

        # execute precedure, case will be interrupted while preHandle failed

        mainTestCasePassFlag = False
        if preTestCasePassFlag:
            case.logger.info('====== Test Handle of Case ======')

            # write into status.yaml
            tmpStatus = {'pre_status': TEST_STATUS.PASS}
            if self.runTestInParallelFlag:
                tmpStatus['duration'] = '%sS' % str(
                    time.time() - self.globalTestStatus[case.name['status']]['start_time'])
            else:
                tmpStatus['duration'] = '%sS' % str(time.time() - self.startTime)

            testCaseWriteStatus['status'] = tmpStatus
            self.writeStatus(testCaseWriteStatus)
            testCaseWriteStatus.pop('status')
            tmpStatus['current_stage'] = 'main'
            try:
                case.testHandle()
                mainTestCasePassFlag = True
                self.runHooks('afterPrecedure')
            except Exception as e:
                mainTestCasePassFlag = False
                self._handleException(case, e, 'main')
                Log.MainLogger.fail(
                    'Case %s Test Handle failed, \ndetails: %s' % (case.name, str(traceback.format_exc())))
                self.runHooks('afterPrecedure')
        if mainTestCasePassFlag is True:
            case.logger.passInfo('[%s Test Handle has passed.]' % case.name)
            if not self.runTestInParallelFlag:
                Log.MainLogger.passInfo('Case [%s] is passed.' % case.name)
            case.setCaseStatus(TEST_STATUS.PASS)

            # write into status.yaml
            tmpStatus['main_stage'] = TEST_STATUS.PASS
            if self.runTestInParallelFlag:
                tmpStatus['duration'] = '%sS' % str(
                    time.time() - self.globalTestStatus[case.name['status']]['start_time'])
            else:
                tmpStatus['duration'] = '%sS' % str(time.time() - self.startTime)

            testCaseWriteStatus['status'] = tmpStatus
            self.writeStatus(testCaseWriteStatus)
            testCaseWriteStatus.pop('status')

        # whether preHandle and procedure failed or passed, postHandle must be executed
        postTestCasePassFlag = True
        self.logger.info('====== Post Handle ======')

        # write into status.yaml
        tmpStatus['current_stage'] = 'post'
        testCaseWriteStatus['status'] = tmpStatus
        self.writeStatus(testCaseWriteStatus)

        try:
            case.postHandle()
            self.runHooks('afterPostHandle')
        except ATException as e:
            postTestCasePassFlag = False
            self._handleException(case, e, 'post')
            self.runHooks('afterPostHandle')

        if postTestCasePassFlag is True:
            case.logger.passInfo('%s Post Handle Passed.' % case.name)

            # write into status.yaml
            tmpStatus['post_status'] = TEST_STATUS.PASS
            if self.runTestInParallelFlag:
                tmpStatus['duration'] = '%sS' % str(
                    time.time() - self.globalTestStatus[case.name['status']]['start_time'])
            else:
                tmpStatus['duration'] = '%sS' % str(time.time() - self.startTime)

            testCaseWriteStatus['status'] = tmpStatus
            self.writeStatus(testCaseWriteStatus)
            testCaseWriteStatus.pop('status')

            if self.runTestInParallelFlag:
                self.globalTestStatus[case.name]['status'] = case.caseStatus

        # write into status.yaml
        tmpStatus['current_stage'] = 'post'
        testCaseWriteStatus['status'] = tmpStatus
        self.writeStatus(testCaseWriteStatus)

        if self.runTestInParallelFlag:
            self.globalTestStatus[case.name]['end_time'] = time.time()
        case.logger.tcEnd()
        Log.releaseFileHandler(Log.LogType.TestCase, caseLogFile)

    def __runConfiguration(self, configuration):
        """To run the configuration instance
        """
        testName = configuration.name
        testId = self._getIdentityOfTest(configuration)
        self.logger.tcStart('TestConfig %s starts...' % testName)
        self.runHooks('afterPreTest')

        tmpStatus = {
            'current_stage': 'main',
            'main_status': TEST_STATUS.NOT_RUN,
            'duration': '0S'
        }
        configurationWriteStatus = {
            'id': testId,
            'name': testName,
            'what': 'configuration',
            'status': tmpStatus
        }

        # execute the config if params is 'Config'
        if configuration.getParameter('Mode')['Mode'] == 'Config':
            self.writeStatus(configurationWriteStatus)
            self.logger.info('====== CONFIGURATION MODE ======')

            try:
                configuration.configure()
            except ATException as e:
                self._handleException(configuration, e, 'main')

            # Save states and write in file
            tmpStatus['duration'] = '%sS' % str(time.time() - self.startTime)
            tmpStatus['main_status'] = TEST_STATUS.PASS
            configurationWriteStatus['status'] = tmpStatus
            self.writeStatus(configurationWriteStatus)

            configuration.setCaseStatus(TEST_STATUS.CONFIGURED)
            self.logger.tcEnd('%s has been successfully configured.' % testName)
            tmpStatus['current_stage'] = 'NODE'
            configurationWriteStatus['status'] = tmpStatus
            self.writeStatus(configurationWriteStatus)

        # execute the deconfig if params is 'DeConfig'
        elif configuration.getParameter('Mode')['Mode'] == 'DeConfig':
            self.writeStatus(configurationWriteStatus)
            self.logger.info('====== DE CONFIGURATION MODE ======')

            try:
                configuration.deConfigure()
            except ATException as e:
                self._handleException(configuration, e, 'main')

            # Save states and write in file
            tmpStatus['duration'] = '%sS' % str(time.time() - self.startTime)
            tmpStatus['main_status'] = TEST_STATUS.PASS
            configurationWriteStatus['status'] = tmpStatus
            self.writeStatus(configurationWriteStatus)

            configuration.setCaseStatus(TEST_STATUS.DECONFIGURED)
            self.logger.tcEnd('%s has been successfully de-configured.' % testName)
            tmpStatus['current_stage'] = 'NODE'
            configurationWriteStatus['status'] = tmpStatus
            self.writeStatus(configurationWriteStatus)

        self.runHooks('afterPrecedure')
        self.runHooks('afterPostHandle')

    def __runTestParallel(self, case):
        """execute case single when executing case concurrently set serial
        """
        # the begin time
        self.globalTestStatus[case.name]['start_time'] = time.time()

        # thread id refected log files
        tcLogFile = case.name
        self.tidToTcLogs[threading.current_thread().ident] = tcLogFile + '---0'
        Log.changeLogFile(Log.LogType.TestCase, tcLogFile)
        case.logCaseDetails()
        case.logParameter()

        # execute case singlly
        self.tidToTcObject[threading.current_thread().ident] = case
        self.__runTest(case, tcLogFile)

    @staticmethod
    def createImageLink():
        """To create the images in file named timeline
        """
        return {}

    def _checkTestCaseThreadStatus(self, timeSinceLastStatus):
        """Polling check the case status
        """
        runningTestCount = len(self.currentRunningTestThreads)

        # statrt check when threads count > 0

        while runningTestCount > 0:
            for th in self.currentRunningTestThreads:
                if not th.isAlive():
                    runningTestCount -= 1
                    if re.match(TEST_STATUS.FAILED + '|' + TEST_STATUS.CONFIG_ERROR,
                                self.tidToTcObject[th.ident].caseStatus):
                        self.logger.error(
                            'Test case %s: [Thread ID: %s] threw an error.' % (self.tidToTcName[th.ident], th.ident))

                        # kill other alive thread and set the case status while case failed and stopOnError has been configured,
                        # and there are alive threads
                        if self.stopOnError:
                            self.logger.info('StopOnError is set so Engine is going to kill all '
                                             'remaining test')
                            for thChild in self.currentRunningTestThreads:
                                if thChild.isAlive():
                                    self.globalTestStatus[self.tidToTcName[thChild.ident]][
                                        'status'] = TEST_STATUS.KILLED
                                    self.globalTestStatus[self.tidToTcName[thChild.ident]]['end_time'] = time.time()
                                    self.killTestThread(self.tidToTcObject[thChild.ident], thChild)

                            # check the thread whether dead

                            for thChild in self.currentRunningTestThreads:
                                if thChild.isAlive():
                                    thChild.join()
                                self.logger.debug('Finished or Exit thread %s' % thChild.ident)

                            runningTestCount = 0
                            self.updateStatus()
                            break

                # every 5 minute record if there are alive thread
                if (time.time() - 300) >= timeSinceLastStatus:
                    self.makeTimeLog()
                    timeSinceLastStatus = time.time()
            time.sleep(1)

        # to wait all the thread complete
        self.waitAllTestComplete(self.currentRunningTestThreads)

        # print the cases' status finally
        for th in self.currentRunningTestThreads:
            logLink = "<a href=',/TestCases/%s.html'><font color=blue>Log Link</font></a>" % self.tidToTcLogs[th.ident]
            self.logger.info('Test case %s: %s.\n Thread ID: %s.\n %s'
                             % (self.tidToTcName[th.ident], self.globalTestStatus[self.tidToTcName[th.ident]]['status'],
                                th.ident, logLink))

    def writeCssStyleToTimeLog(self, durationStr, controllerLink, width):
        """write the css template into TimeLine.xml when executed concurrently
        """
        cssStr = """
        <!DOCTYPE html>
        <html>
        <style>
        .quick-nav {
            position: relative;
            background-color: #FFFFFF;
            font-size: 9px;
            -moz-border-radius: 0px;
            width: %spx;
        }
        .quick-nav table th.skew {
            height: 80px;
            width: 40px;
            position: relative;
            vertical-align: bottom;
        }
        .quick-nav table th.skew > div {
            position: relative;
            top: 0px;
            left:30px;
            height: 100%%;
            transform: skew(-45deg, 0deg);
            -ms-transform: skew(-45deg, 0deg);
            -moz-transform: skew(-45deg, 0deg);
            -webkit-transform: skew(-45deg, 0deg);
            -o-transform: skew(-45deg, 0deg);
            overflow: hidden;
            border-top: lpx solid #CCCCCC;
            border-left: lpx solid #CCCCCC;
            border-right: lpx solid #CCCCCC;
        }
        .quick-nav table th.skew span {
            transform: skew(45deg, 0deg) rotate(315deg);
            -ms-transform: skew(45deg, 0deg) rotate(315deg);
            -moz-transform: skew(45deg, 0deg) rotate(315deg);
            -webkit-transform: skew(45deg, 0deg) rotate(315deg);
            -o-transform: skew(45deg, 0deg) rotate(315deg);
            position: absolute;
            bottom: 5px;
            left: 0px;
            display: inline-block;
            width: 15px;
            text-align: left;
        }
        .quick-nav table td {
            width: 15px;
            height: 15px;
            text-aligh: center;
            vertical-align: middle;
            border: 1px solid #CCCCCC;
            padding: 0px 0px;
        }
        </style>
        <body>
        <h4>PARALLEL Time Chart</h4>
        Total Runtime: %s
        <br>
        %s
        <br>
        <br>
        <div class="quick-nav">
        <table cellspacing="0">
        <thead>
        """ % (width, durationStr, controllerLink)
        self.timeLineLogFileHandler.write(cssStr)

    def _handleException(self, case, msg, stage):
        """deal with the exception occurred running
        """
        name = case.name
        identity = self._getIdentityOfTest(case)

        what = None
        if isinstance(case, Case):
            what = 'test_case'
        elif isinstance(case, Configuration):
            what = 'configuration'

        # the case failed reason
        case.setFailureReason('\n---------------------------------------------\n')
        case.setFailureReason(case.failureReason +
                              'Test Stage: %s Failed because: %s\n' % (stage, msg))
        status = {'current_stage': stage}

        # case is configuration
        if what == 'configuration':
            case.setCaseStatus(TEST_STATUS.FAILED)
            case.logError('%s Failed, because an issue occurred while trying to run the test configuration: \n%s'
                          % (name, msg))
        # stage is pre
        elif stage == 'pre':
            case.setCaseStatus(TEST_STATUS.CONFIG_ERROR)
            if self.runTestInParallelFlag:
                self.globalTestStatus[name]['status'] = TEST_STATUS.FAILED

                case.logError('%s Failed, because an issue occurred while trying to run the preHandle for: \n%s'
                              % (name, msg))
                status['pre_status'] = TEST_STATUS.FAILED
                status['main_status'] = TEST_STATUS.CONFIG_ERROR

        # stage is main
        elif stage == 'main':
            case.setCaseStatus(TEST_STATUS.FAILED)
            if self.runTestInParallelFlag:
                self.globalTestStatus[name]['status'] = TEST_STATUS.FAILED

                case.logError('%s Failed, because an issue occurred while trying to run the test case: \n%s'
                              % (name, msg))
                case.incrErrorCount()
                status['main_status'] = TEST_STATUS.FAILED

        # stage is main
        elif stage == 'post':
            case.logError('%s Failed, because an issue occurred while trying to run the test case: \n%s'
                          % (name, msg))
            status['post_status'] = TEST_STATUS.FAILED

        if self.runTestInParallelFlag and isinstance(case, Case):
            status['duration'] = '%sS' % str(time.time() - self.globalTestStatus[case.name]['start_time'])
        else:
            status['duration'] = '%sS' % str(time.time() - self.startTime)

        statusToWrite = {
            'what': what,
            'id': identity,
            'name': name,
            'status': status
        }
        self.writeStatus(statusToWrite)
        self.setTestSetError(True)

        # todo configuration

        if (isinstance(case, Configuration) and self.configStopOnError) or self.stopOnError:
            # todo configuration
            if self.runTestInParallelFlag and isinstance(case, Case):
                self.globalTestStatus[case.name]['end_time'] = time.time()
            if not self.runTestInParallelFlag:
                self.logger.warn('Engine told me stop on error!')
                self.postTestSet()
                self.logger.warn('Set set stop on error, now exit ATFramework!')
                self.updateStatus()
                self.__close_status_log_file()
                sys.exit(1)

    def _getIdentityOfTest(self, case, identityName='id'):
        """To get the specified case instance
        """
        identityDict = {'name': identityName}
        if case.hasIdentity(identityDict):
            identities = case.getIdentity(identityDict)
            for identity in identities:
                if identity['name'] == identityName:
                    return identity['id']
        else:
            self.logger.trace('Identity [%s] does not exist for %s.' % (identityName, case.name))

    def killTestThread(self, case, th):
        """To kill the specified case threads
        """
        if th.ident in self.tidToTcLogs:
            Log.changeLogFile(Log.LogType.TestCase, re.sub('---0$', '', self.tidToTcLogs[th.ident]))
            case.logger.info('Controller told me stop. \nThread ID: [%s]' % th.ident)
            Log.releaseFileHandler(Log.LogType.TestCase, re.sub('---0$', '', self.tidToTcLogs[th.ident]))
            Log.changeLogFile(Log.LogType.Main, 'Controller')
            case.setCaseStatus(TEST_STATUS.KILLED)
            th.kill()

    def addExecutedParameter(self, **kwargs):
        """To add the test parameters of the engine strategy

        Args:
            kwargs  (dict): Test Engine params, key follow
                            name            (str): parameter name, mandatory
                            display_name    (str): parameter displayed name, optional
                            description     (str): parameter description, optional
                            default_value   (ParamType): parameter type, optional
                            type            (str): parameter Type, defined by ParamType
                            identity        (str): parameter identity
                            assigned_value  (ParamType): parameter value, mandatory
                            optional        (bool): parameter name, optional and default 'False'
        """

        paramObj = Parameter(kwargs)
        if paramObj.name in self.parameters:
            raise ATException('Add parameter failed, parameter: [%s] already exist.' % paramObj.name)
        if not paramObj.isOptional() and paramObj.getValue() is None:
            raise ATException('Add parameter failed, parameter: [%s] is optional, must be set a value.' % paramObj.name)

        self.parameters[paramObj.name] = paramObj

    def setParameter(self, customParamList=None):
        """To set the test params of the Engine
        """
        # stop on error
        self.addExecutedParameter(
            name='stop_on_error',
            description='If set to a true value, it will stop excution of all the test '
                        'in the test set when an error is encountered.',
            default_value=1,
            type='BOOLEAN',
            display_name='Stop On Error'
        )

        # log level
        self.addExecutedParameter(
            name='logging_level',
            description='Logging level for the message to be displayed on the screen',
            default_value='INFO',
            validation={
                'valid_values': ['TRACE', 'DEBUG', 'CMD', 'INFO', 'WARN', 'ERROR', 'STATUS', 'FATAL', 'OFF']
            },
            type='select',
            display_name='Logging level'
        )

        # log rotation size
        self.addExecutedParameter(
            name='log_rotation_size',
            description='The size threshold for the log files beyond which the log files are roted.',
            default_value='60MB',
            type='SIZE',
            display_name='Logging Rotation Size'
        )

        # max log size
        self.addExecutedParameter(
            name='max_log_size',
            description='The max size of the log files for a case',
            default_value='1MB',
            type='SIZE',
            display_name='Max Log Size'
        )

        # stop for config error
        self.addExecutedParameter(
            name='stop_on_config_error',
            description='If set to a true value, it will stop excution of all the test '
                        'in the test set when an error is encountered.',
            default_value=0,
            type='BOOLEAN',
            display_name='Stop On Config Error'
        )

        # monitor interval
        self.addExecutedParameter(
            name='monitor_interval',
            description='The interval in ATFramework time unit to specify how often to get the monitor sample.',
            default_value='1S',
            type='time',
            display_name='Monitor Interval'
        )

        if not customParamList:
            return
        hasInvalidParam = False
        for param in customParamList:
            if param['name'] in self.parameters:
                paramObj = self.parameters[param['name']]
                try:
                    paramObj.setValue(param['value'])
                except ATException:
                    msg = 'The Set Parameter: [%s] has been set to an invalid value' % param['name']
                    self.logger.error(msg)
                    hasInvalidParam = True

                if paramObj.isOptional() and paramObj.getValue() is None:
                    msg = 'A value for Test Set Parameter: [%s] must be specified' % param['name']
                    self.logger.error(msg)
                    hasInvalidParam = True

        if hasInvalidParam:
            raise ATException('One or more Test Set Parameters are invalid, please check log for more information.')

    def getParameter(self, *args):
        """To get the value of the specified name parameter, if name does not specified then return all
        """
        paramValue = {}
        if not args:
            for key in self.parameters:
                paramValue[key] = self.parameters[key].getValue()

        for reqName in args:
            if reqName not in self.parameters:
                raise ATException('Parameter name: [%s] dose not exist.' % reqName)

            paramValue[reqName] = self.parameters[reqName].getValue()

        return paramValue

    def createTestCaseLogFile(self, name):
        """To create the case's log file
        """
        return '%s-%s' % (name, str(self.totalTestCounter))

    @staticmethod
    def getTimeStamp():
        """Get the specified format timestamp
        """
        return datetime.datetime.now().strftime('%Y_%m_d_%H-%M-%S-%f')

    @validate(status=bool)
    def setTestSetError(self, status):
        """To set the status error or not in test set
        """
        self.isTestSetError = status

    def makeTimeLog(self, engineFailFlag=None):
        """To create time log html file, and write timeline

        Args:
             engineFailFlag (bool): Engine error sign, The default is empty, used by rates
        """
        color = 'green'
        status = ''
        for name in self.globalTestStatus:
            if re.match(TEST_STATUS.FAILED + '|' + TEST_STATUS.CONFIG_ERROR, self.globalTestStatus[name]['status']):
                color = 'red'
                status = '---FAILED'
                break

        controllerLink = "<a href='.\Controller---0.html><font color=%s>View Controller Log %s</font></a>" \
                         % (color, status)

        earliest = None
        latest = None
        for name in self.globalTestStatus:
            if self.globalTestStatus[name]['status'] == TEST_STATUS.RUNNING:
                self.globalTestStatus[name]['end_time'] == time.time()
            if earliest is None or (self.globalTestStatus[name]['start_time'] < earliest):
                earliest = self.globalTestStatus[name]['start_time']
            if latest is None or (self.globalTestStatus[name]['end_time'] > latest):
                latest = self.globalTestStatus[name]['end_time']

        if not (earliest and latest):
            self.logger.debug('There is no enough runtime to generate the timeline log yet.'
                              '\n StartTime: [%s] \n LastTime: [%s]' % (str(earliest), str(latest)))
            return

        # create time line log file
        self.setupTimeLog()

        # set the case amount of time

        duration = latest - earliest
        days = int(duration) / (24 * 60 * 60)
        hours = int((duration / (60 * 60)) % 24)
        minutes = int((duration / 60) % 60)
        secounds = int(duration % 60)

        durationStr = '[%s],[%s],[%s],[%s]' % (days, hours, minutes, secounds)

        # Calculate the length of each form
        cellDuration = None
        cellCount = None

        def hasMultipleDuration(startTime, endTime, tcDict):
            for tc in tcDict:
                durationCnt = 0
                if tcDict[tc]['start_time'] >= startTime and tcDict[tc]['end_time'] <= endTime:
                    durationCnt += 1
                if durationCnt > 1:
                    return False
            return True

        def cDurationExec():
            for cDuration in xrange(1, 1200):
                if cDuration * cells > duration:
                    tmp = earliest
                    while tmp < latest:
                        tmp += duration
                        if not hasMultipleDuration(tmp, tmp + cDuration, self.globalTestStatus):
                            return None
                        return {'cDuration': cDuration, 'cells': cells}

        for cells in xrange(25, 1000):
            tmpDurationDict = cDurationExec()
            if not tmpDurationDict:
                continue
            else:
                cellDuration = tmpDurationDict['cDuration']
                cellCount = tmpDurationDict['cells']
                break

        if not (cellDuration and cellCount):
            self.logger.warn('Too much data to plot.')
            return

        width = cellCount * 15
        self.writeCssStyleToTimeLog(durationStr, controllerLink, width)
        imageLink = self.createImageLink()
        self.timeLineLogFileHandler.write('<tr><th></th>')

        # Written form head and timestamp
        for cnt in xrange(0, cellCount):
            timeStr = time.strftime('%B;%d;%H:%M:%S', time.localtime(earliest + (cnt + cellDuration)))
            self.timeLineLogFileHandler.write("<th class='skew'><div><span>%s</span></div></th>" % timeStr)
        self.timeLineLogFileHandler.write("</tr></thead><tbody>\n")

        # According to the number of the case, draw a timeline forms
        for test in self.globalTestStatus:
            self.timeLineLogFileHandler.write('<tr><td>%s</td>' % test)
            cellDict = {}
            for cellCnt in xrange(0, cellCount):
                cellDict[earliest + (cellCnt * cellDuration)] = ''

                containedImg = imageLink['containedPass']
                runningImg = imageLink['runningPass']
                endImg = imageLink['endPass']
                startImg = imageLink['startPass']

                if re.match('fail|configError', self.globalTestStatus[test]['status'], re.IGNORECASE):
                    containedImg = imageLink['containedFail']
                    runningImg = imageLink['runningFail']
                    endImg = imageLink['endFail']
                    startImg = imageLink['startFail']
                elif re.match('kill', self.globalTestStatus[test]['status']):
                    endImg = endImg = imageLink['endKilled']

                if 'tid' in self.globalTestStatus[test] and self.tidToTcLogs[self.globalTestStatus[test]['tid']]:
                    log = self.tidToTcLogs[self.globalTestStatus[test]['tid']]
                    link = "<a href=',\TestCases\%s.html'>" % log
                    containedImg = link + containedImg + '</a>'
                    runningImg = link + runningImg + '</a>'
                    endImg = link + endImg + '</a>'
                    startImg = link + startImg + '</a>'

                running = False

                for count in xrange(0, cellCount):
                    if (earliest + (count * cellDuration)) <= self.globalTestStatus[test]['start_time'] \
                            <= (earliest + (count * cellDuration) + cellDuration) and not running:
                        if (earliest + (count * cellDuration)) <= self.globalTestStatus[test]['end_time'] \
                                < (earliest + (count * cellDuration) + cellDuration):
                            key = earliest + (count * cellDuration)
                            cellDict[key] = containedImg
                        else:
                            key = earliest + (count * cellDuration)
                            cellDict[key] = startImg
                            running = True
                            continue
                    elif (earliest + (count * cellDuration)) <= self.globalTestStatus[test]['end_time'] \
                            <= (earliest + (count * cellDuration) + cellDuration) and running:
                        key = earliest + (count * cellDuration)
                        cellDict[key] = endImg
                        running = False
                        continue
                    elif running:
                        key = earliest + (count * cellDuration)
                        cellDict[key] = runningImg

            for timeKey in sorted(cellDict):
                self.timeLineLogFileHandler.write('<td>')
                if cellDict[timeKey] == '':
                    cellDict[timeKey] = imageLink['bigEmpty']
                self.timeLineLogFileHandler.write(cellDict[timeKey])
                self.timeLineLogFileHandler.write('</td>')

            self.timeLineLogFileHandler.write('</tr>\n')

        self.timeLineLogFileHandler.write('</tbody></table>')
        self.timeLineLogFileHandler.write('<img src=\'Images/Legend.jpg\' alt=\'Legend\'>')
        self.timeLineLogFileHandler.flush()
        self.timeLineLogFileHandler.close()

    def waitAllTestComplete(self, threadList):
        """To wait all threads complete
        """
        self.logger.info('Now just waiting for any case thread exit or finished.')
        for th in threadList:
            if th.released:
                continue
            elif th.isAlive():
                th.join()
            self.releaseThreadHandle(th)

    def createEngineHtmlLog(self):
        """create controller ---0.html
        """

        self.EngineLogFileName = os.path.join(Log.LogFileDir, 'Controller---0.html')
        Log.changeLogFile(Log.LogType.Main, 'Controller')
        self.logger.info('Main Controller Log \n <a href=\'./TimeLine.html\'>Timeline Log</a>')
        Log.MainLogger.info('<a href=\'./Controller---0.html\'>Main Controller Log</a>'
                            '\n<a href=\'./TimeLine.html\'>Timeline Log</a>')

    def runTestsInParallel(self):
        """A single concurrent execution cases
        """
        self.logger.info('Engine.py (runTestsInParallel) - Running all case parallel')
        self.updateStatus()
        self.createEngineHtmlLog()
        self.timeLineLogInitial()

        tmpConfigurationTests = []
        tmpTestsCases = []

        for case in self.testCases:
            if isinstance(case, Configuration):
                tmpConfigurationTests.append(case)
            elif isinstance(case, Case):
                tmpTestsCases.append(case)

        for conf in tmpConfigurationTests:
            self.__runConfiguration(conf)

        timeSinceLastStatus = time.time()

        for case in tmpTestsCases:
            caseTmpName = case.name
            time.sleep(0.1)
            case.setTestCaseName(caseTmpName)

            self.globalTestStatus[case.name] = {}

            caseThread = Threads(self.__runTestParallel, case.name, case=case)
            caseThread.start()
            self.currentRunningTestThreads.append(caseThread)

            while caseThread.ident not in self.tidToTcLogs or not self.tidToTcLogs[caseThread.ident]:
                time.sleep(1)

            logLink = '<a href=\'./TestCases/%s.html\'><font color=blue>%s</font></a>' \
                      % (self.tidToTcLogs[caseThread.ident], self.tidToTcLogs[caseThread.ident])
            self.logger.info(
                'Test Case: [%s] Start...\nThread ID: [%s]\n %s' % (caseThread.name, caseThread.ident, logLink))
            self.tidToTcName[caseThread.ident] = case.name
            self.globalTestStatus[case.name]['tid'] = caseThread.ident

        self._checkTestCaseThreadStatus(timeSinceLastStatus)

        self.makeTimeLog()
        self.updateStatus()

    def incrementTestCounter(self):
        """Increase the count test case execution
        """
        self.totalTestCounter += 1

    def runConfiguration(self):
        """Run the test configuration, should be implemented by RatesEngine
        """
        raise ATException('Engine\s runConfiguration method is unimplemented')

    def runTests(self):
        """Sequential running all the cases configured in set
        """
        runTestCases = []
        self.logger.info('Engine Running All The Cases.')
        self.updateStatus()

        for case in self.testCases:
            self.testSet.setRunHistory(runTestCases)
            self.setCurrentlyRunningTest(case)
            self.testSet.setCurrentlyRunningTest()
            self.startTime = time.time()

            tmpSetStatus = {
                'current_stage': 'main',
                'currently_running_test': case.name
            }
            testSetWriteStatus = {
                'what': 'test_set',
                'name': self.testSet.name,
                'id': self.testSet.getIdentity('id'),
                'status': tmpSetStatus
            }
            self.writeStatus(testSetWriteStatus)

            self.incrementTestCounter()

            # Change log file
            caseLogFile = case.name
            Log.changeLogFile(Log.LogType.TestCase, caseLogFile)
            case.logCaseDetails()
            case.logParameter()

            self.globalTestStatus[case.name] = {}

            self.runHooks('beforePreTest')
            if isinstance(case, Configuration):
                self.__runConfiguration(case)
            else:
                self.__runTest(case, caseLogFile)
                self.updateStatus()
                self.setCurrentlyRunningTest(None)

    def runTestSet(self):
        """executed test set
        """
        self.testSetStartTime = time.time()
        self.testSet.status = TEST_STATUS.RUNNING
        self.logger.info('Setting the execution parameters.')

        # parameters setting
        for paramName in self.parameters:
            if paramName == 'stop_on_error':
                self.stopOnError = self.parameters[paramName].getValue()
            elif paramName == 'stop_on_config_error':
                self.configStopOnError = self.parameters[paramName].getValue()
            elif paramName == 'logging_level':
                self.logLevel = self.parameters[paramName].getValue()
            elif paramName == 'log_rotaion_size':
                self.logRotationSize = self.parameters[paramName].getValue()
            elif paramName == 'max_log_size':
                self.logMaxSize = self.parameters[paramName].getValue()
            elif paramName == 'monitor_interval':
                self.monitorInterval = self.parameters[paramName].getValue()

        self.logger.info('The logging level is set to: %s' % self.logLevel)
        self.logger.info('The stop on error value is: %s' % self.stopOnError)
        if self.logRotationSize:
            self.logger.info('The log rotation size is: %s' % self.logRotationSize)
        if self.logMaxSize:
            self.logger.info('The max log size is: %s' % self.logMaxSize)

        yamlStatus = {
            'what': 'test_set',
            'id': self.testSet.getIdentity('id'),
            'name': self.testSet.name
        }
        tmpStatus = {
            'current_stage': 'pre',
            'current_running_test': 'pre_test_set'
        }
        yamlStatus['status'] = tmpStatus
        self.writeStatus(yamlStatus)
        yamlStatus.pop('status')

        # set the log level
        self.startMonitor()
        self.preTestSet()

        for testSetParamName in self.testSet.parameters:
            if testSetParamName == 'parallel':
                self.runTestInParallelFlag = self.testSet.parameters[testSetParamName].getValue()

        # concurrently singlly execution
        if self.runTestInParallelFlag is True:
            Log.IsMultithreading = True
            self.runTestsInParallel()
        else:
            self.runTests()

        tmpStatus = {
            'current_stage': 'post',
            'current_running_test': 'post_test_set'
        }
        yamlStatus['status'] = tmpStatus
        self.writeStatus(yamlStatus)
        self.postTestSet()
        self.__close_status_log_file()

    def timeLineLogInitial(self):
        """Create time images directory, and crushed into the image file
        """
        timeImgDstPath = os.path.join(Log.LogFileDir, 'TimeLine.html')
        timeLineFileName = os.path.join(Log.LogFileDir, 'TimeLine.html')

        controllerLink = "<a href='.\Controller---0.html'><font color=%s>View Controller Log %s</font></a>" % (
            'blue', '----NotRun')

        # todo Create time images directory, and crushed into the image file
        imagesList = ()
        import shutil
        if not os.path.exists(timeImgDstPath):
            os.makedirs(timeImgDstPath)

        for imgName in imagesList:
            path = os.path.split(os.path.realpath(__file__))[0]
            shutil.copy(os.path.join(path, 'RatsImgs', imgName), os.path.join(timeImgDstPath, imgName))

        self.timeLineLogFileHandler = open(timeLineFileName, 'w')
        self.writeCssStyleToTimeLog('0', controllerLink, 240)
        self.timeLineLogFileHandler.close()

    def setupTimeLog(self):
        """Open timeline log file
        """
        timeLineFileName = os.path.join(Log.LogFileDir, 'TimeLine.html')
        self.timeLineLogFileHandler = open(timeLineFileName, 'w')

    def setLogLevel(self, level):
        """To set the logger level at the console
        """
        set.logLevel = level

    @validate(flag=bool)
    def setStopOnConfigError(self, flag):
        """To set stopOnConfigError
        """
        self.configStopOnError = flag

    @validate(flag=bool)
    def setStopOnError(self, flag):
        """To set StopOnError
        """
        self.stopOnError = flag

    def __monitor(self, hosts, interval):
        """The monitor thread execution

        Args:
            hosts   (dict): key-value follow
                            id  (str): host id
                            host(instance): object
            interval(str) : the monitor data update interval, default is 180S
        """
        # Log.changeLogFile(None, 'Monitor')
        # monitor = HostMonitor()
        # monitor.startMonitor(hosts, interval)
        pass

    def startMonitor(self):
        """sed to monitor the execution of the performance data of the object
        """
        # monitorIntervalInSeconds = Units.getNumber(Units.convert(self.monitorInterval, 'S'))
        # if monitorIntervalInSeconds <= 0:
        #     return
        # cases = self.testCases
        # if len(cases) <= 0:
        #     return
        # phons = cases[0].resource.getAndroidPhone()
        # if phons:
        #     th = threading.Thread(target=self.__monitor, args=(phons, self.monitorInterval))
        #     th.setDaemon(True)
        #     th.start()
        pass

    def updateStatus(self):
        """To update the current test status
        """
        total = 0
        notRun = 0
        passed = 0
        failed = 0
        configError = 0
        running = 0
        killed = 0

        for case in self.testCases:
            if isinstance(case, Base):
                if case.caseStatus == TEST_STATUS.NOT_RUN:
                    notRun += 1
                elif case.caseStatus == TEST_STATUS.PASS:
                    passed += 1
                elif case.caseStatus == TEST_STATUS.FAILED:
                    failed += 1
                elif case.caseStatus == TEST_STATUS.RUNNING:
                    running += 1
                elif case.caseStatus == TEST_STATUS.KILLED:
                    killed += 1
                elif case.caseStatus == TEST_STATUS.CONFIG_ERROR:
                    configError += 1
        total = notRun + passed + failed + configError + running + killed

        fh = open(Log.LogFileDir + '\\status.js', 'w')
        fh.write('var stats = [{0}, {0}, {0}, {0}, {0}, {0}, {0}]\n'.format(
            total, passed, failed, configError, notRun, killed, running))
        fh.write('var testData = ['
                 '{label: \'Pass\', data: %s, color: \'green\'},'
                 '{label: \'Fail\', data: %s, color: \'red\'},'
                 '{label: \'ConfigError\', data: %s, color: \'blue\'},'
                 '{label: \'Not Run\', data: %s, color: \'yellow\'},'
                 '{label: \'Kill\', data: %s, color: \'orange\'},'
                 '{label: \'Running\', data: %s, color: \'#2ECCFA\'},'
                 ']' % (passed, failed, configError, notRun, killed, running))
        fh.close()

    def writeStatus(self, objectStatus):
        """Write the cases of state information to the yaml.xml file

        Args:
            objectStatus   (dict): format follow
                            objectStatus = {
                                'what': 'test_case|test_config|test_set',
                                'name': 'xxx',
                                'id': '1',
                                'status': {
                                    'current_stage': 'post' # The execution of the current stage, like 'post', 'post', 'main'
                                    'pre_status': 'PASS',
                                    'main_status': 'PASS',
                                    'post_status': 'PASS',
                                    'currently_running_test': None # 'what' is a set to save the current executing cases
                                    'duration': 10000,
                                    'last_step_logged': '',
                                    'process_id': 1000,
                                    'program_name': 'ATF'
                            }
        """

        if self.statusLogFileHandler:
            objectStatus['when'] = self.getTimeStamp()

            self.statusYamlLock.acquire()
            yaml.dump(objectStatus, self.statusLogFileHandler,
                      default_flow_style=False, explicit_start=True, explicit_end=True)
            self.statusYamlLock.release()

    def preTestSet(self):
        """operation interfaces before the test set executed
        """
        yamlStatus = {
            'what': 'test_set',
            'name': self.testSet.name,
            'id': self.testSet.getIdentity('id')
        }
        tmpStatus = {
            'current_stage': 'pre',
            'currently_running_test': 'pre_test_set'
        }

        try:
            self.logger.preSet('Pre-Test-Set start.')
            self.runHooks('beforePreTestSet')
        except ATException as e:
            tmpStatus['pre_status'] = TEST_STATUS.FAILED
            yamlStatus['status'] = tmpStatus
            self.writeStatus(yamlStatus)
            self.setTestSetError(True)
            self.logger.error('Pre-Test-Set failed because of the following error:\n%s' % e)
            self.postTestSet()
            self.logger.warn('Now Exit ATFramework')
            sys.exit(1)
        tmpStatus['pre_status'] = TEST_STATUS.PASS
        yamlStatus['status'] = tmpStatus
        self.writeStatus(yamlStatus)

    def postTestSet(self):
        """Operations after test set executed
        """
        yamlStatus = {
            'what': 'test_set',
            'name': self.testSet.name,
            'id': self.testSet.getIdentity('id')
        }
        tmpStatus = {
            'current_stage': 'post',
            'currently_running_test': 'post_test_set',
            'duration': '%sS' % str(time.time() - self.testSetStartTime)
        }

        if self.isTestSetError or self.stopOnError:
            self.testSet.setStatus(TEST_STATUS.INCOMPLETE)
            tmpStatus['main_status'] = TEST_STATUS.INCOMPLETE
        else:
            self.testSet.setStatus(TEST_STATUS.COMPLETE)
            tmpStatus['main_status'] = TEST_STATUS.COMPLETE
        yamlStatus['status'] = tmpStatus
        self.writeStatus(yamlStatus)
        try:
            Log.changeLogFile(Log.LogType.PostTestSet, 'Post_TestSet')
            self.logger.postSet('Post-Test-Set start...')
            self.testSet.runPostSetActions()
            self.runHooks('afterPostTestSet')
        except ATException as e:
            tmpStatus['current_stage'] = 'Done'
            tmpStatus['post_status'] = TEST_STATUS.FAILED
            tmpStatus['currently_running_test'] = 'done_test_set'
            yamlStatus['status'] = tmpStatus
            self.writeStatus(yamlStatus)
            self.logger.error('Post-Test-Set failed because: \n%s' % e)
            self.runHooks('afterPostTestSet')
        tmpStatus['current_stage'] = 'Done'
        tmpStatus['post_status'] = TEST_STATUS.PASS
        tmpStatus['currently_running_test'] = 'done_test_set'
        yamlStatus['status'] = tmpStatus
        self.writeStatus(yamlStatus)

    @staticmethod
    def releaseThreadHandle(th):
        """release the thread handle
        """
        th._Thread__started.Event__cond = None
        th._Thread__started = None
        th._Thread__stderr = None
        th._Thread__lock = None
        th.additonalInfo = None
        th.setReleaseFlag(True)

    def setCurrentlyRunningTest(self, case):
        """Set the performing the test case object of current Engine
        """
        self.currentRunningTest = case

    def runHooks(self, point):
        """run hooks
        """

        hooks = self.testSet.hooks
        if not hooks:
            return
        for hook in hooks:
            self.logger.info('====== Running Hook %s for HookPoint %s ======' % (str(hook), point))
            try:
                if hasattr(hook, point):
                    exec ('hook.%s()' % point)
            except Exception as e:
                self.logger.warn('Hook %s threw an exception but ATFramework will continue. \nError: %s'
                                 % (str(hook), traceback.format_exc()))
            self.logger.info('====== Hook %s Completed running for HookPoint %s ======' % (str(hook), point))
