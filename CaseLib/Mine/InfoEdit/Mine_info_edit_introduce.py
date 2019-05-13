# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Mine_info_edit_introduce(Case):
    """
    Description:
        编辑个人简介
    preHandle:
        1.进入我的-首页，进入资料编辑页面；
        2.点击个人简介，进入个人简介页面；
    testHandle:
        1.点击返回，能正常返回到资料编辑页面；
        2.进入个人简介页面，输入简介信息，点击返回，再次进入简介页面，简介信息未变动。
        3.输入简介信息，点击保存，返回编辑资料页面，简介信息已改动变动。
    """

    def preHandle(self):
        self.logStep('1.进入我的-首页，进入资料编辑页面')
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.phone.doAction(alias='mine', action='click')
        self.phone.doAction(alias='info_edit', action='click')

        self.logStep('2.点击个人简介，进入个人简介页面')
        self.phone.doAction(alias='acc_intro', action='click')

    def testHandle(self):

        self.logStep('1.点击返回，能正常返回到资料编辑页面。')
        self.phone.doAction(alias='back', action='click')

        self.logStep('2.进入个人简介页面，输入简介信息，点击返回，再次进入简介页面，简介信息未变动')
        self.phone.doAction(alias='acc_intro', action='click')
        import time
        text = str(time.time())
        self.phone.doAction(alias='intro_info', action='input', value=text)
        self.phone.doAction(alias='back', action='click')
        self.phone.doAction(alias='acc_intro', action='click')
        if self.phone.getSpecElementText(alias='intro_info') != text:
            self.logger.passInfo('返回后，再次进入简介页面，简介信息未变动')
        else:
            raise ATException('返回后，再次进入简介页面，简介信息已经变动')

        self.logStep('3.输入简介信息，点击保存，返回编辑资料页面，简介信息已改动变动')
        self.phone.doAction(alias='intro_info', action='input', value=text)
        self.phone.doAction(alias='commit', action='click')
        self.phone.doAction(alias='acc_intro', action='click')
        if self.phone.getSpecElementText(alias='intro_info') == text:
            self.logger.passInfo('返回后，再次进入简介页面，简介信息已经变动')
        else:
            raise ATException('返回后，再次进入简介页面，简介信息未变动')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')