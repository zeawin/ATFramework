# -*- coding: utf-8 -*-

"""
    Effect: BaseLogger, provide the union function
"""

import threading
import datetime
import cgi
import LogFormat
import logging
import re
import traceback
import sys
import pprint
import cStringIO
from Enum import FileLogLevel


class BaseLogger(object):
    """The BaseLogger
    """

    def __init__(self, className, appender=None):
        self.className = className
        self.appender = appender

    def setAppender(self, appender):
        self.appender = appender

    def info(self, *args):
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Info, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def tcStart(self, *args):
        """print the Test Start tag
        """
        if not args:
            args = ('TestCase Start', )
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.TcStart, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def tcEnd(self, *args):
        """print the Test End tag
        """
        if not args:
            args = ('TestCase End', )
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.TcEnd, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def error(self, *args):
        """print the error information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Error, msg)}
        self._log().log(FileLogLevel.Error, msg, extra=html)
        Log = __import__('Framework').Log
        if Log.MainAppender:
            Log.MainAppender.getLogger().log(FileLogLevel.Error, msg, extra=html)

    def exception(self, *args):
        """print the exception information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Error, msg)}
        self._log().log(FileLogLevel.Error, msg, extra=html)

    def warn(self, *args):
        """print the warn information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Warn, msg)}
        self._log().log(FileLogLevel.Warn, msg, extra=html)

    def debug(self, *args):
        """print the warn information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Debug, msg)}
        self._log().log(FileLogLevel.Debug, msg, extra=html)

    def cmd(self, *args):
        """print the cmd information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Cmd, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def cmdResponse(self, *args):
        """print the cmd response information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Cmd, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def passInfo(self, *args):
        """print the pass information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.PassInfo, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def fail(self, *args):
        """print the pass information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Fail, msg)}
        self._log().log(FileLogLevel.Error, msg, extra=html)

    def configError(self, *args):
        """print the config_error information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.ConfigError, msg)}
        self._log().log(FileLogLevel.Error, msg, extra=html)

    def tcStep(self, *args):
        """print the test step information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.TcStep, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def tcStatus(self, *args):
        """print the test status information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.TcStatus, msg)}
        self._log().log(FileLogLevel.TcStatus, msg, extra=html)

    def trace(self, *args):
        """print the trace information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.Trace, msg)}
        self._log().log(FileLogLevel.Debug, msg, extra=html)

    def preSet(self, *args):
        """print the pre set information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.PreSet, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def postSet(self, *args):
        """print the post set information
        """
        msg = self.__formatParameter(*args)
        html = {'html': self._formatLogMsg(FileLogLevel.PostSet, msg)}
        self._log().log(FileLogLevel.Info, msg, extra=html)

    def _log(self):
        """To get the Appender.logging in current thread
        """
        if self.appender:
            return self.appender.getLogger()
        if hasattr(threading.currentThread(), 'appender'):
            return threading.currentThread().appender.getLogger()
        else:
            return logging.getLogger()

    def _formatLogMsg(self, level, msg):
        """To format the log. Add timestamp and trace
        """

        if level not in FileLogLevel:
            raise Exception
        parameterDic = {
            'level': logging.getLevelName(level),
            'timestamp': datetime.datetime.now().strftime(LogFormat.timeFormat)[0:23],
            'className': self.className,
            'threadID': threading.currentThread().ident
        }
        pattern = re.compile('<a .+>.+</a>', re.I)

        if not pattern.search(msg):
            parameterDic['msg'] = cgi.escape(msg)
        else:
            parameterDic['msg'] = msg
        traceList = []
        traceStack = traceback.extract_stack()

        traceStack.reverse()

        lineno= traceStack[2][1]

        parameterDic['lineno'] = lineno

        for trace in traceStack[2:]:
            traceDic = dict(zip(LogFormat.traceDicFormat, trace))
            traceList.append(LogFormat.traceFormat.format(**traceDic))
        trace = '\n'.join(traceList)
        parameterDic['trace'] = trace.replace('"', '\'')
        return unicode(LogFormat.logFormatDic['general'].format(**parameterDic),
                       'UTF-8', errors='replace')

    def formatException(self):
        try:
            ei = sys.exc_info()
            if None not in ei:
                sio = cStringIO.StringIO()
                traceback.print_exception(ei[0], ei[1], ei[2], None, sio)
                s = sio.getvalue()
                sio.close()
                if s[-1:] == '\n':
                    s = s[:-1]
                return s
            else:
                return ''
        finally:
            del ei

    def __formatParameter(self, *args):
        exception = None
        msg = ''
        for parameter in args:
            if isinstance(parameter, Exception):
                exception = parameter
                continue
            elif isinstance(parameter, dict) or isinstance(parameter, list):
                msg += pprint.pformat(parameter)
            elif isinstance(parameter, unicode):
                msg += parameter.encode('UTF-8', errors='replace')
            else:
                msg += str(parameter)
        if exception:
            msg += self.formatException()
        return msg