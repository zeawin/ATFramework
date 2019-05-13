# -*- coding: utf-8 -*-

"""
    Effect: Encapsulate logging
"""

import logging
import logging.handlers
import LogFormat
from ExtendFileHandler import ExtendFileHandler

class Appender(object):
    """
    """
    _loggerDict = {}

    def __init__(self, logType, fileName, baseConfig):
        htmlHead = LogFormat.formatHtmlHead(logType)
        htmlTail = LogFormat.logFormatDic['htmlTail']
        if fileName not in Appender._loggerDict:
            handler = ExtendFileHandler(baseConfig, fileName, htmlHead, htmlTail)
            logger = logging.getLogger(fileName)
            logger.addHandler(handler)
            logger.setLevel(1)
            Appender._loggerDict[fileName] = logger

        self._logger = Appender._loggerDict[fileName]
        self.logType = logType

    def getLogger(self):
        """To get the logging instance
        """
        return self._logger

    @staticmethod
    def releaseResource():
        """release logging instance
        """
        Appender._loggerDict = {}
        for (k, v) in logging.Logger.manager.loggerDict.items():
            if hasattr(v, 'handlers'):
                for handler in v.handlers:
                    if isinstance(handler, ExtendFileHandler):
                        handler.acquire()
                        try:
                            if handler.stream:
                                handler.stream.write(handler.htmlTail)
                                handler.flush()
                        finally:
                            handler.release()
                v.handlers=[]
        logging.shutdown()
        logging.Logger.manager.loggerDict = {}