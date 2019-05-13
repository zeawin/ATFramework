# -*- coding: utf-8 -*-

"""
Effect :
"""

import threading
import ctypes
import random
from multiprocessing.dummy import Pool as ThreadPool
import traceback
from Framework.Exception import ATException
from Framework import Log


class Threads(threading.Thread):
    """defined Threads to process multiple
    Args:
        name    (str)       : Threads name
        args    (dict)      : Parameters of the callback function
        function(function)  : The specific excute function in the thread
    Example:
        def sign(a):
            print a
        th = Threads(sign, name='ss', a=2)
    """
    # id list, Used to hold assigned id, to avoid be repeated
    thIDList = []
    logger = Log.getLogger(__name__)
    def __init__(self, function, name, **args):
        threading.Thread.__init__(self, name=name)

        self.id = random.randrange(1E6)
        while self.id in Threads.thIDList:
            self.id = random.randrange(1E6)
        Threads.thIDList.append(self.id)

        self.callback = function
        self.kwargs = args

        self.case = self.kwargs.get('case') if self.kwargs.get('case') else self.kwargs.get('ratscase')

        self.errorMsg = ''
        self.released = False
        self.result = None

    def setReleaseFlag(self, flag):
        """set the release flag value
        """
        self.released = flag

    def run(self):
        """run function to excute self.callback
        """
        try:
            self.ret = self.callback(**self.kwargs)
        except:
            self.errorMsg = traceback.format_exc()

    def _raiseExc(self, excp):
        """stop this thread
        """
        if not self.isAlive():
            raise ATException('Thread must be started.')
        _asyncRaise(self.ident, excp)

    def kill(self):
        """stop this thread by SystemExit
        """
        self._raiseExc(SystemExit)

    @classmethod
    def waitThreadsComplete(cls, thList):
        """wait for all the specified complete
        """
        if not isinstance(thList, list):
            raise ATException('Param thList must be a list, but get %s' % type(thList))
        for th in thList:
            if isinstance(th, Threads):
                if th.isAlive():
                    th.join()
            else:
                cls.logger.warn('The input parameter: [%s], type: [%s], is not Threads' % (th, type(th)))

def _asyncRaise(tid, excp):
    """stop this thread by ctypes
    """
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(excp))
    if res == 0:
        raise ATException('thread id [%s] does not exist' % ctypes.c_long(tid))

    elif res > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise ATException('PyThreadState_SetAsyncExc failed.')

def multiOperation(func, iterator, processes=None, chunkSize=None):
    """called methods by the thread pool to deal with the data of the iterator
    Args:
        func        (function)  : The callback function
        iterator    (iterable)  : An iterator
        processes   (int)       : The process count
        chunkSize   (int)       : The iterator's step
    """
    pool = ThreadPool(processes)
    ret = pool.map(func, iterator, chunkSize)
    pool.close()
    pool.join()
    return ret
