# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Mine_info_edit_department(Case):
    """
    Description:
        编辑科室信息
    preHandle:
        1.进入我的-首页，进入资料编辑页面；
        2.点击科室，进入科室选择页面；
    testHandle:
        1.点击返回，能正常返回到资料编辑页面；
        2.再次进入科室选择页面，任意选择一门科室，点击返回，科室信息为已选择的科室。
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入我的-首页，进入资料编辑页面')
        self.phone.doAction(alias='mine', action='click')
        self.phone.doAction(alias='info_edit', action='click')

        self.logStep('2.点击科室，进入科室选择页面')
        self.depart = self.phone.getSpecElementText(alias='depart_text')
        self.phone.doAction(alias='depart', action='click')

    def testHandle(self):

        self.logStep('1.点击返回，能正常返回到资料编辑页面')
        self.phone.doAction(alias='back', action='click')

        self.logStep('2.再次进入科室选择页面，任意选择一门科室，点击返回，科室信息为已选择的科室。')
        self.phone.doAction(alias='depart', action='click')
        if self.depart != '胃肠外科':
            subDepart = '胃肠外科'
        else:
            subDepart = '骨科'
        self.phone.getCurrentPage().choseDepart(depart='外科', subDepart=subDepart)
        if self.phone.getSpecElementText(alias='depart_text') == subDepart:
            self.logger.passInfo('科室信息为已选择的科室')
        else:
            raise ATException('科室信息为未更改')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')