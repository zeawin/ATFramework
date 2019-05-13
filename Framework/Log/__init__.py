# -*- coding: utf-8 -*-

"""
    Effect:
"""

import threading
import logging
import os
import datetime
import time
import shutil

import Enum
import LogFormat
from Framework.Utils.Units import Units
from LinkFilter import LinkFilter
from BaseLogger import BaseLogger
from Appender import Appender

ConsoleLogLevel = Enum.ConsoleLogLevel
FileLogLevel = Enum.FileLogLevel
LogType = Enum.LogType
LogFileDir = None
MainLogger = BaseLogger("Main")
MainAppender = None
logging.basicConfig(level=0, format='[%(asctime)-15s][%(thread)d][%(levelname)s] > %(message)s')
logging.getLogger().handlers[0].addFilter(LinkFilter())

baseConfig = {
    'logDir': os.path.join(os.getcwd(), datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')),
    'size': 10,
    'count': -1,
    'style': None,
    'isMultithreading': False,
    'localExecution': False,
    'logPath': None,
    'level': 'INFO'
}


def _replaceMethod(klass, oldMethodName, newMethod):
    """替换类方法"""
    method = getattr(klass, oldMethodName)
    setattr(klass, oldMethodName, (lambda self: newMethod(method, self)))


def _start(oldMethod, self):
    """为新线程添加 appender对象"""
    self.appender = threading.currentThread().appender
    return oldMethod(self)


def setupLogger(logPath, count=-1, size='10MB', localExecution=False, style=None, isMultithreading=False, level='INFO'):
    """初始化日志模块，为主线程添加appender对象"""
    baseConfig['logPath'] = logPath
    baseConfig['localExecution'] = localExecution
    if localExecution:
        baseConfig['logDir'] = os.path.abspath(logPath)
    else:
        baseConfig['logDir'] = os.path.abspath(
            os.path.join(logPath, datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')))

    baseConfig['isMultithreading'] = isMultithreading
    baseConfig['count'] = count
    baseConfig['size'] = Units.getNumber(Units.convert(size, 'MB'))
    baseConfig['style'] = style
    baseConfig['level'] = level
    global LogFileDir
    LogFileDir = baseConfig['logDir']

    # chushihua
    _initLog()


def _initLog():
    """初始化日志框架"""
    count = 0
    while True:
        try:
            count += 1
            os.mkdir(baseConfig['logDir'])
            break
        except WindowsError, e:
            if baseConfig['localExecution']:
                raise e
            if count > 5:
                raise e
            time.sleep(1)
            baseConfig['logDir'] = os.path.abspath(os.path.join(baseConfig['logPath'],
                                                                datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')))

    decorate = os.path.abspath('../Framework/Log/html/')
    for file in ['MainStyle.css', 'jquery-1.6.1.js', 'Main.js', 'echarts-all.js']:
        if file not in os.listdir(baseConfig['logDir']):
            try:
                shutil.copyfile(os.path.join(decorate, file), os.path.join(baseConfig['logDir'], file))
            except Exception:
                pass

    # 创建TestCase目录
    if not os.path.exists(os.path.join(baseConfig['logDir'], LogType.TestCase)):
        os.mkdir(os.path.join(baseConfig['logDir'], LogType.TestCase))
    # 设置自定义目录级别
    _addConsoleLogLevel()
    MainAppender = Appender(LogType.Main, 'Main_Rollup', baseConfig)
    # 当前线程添加appender
    threading.currentThread().appender = MainAppender
    MainLogger.setAppender(MainAppender)
    changeLogFile(LogType.PreTestSet, 'Pre_TestSet')
    # 重写Thread的Start方法
    _replaceMethod(threading.Thread, 'start', _start)


def changeLogFile(logType, fileName):
    """修改当前线程日志打印文件"""
    if not MainLogger:
        return

    if logType in LogType or logType is None:
        fileFullName = fileName
        if logType is Enum.LogType.TestCase:
            fileFullName = logType + '/' + fileName
        fileFullName = fileFullName.replace('.', '_')
        if fileFullName not in Appender._loggerDict:
            fileLink = fileFullName + '---0' + '.html'
            if logType is Enum.LogType.PreTestSet:
                MainLogger.preSet(LogFormat.fileLink.format(href=fileLink, msg=fileName))
            elif logType is Enum.LogType.PostTestSet:
                MainLogger.postSet(LogFormat.fileLink.format(href=fileLink, msg=fileName))
            elif not baseConfig['isMultithreading']:
                MainLogger.info(LogFormat.fileLink.format(href=fileLink, msg=fileName))
        appender = Appender(logType, fileFullName, baseConfig)
    else:
        raise Exception()

    threading.currentThread().appender = appender


def releaseFileHandler(logType, fileName):
    """释放日志文件句柄"""
    if logType in LogType:
        fileFullName = fileName
        if logType is Enum.LogType.TestCase:
            fileFullName = logType + '/' + fileName
        fileFullName = fileFullName.replace('.', '_')
        if fileFullName not in Appender._loggerDict:
            return
        else:
            logger = Appender._loggerDict[fileFullName]
            for handler in logger.handlers:
                handler.releaseFileHandler()
            logging.Logger.manager.loggerDict.pop(fileFullName)
            logger.handlers = []
            Appender._loggerDict.pop(fileFullName)
    else:
        raise Exception()


def getLogger(className):
    """获取baseLogger实例 """
    return BaseLogger(className)


def releaseResource():
    """释放日志文件资源"""
    Appender.releaseResource()


def changeConsoleLogLevel(logLevel):
    """修改控制台日志打印"""
    if logLevel not in ConsoleLogLevel:
        raise Exception()
    rootLogger = logging.getLogger()
    for handler in rootLogger():
        handler.setLevel(logLevel)


def _addConsoleLogLevel():
    """添加自定义的控制台日志级别"""
    logging.addLevelName(FileLogLevel.Trace, 'TRACE')
    logging.addLevelName(FileLogLevel.TcStatus, 'TC_STATUS')
    logging.addLevelName(FileLogLevel.TcStep, 'TC_STEP')
    logging.addLevelName(FileLogLevel.TcStart, 'TC_START')
    logging.addLevelName(FileLogLevel.Section, 'SECTION')
    logging.addLevelName(FileLogLevel.TcEnd, 'TC_END')
    logging.addLevelName(FileLogLevel.PreSet, 'PRE_SET')
    logging.addLevelName(FileLogLevel.PostSet, 'POST_SET')
    logging.addLevelName(FileLogLevel.Cmd, 'CMD')
    logging.addLevelName(FileLogLevel.CmdResponse, 'CMD_RESPONSE')
    logging.addLevelName(FileLogLevel.ConfigError, 'CONFIG_ERROR')
    logging.addLevelName(FileLogLevel.Fail, 'FAIL')
    logging.addLevelName(FileLogLevel.PassInfo, 'PASS')
