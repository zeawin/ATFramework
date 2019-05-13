# -*- coding: utf-8 -*-

import traceback


class ATException(Exception):
    def __init__(self, msg=None):
        if msg:
            self.message += (msg + '\n' + traceback.format_exc())
        else:
            self.message += traceback.format_exc()

    def __str__(self):
        return self.message
