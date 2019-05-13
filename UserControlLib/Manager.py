# -*- coding: utf-8 -*-

import sys
import re
from Framework.Exception import ATException
from Framework import Log


class Manager(object):
    Pool = {}
    logger = Log.getLogger(__name__)

    def __init__(self, instance):
        self.page = {}
        Manager.Pool[instance] = self

    def __new__(cls, instance):
        if instance in Manager.Pool:
            cls.logger.debug('There is a Manager instance already exist for [%s], return the exists Manager instance.'
                             % str(instance))
            return Manager.Pool[instance]
        return super(Manager, cls).__new__(cls, instance)

    def getSpecPage(self, phone, title):

        # TODO 版本处理
        if title not in self.page:
            matcher = re.match('([a-z]+)_(.*)$', title, re.I)
            if matcher:
                name = matcher.groups()[0]
            else:
                name = title
            package = 'UserControlLib.Page.Page.%s' % name
            __import__(package)
            module = sys.modules[package]
            className = getattr(module, name)
            pageObj = className(phone, title)
            if pageObj:
                self.page[title] = pageObj
            else:
                raise ATException('Generate %s page instance failed' % title)

        if not self.page[title]:
            raise ATException('Generate or get page instance failed')

        return self.page[title]
