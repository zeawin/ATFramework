#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
The start
"""

import argparse
import os
import re
import sys
from argparse import RawDescriptionHelpFormatter
from xml.etree.ElementTree import ParseError

getAbsPath = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


def __getLibAbsPath(currentPath, depth):
    """ Get an absolute path relative depth
    """
    libPath = currentPath
    while depth:
        libPath = os.path.split(libPath)[0]
        depth -= 1
    return libPath


def initLibPath():
    """init Lib Path. append lib path into python path.
    """
    libHash = {
        'Framework': 1,
        'UserControlleLib': 1,
        'CaseLib': 1
    }

    binPath = os.path.split(os.path.realpath(__file__))[0]

    for key in libHash:
        sys.path.append(os.path.join(__getLibAbsPath(binPath, libHash[key]), key))


from Framework import Log
from Framework.Engine.Engine import Engine
from Framework.Engine.Set import Set
from Framework.Engine.XMLTags.TestSet import TEST_PARAM
from Framework.Exception import ATException
from Framework.Utils.Codec import convertToUtf8
from Framework.Utils.Units import Units
from Framework.Utils.XMLParser import XMLParser
from Framework.Engine.XMLTags.MainConfig import WORKSPACE, MAIN_CONFIG
from UserControlLib.Resource import Resource

if sys.version_info >= (3, 0):
    raise RuntimeError("You need python 2.7 for ATFramework.")

__author__ = "Automation"
__date__ = "20160330"
__version__ = "1.0"
__version_info__ = (2, 0, 0, 1)
__License__ = "public"


def __updateOptions(args):
    """解析并更新mainCOnfig数据
    """

    mainConfig = {}
    args.workspace = re.sub(r'[\/]$', "", args.workspace)
    if args.configFile and args.workspace:
        try:
            args.configFile = os.path.join(args.workspace, args.configFile)

            mainConfigRawData = XMLParser.getXMLData(args.configFile)

            mainConfig = XMLParser.getSpecifiedKeyRawData(mainConfigRawData, MAIN_CONFIG.OPT)

            if MAIN_CONFIG.TESTBED_FILE in mainConfig:
                mainConfig[MAIN_CONFIG.TESTBED_FILE] = os.path.join(args.workspace,
                                                                    mainConfig[MAIN_CONFIG.TESTBED_FILE])

            mainConfig[MAIN_CONFIG.TEST_SET_FILE] = os.path.join(args.workspace,
                                                                 mainConfig[MAIN_CONFIG.TEST_SET_FILE])

            mainConfig[MAIN_CONFIG.LOCAL_EXECUTION_LOG_PATH] = os.path.join(args.workspace, mainConfig[
                MAIN_CONFIG.LOCAL_EXECUTION_LOG_PATH])

        except (ATException, IOError, AttributeError, ParseError):
            print ("ERROR: The Specified Main Configuration File: '%s'\n"
                   "Dose Not Exist Or File Is Not The Correct Xml File!" % args.configFile)
            sys.exit(1)
    else:
        print "WARNING: Please Specify The MainConfig File! " \
              "Use 'python ATFStart.py -h' To Show Detail Information. "
        sys.exit(1)

    # update mainConfig

    if WORKSPACE not in mainConfig and args.workspace:
        mainConfig[WORKSPACE] = args.workspace

    if args.testBedFile and args.workspace:
        mainConfig[MAIN_CONFIG.TESTBED_FILE] = os.path.join(args.workspace, args.testBedFile)

    if MAIN_CONFIG.TESTBED_FILE in mainConfig and not os.path.isfile(mainConfig[MAIN_CONFIG.TESTBED_FILE]):
        print ("ERROR: The Specified Testbed File: '%s' Not Be Found!" % mainConfig[MAIN_CONFIG.TESTBED_FILE])
        sys.exit(1)

    if args.testSetFile and args.workspace:
        mainConfig[MAIN_CONFIG.TEST_SET_FILE] = os.path.join(args.workspace, args.testSetFile)

    if MAIN_CONFIG.TEST_SET_FILE in mainConfig and not os.path.isfile(mainConfig[MAIN_CONFIG.TEST_SET_FILE]):
        print ("ERROR: The Specified Testset File: '%s' Not Be Found!" % mainConfig[MAIN_CONFIG.TEST_SET_FILE])
        sys.exit(1)

    if MAIN_CONFIG.LOCAL_EXECUTION_LOG_PATH in mainConfig and not os.path.exists(
            mainConfig[MAIN_CONFIG.LOCAL_EXECUTION_LOG_PATH]):
        print ("WARNING: The Specified Local Exception Log Path: '%s' Not Be Found!" % mainConfig[
            MAIN_CONFIG.LOCAL_EXECUTION_LOG_PATH])

        os.makedirs(mainConfig[MAIN_CONFIG.LOCAL_EXECUTION_LOG_PATH])
        print (
            "INFO: Create Specified Local Base Log Path: '%s' Success. " % mainConfig[
                MAIN_CONFIG.LOCAL_EXECUTION_LOG_PATH])

    return mainConfig


def __setParam(toParamList, fromParam):
    """公共函数，字典或者列表的参数处理
    """

    if not isinstance(fromParam, list):
        toParamList.append(fromParam)
    else:
        toParamList.extend(fromParam)

    return toParamList


def __createTestCaseObject(testSetInfo, logger, resourceObject):
    """创建测试对象
    """

    testRawData = []
    tmpTestRawData = None

    if TEST_PARAM.TESTS in testSetInfo and TEST_PARAM.TEST in testSetInfo[TEST_PARAM.TESTS] and \
            testSetInfo[TEST_PARAM.TESTS][TEST_PARAM.TEST]:
        tmpTestRawData = testSetInfo[TEST_PARAM.TESTS][TEST_PARAM.TEST]

    if isinstance(tmpTestRawData, dict):
        testRawData.append(tmpTestRawData)
    elif isinstance(tmpTestRawData, list):
        testRawData.extend(tmpTestRawData)

    if len(testRawData):
        pass
    else:
        logger.error("There were no tests specified to be executed.")
        sys.exit(1)

    testId = 0
    INSTANCE_ID = "instance_id"
    order = 0
    testCasesObjects = []

    for testInfo in testRawData:
        if 'run' in testInfo and '0' == testInfo['run']:
            logger.info(
                "Test case location: '%s', test case name: '%s' is removed." % (testInfo['location'], testInfo['name']))
            continue
        order += 1
        instanceId = None
        if INSTANCE_ID in testInfo and testInfo[INSTANCE_ID]:
            instanceId = testInfo[INSTANCE_ID]

        # 测试名字为测试用例的文件名， 也等于测试类名， 测试路径等于测试相对的模块路径，创建对象时使用这两个变量

        testName = testInfo[TEST_PARAM.NAME]
        testLocation = testInfo[TEST_PARAM.LOCATION]
        testCaseModule = re.sub(r'[\\|/]', ".", testLocation)

        # 检查并设置测试参数
        customParams = []
        if TEST_PARAM.PARAMETERS in testInfo and TEST_PARAM in testInfo[TEST_PARAM.PARAMETERS]:
            customParams = __setParam(customParams, testInfo[TEST_PARAM.PARAMETERS][TEST_PARAM.PARAM])

        # 用于test case全局参数赋值

        globalTestCaseParams = __generateGlobalTestCaseParameter(testSetInfo)
        if globalTestCaseParams:
            for globalParam in globalTestCaseParams:
                for customParam in customParams:
                    if globalParam["name"] == customParam["name"] and \
                            ('override' not in customParam or re.match(r'0|false|no', customParam['override'], re.I)):
                        customParam['value'] = globalParam['value']
        # configParams
        configParams = []
        if "config_params" in testInfo and TEST_PARAM.PARAM in testInfo["config_params"]:
            configParams = __setParam(configParams, testInfo['config_params'][TEST_PARAM.PARAM])

        # configParams
        deConfigParams = []
        if "deConfig_params" in testInfo and TEST_PARAM.PARAM in testInfo["deConfig_params"]:
            deConfigParams = __setParam(deConfigParams, testInfo['deConfig_params'][TEST_PARAM.PARAM])

        # identities
        testIdentites = {"identity": []}
        if "identities" in testInfo and "identity" in testInfo["identities"]:
            testIdentites["identity"] = __setParam(testIdentites["identity"], testInfo["identities"]["identity"])
        # else:
        #     testId += 1
        #     idString = "TEST_ID_" + str(testId)
        #     testIdentites["identity"] = [{"name": "id", "value": idString}]

        # test dependencies
        testDependencies = {"dependencies": []}
        if "dependencies" in testInfo and "dependency" in testInfo["dependencies"]:
            testDependencies = __setParam(testDependencies["dependencies"], testInfo["dependencies"]["dependency"])
        else:
            testDependencies = None

        testDescription = None
        if "desription" in testInfo and "dependency" in testInfo["desription"]:
            testDependencies = testInfo["desription"]

        testTags = []
        if "tags" in testInfo and testInfo["tags"]:
            if "tag" in testInfo["tags"] and testInfo["tags"]["tag"]:
                testTags = testInfo["tags"]["tag"]

        requiredEquipment = []
        if "required_equipment" in testInfo and testInfo["required_equipment"]:
            requiredEquipment = testInfo["required_equipment"]

        shareableEquipment = None
        if "shareable_equipment" in testInfo and testInfo["shareable_equipment"]:
            shareableEquipment = testInfo["shareable_equipment"]

        stepsToPerform = []
        if "steps_to_perform" in testInfo and testInfo["steps_to_perform"]:
            stepsToPerform = testInfo["steps_to_perform"]

        ####
        customParams = convertToUtf8(customParams)
        # 创建测试对象
        param = {"name": testName,
                 "location": testLocation,
                 "params": customParams,
                 "instance_id": instanceId,
                 "identities": testIdentites,
                 "dependencies": testDependencies,
                 "order": order,
                 "resource": resourceObject,
                 "description": testDescription,
                 "tags": testTags,
                 "deConfig_params": deConfigParams,
                 "config_params": configParams,
                 "steps_to_perform": stepsToPerform,
                 "required_equipment": requiredEquipment,
                 "shareable_equipment": shareableEquipment}
        tcObjCreateFailedFlag = False
        errorMsg = None
        try:
            __import__(testCaseModule)
            tcObj = getattr(sys.modules[testCaseModule], testName)(param)
            testCasesObjects.append(tcObj)
        except Exception, errorMsg:
            tcObjCreateFailedFlag = True

        if tcObjCreateFailedFlag is True:
            logger.error("Unable To Create The Test Case Object For: %s \n" % testName, errorMsg)
            sys.exit(1)

    return testCasesObjects


def __createLogParam(executionparam, mainConfigData, testSetInfo, testSetName):
    """创建日志参数
    """

    maxLogSize = 0
    loggerParams = {}
    supportAbnormalSp = 0

    # 设置log size
    for userParam in executionparam:
        if userParam["name"] == "log_rotation_size":
            loggerParams["size"] = userParam["value"]

        if userParam["name"] == "RANDOM_NEGATIVE_CLI" and userParam["value"]:
            pass

        if userParam["name"] == "SUPPORT_ABNORMAL_SP" and userParam["name"]:
            supportAbnormalSp = 1 if userParam["value"] else 0

        if userParam["name"] == "MAX_LOG_SIZE":
            maxLogSize = userParam["value"]

        if userParam["name"] == "logging_level" and userParam["value"]:
            loggerParams["logging_level"] = userParam["value"]

    maxLogSizeNum = Units.getNumber(Units.convert(maxLogSize, "B")) if maxLogSize else 0

    if "size" not in loggerParams:
        loggerParams["size"] = "10MB"

    rotationSizeNum = Units.getNumber(Units.convert(loggerParams["size"], "B"))

    # 设置log count
    if not maxLogSize:
        loggerParams["count"] = -1
    elif maxLogSizeNum < rotationSizeNum:
        loggerParams["count"] = 1
    else:
        loggerParams["count"] = (maxLogSize / rotationSizeNum) + 1

    # 设置log path & log type
    # if "local_execution_log_path" in mainConfigData and mainConfigData['local_execution_log_path']:
    logPath = mainConfigData["local_execution_log_path"]
    logPathType = "LOCAL_EXECUTION"
    loggerParams['logPath'] = logPath
    loggerParams['type'] = logPathType

    # 设置log style
    style = None
    if "test_set_parameters" in testSetInfo and "parameter" in testSetInfo["test_set_parameters"]:
        for param in testSetInfo["test_set_parameters"]["parameter"]:
            if param["name"] == "parallel" and param["value"]:
                style = "parallel"
                break

    loggerParams['style'] = style
    return loggerParams


def __createTestSetObject(testSetInfo, testSetName, tcObjects, buildParameters, hookObjects):
    """创建测试套
    """

    testSetIds = []
    tsIds = []
    if "identities" in testSetInfo and "identity" in testSetInfo["identities"]:
        tsIds = __setParam(tsIds, testSetInfo["identities"]["identity"])
        for key in tsIds:
            testSetIds[key["name"]] = key["id"]
    else:
        testSetIds = None

    # 创建件对象时设置对象的名称，每个对象原有的名称后面加上对象在列表中的index
    # 使得在单次并发和并发循环执行时name不同

    # 若不存在相同的用例则不需要修改名字，如果存在则重命名，命名方式为原名称后面加——与数字的组合

    tmp = {}
    for tc in tcObjects:
        if tc.name in tmp:
            tmp[tc.name].append(tc)
        else:
            tmp[tc.name] = [tc]

    for name in tmp:
        if len(tmp[name]) > 1:
            objectNum = 0
            for tmpTc in tmp[name]:
                tmpTc.setTestCasename(tmpTc.name + "_" + str(objectNum))
                objectNum += 1

    # 创建测试套Parameter
    testSetParams = []
    if "test_set_parameters" in testSetInfo and "parameter" in testSetInfo["test_set_parameters"]:
        testSetParams = __setParam(testSetParams, testSetInfo["test_set_parameters"]["parameter"])

    testSetDir = Log.LogFileDir
    testSetCustomParams = {"name": testSetName,
                           "identities": testSetIds,
                           "test_set_params": testSetParams,
                           "tests": tcObjects,
                           "hooks": hookObjects,
                           "log_dir": testSetDir,
                           "build_params": buildParameters}
    return Set(testSetCustomParams)


def __generateGlobalTestCaseParameter(testSetInfo):
    """获取测用例的全局Parameter
    """
    globalTestCaseParams = []
    if "general_test_case_parameters" in testSetInfo and "param" in testSetInfo['general_test_case_parameters']:
        globalTestCaseParams = __setParam(globalTestCaseParams, testSetInfo["general_test_case_parameters"]["param"])
    return globalTestCaseParams


def __setTestSetName(testSetInfo):
    """设置测试套名称
    """
    if "name" in testSetInfo and testSetInfo["name"]:
        testSetName = testSetInfo["name"]
        return testSetName
    else:
        return None


def __setExecutionParams(mainConfigData):
    """设置测试执行参数
    """
    executionParams = []
    if "execution_parameters" in mainConfigData and mainConfigData["execution_parameters"] \
            and "param" in mainConfigData["execution_parameters"] and mainConfigData["execution_parameters"]["param"]:
        executionParams = __setParam(executionParams, mainConfigData["execution_parameters"]["param"])

    return executionParams


def __createTestEngine(tcObjects, testSetObject, executionParams, logger):
    """创建测试引擎
    """
    engineObject = None
    engineType = "standard"
    # parallel = testSetObject.getParameter('parallel')['parallel']

    # if parallel:
    # 	for tc in tcObjects:
    # 		if isinstance(tc, RatsCase):
    # 			engineType = "rats"
    # 			break

    if engineType == "standard":
        logger.info("Running Test Set with the Standard Engine.")
        engineParams = {"test_set": testSetObject,
                        "params": executionParams}
        engineObject = Engine(engineParams)

    # if engineType == "rats":
    # 	logger.info("Running Test Set with the Rats Engine. ")
    # 	engineParams = {"test_set": testSetObject,
    # 					"params": executionParams}
    # 	engineObject = RatsEngine(engineParams)
    # 	Log.IsMultithreading = True

    return engineObject


def __createHookObject(testSetInfo, logger, resourceObject):
    """创建测试套中配置hook对象
    """
    tmpHooks = []
    if "hooks" in testSetInfo and "hook" in testSetInfo["hooks"]:
        tmpHooks = __setParam(tmpHooks, testSetInfo["hooks"]["hook"])

    tmpTestCaseGeneralParam = []
    if "general_test_case_parameters" in testSetInfo \
            and "param" in testSetInfo["general_test_case_parameters"]["param"]:
        tmpTestCaseGeneralParam = __setParam(tmpTestCaseGeneralParam,
                                             testSetInfo["general_test_case_parameters"]["param"])

    hookObjects = []
    hookFaild = False
    for hookInfo in sorted(tmpHooks, key=lambda hook: hook["id"]):
        location = hookInfo.get("location")
        hookName = hookInfo.get("name")
        hookModule = re.sub(r'[\\|/]', ".", location)
        param = []
        if "parameters" in hookInfo and "param" in hookInfo["parameters"]:
            params = __setParam(param, hookInfo["parameter"]["param"])

        localParamDict = {}
        for localParam in param:
            localParamDict[localParam["name"]] = localParam

        for globalParam in tmpTestCaseGeneralParam:
            if globalParam["name"] not in localParamDict:
                localParamDict[globalParam["name"]] = globalParam
            elif "override" in globalParam and globalParam["override"]:
                tmpDict = globalParam
                tmpDict.pop("override")
                localParamDict[tmpDict['name']] = tmpDict
        param = localParamDict.itervalues()

        try:
            __import__(hookModule)
            hookObj = getattr(sys.modules[hookModule], hookName)({"resource": resourceObject, "params": param})

            hookObjects.append(hookObj)
        except Exception, errorMsg:
            hookFaild = True
            logger.error("Unable to import %s module "
                         "or Unable to create the Hook object for %s.\n%s" % (hookModule, hookModule, errorMsg))

        if hookFaild:
            logger.error("Please check the log file for further details..")
            logger.warn("ATFramework will be Exit Now.")
            sys.exit(1)

        return hookObjects


def execute(mainConfigData):
    """测试执行主函数
    """
    testBedInfo = []
    if "testbed_file" in mainConfigData:
        testBedInfo = XMLParser.getXMLData(getAbsPath(mainConfigData["testbed_file"]))['testbedinfo']

    testSetRawInfo = XMLParser.getXMLData(getAbsPath(mainConfigData["test_set_file"]))
    testSetInfo = testSetRawInfo["opt"]["test_set"]

    testSetName = __setTestSetName(testSetInfo)
    buildParameters = None

    executionParams = __setExecutionParams(mainConfigData)

    customLogParams = __createLogParam(executionParams, mainConfigData, testSetInfo, testSetName)

    Log.setupLogger(customLogParams["logPath"], count=customLogParams["count"], size=customLogParams["size"],
                    localExecution=False, style=customLogParams['style'], level=customLogParams['logging_level'])

    logger = Log.getLogger("ATFramework-start")

    try:
        logger.info("Start Creating All The Objects Under Test Defined In The Testbed..")
        resourceObject = Resource(testBedInfo)
    except Exception, errorMsg:
        logger.error("Create Objects Under Test Defined In The Testbed Failed. \n", errorMsg)
        sys.exit(1)

    if resourceObject.getInitErrors():
        sys.exit(1)

    logger.passInfo("Create Resource Success Complete.")

    # 创建测试用例对象
    # logger.info("Start Creating All The Test Case Objects Defined In The TestSet ...")
    tcObjects = __createTestCaseObject(testSetInfo, logger, resourceObject)
    logger.passInfo("Create Test Case Success Complete.")
    hookObjects = []
    # 创建测试套对象
    try:
        logger.info("Start Create Test Set Object ...")
        testSetObject = __createTestSetObject(testSetInfo, testSetName, tcObjects, buildParameters, hookObjects)
    except Exception, errorMsg:
        logger.trace("Create Test Set Failed: ", errorMsg)
        sys.exit(1)
    logger.passInfo("Create Test Set Success Complete.")
    # 创建控制器对象
    try:
        logger.info("Start Create Test Engine Object ...")
        engineObject = __createTestEngine(tcObjects, testSetObject, executionParams, logger)
    except Exception, errorMsg:
        logger.error("Unable to create the Test Engine. object:", errorMsg)
        sys.exit(1)
    logger.passInfo("Create Test Engine Success Complete.")
    resourceObject.setTestEngine(engineObject)

    # hookObjects = __createHookObject(testSetInfo, logger, resourceObject)
    #
    # testSetObject.addHooks(hookObjects)

    # 执行测试
    testFailFlag = False

    if engineObject:
        try:
            logger.info("Start Run Test Set ....")
            engineObject.runTestSet()
        except Exception, errorMsg:
            testFailFlag = True
            engineObject.postTestSet()
            logger.error("Error Occurred While Running The Test Set: \n%s", errorMsg)
            Log.releaseResource()
            sys.exit(1)

    if not testFailFlag:
        logger.passInfo("Test Set Running Complete.")
        Log.releaseResource()
        failed = False

        for test in testSetObject.testCases:
            if re.match(r'Fail|ConfigError|Kill|Incomplete|NotRun', test.caseStatus, re.IGNORECASE):
                failed = True
                break
        if not failed:
            logger.info("All Test Cases Executed.")
            sys.exit(0)
        else:
            logger.warn("Part of Test Cases Failed. Please Check Log message.")
            sys.exit(1)


def useAge():
    """参数接收
    """

    msg = ("\n"
           "	\n"
           "	 =========================================\n"
           '     *              ATFramework              *\n'
           "	 =========================================\n"
           "	\n"
           "	\n"
           "	")
    print(msg)
    workPath = os.path.split(os.path.realpath(__file__))[0]

    parser = argparse.ArgumentParser(description=msg, formatter_class=RawDescriptionHelpFormatter)

    parser.add_argument("-c", "--configFile",
                        dest="configFile",
                        help="- (required) The main test configuration file.")

    parser.add_argument("-tb", "--testBedFile",
                        dest="testBedFile",
                        help="- The Testbed xml file.")

    parser.add_argument("-ts", "--testSetFile",
                        dest="testSetFile",
                        help="- The testSetFile xml file.")

    parser.add_argument("-lb", "--localBaseLogPath",
                        dest="localBaseLogPath",
                        help="- The local base log path.")

    parser.add_argument("-le", "--localExecutionLogPath",
                        dest="localExecutionLogPath",
                        help="- The local execution log path.")

    parser.add_argument("-v", "--version",
                        help="- The version of UniAuto installed.",
                        action="store_true")

    parser.add_argument("-u", "--useCryptoLock",
                        dest="useCryptoLock",
                        help="- Force Command::Sah to lock around all Net::SSH2 API calls.")

    parser.add_argument("-nu", "--nouseCryptoLock",
                        dest="nouseCryptoLock",
                        help="- Opposite of above.")

    parser.add_argument("-w", "--workspace",
                        dest="workspace",
                        help="- The workspace path.",
                        default=workPath)

    args = parser.parse_args()

    if args.version:
        print("ATFramework Version:%s" % __version__)
        sys.exit(0)

    return __updateOptions(args)


if __name__ == '__main__':
    mainConfigInfo = useAge()
    execute(mainConfigInfo)
