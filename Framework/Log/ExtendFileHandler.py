# -*- coding: utf-8 -*-

"""
    Effect: log file controller
"""

import os
import logging
import logging.handlers
import LogFormat
from logging.handlers import RotatingFileHandler


class ExtendFileHandler(RotatingFileHandler):
    """log file controller, implement from RotatingFileHandler
    """

    def __init__(self, baseConfig, name, htmlHead, htmlTail):
        self.logFileExtension = '.html'
        self.baseLogFileName = os.path.abspath(os.path.join(baseConfig['logDir'], name))
        fileFullName = self.baseLogFileName + '---0' + self.logFileExtension
        RotatingFileHandler.__init__(self, fileFullName, maxBytes=baseConfig['size'] * 1024 * 1024,
                                     backupCount=baseConfig['count'], encoding='UTF-8')
        self.fileCount = 1

        formatter = logging.Formatter('%(html)s')
        self.setFormatter(formatter)
        self.setLevel(baseConfig['level'])
        self.htmlHead = htmlHead
        self.htmlTail = htmlTail

        if self.stream is None:
            self.stream = self._open()
        self.stream.write(self.htmlHead)
        self.flush()

    def doRollover(self):
        """override base class function, create new file when current file More than a specified value
        """

        if self.backupCount == -1 or self.fileCount < self.backupCount:
            newFileName = os.path.basename(self.baseLogFileName) + '---' + str(self.fileCount) + self.logFileExtension
            if self.stream:
                self.stream.write(LogFormat.logFormatDic['nextFileLink'].format(fileName=newFileName))
                self.stream.write(self.htmlTail)
                self.flush()
                self.stream.close()
                self.stream = None
            self.baseFilename = self.baseLogFileName + '---' + str(self.fileCount) + self.logFileExtension
            self.stream = self._open()

            self.stream.write(self.htmlHead)
            self.flush()
        self.fileCount += 1

    def releaseFileHandler(self):
        """release the file handler
        """
        try:
            self.acquire()
            if self.stream:
                self.stream.write(self.htmlTail)
            self.flush()
            self.close()
        except (IOError, ValueError):
            pass
        finally:
            self.release()
