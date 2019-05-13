# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Mine_info_edit_speciality(Case):
    """
    Description:
        编辑擅长术式
    preHandle:
        1.进入我的-首页，进入资料编辑页面；
        2.点击擅长术式，进入添加擅长页面；
    testHandle:
        1.点击返回，能正常返回到资料编辑页面；
        2.再次进入添加擅长页面，任意选择两项擅长，点击保持，再次点击擅长术式，显示上次保存的两项擅长。
    """

    def preHandle(self):
        self.logStep('1.进入我的-首页，进入资料编辑页面')
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.phone.doAction(alias='mine', action='click')
        self.phone.doAction(alias='info_edit', action='click')

        self.logStep('2.点击擅长术式，进入添加擅长页面')
        self.phone.doAction(alias='speciality', action='click')

    def testHandle(self):

        self.logStep('1.点击返回，能正常返回到资料编辑页面。')
        self.phone.doAction(alias='back', action='click')

        self.logStep('2.再次进入添加擅长页面，任意选择两项擅长，点击保持，再次点击擅长术式，显示上次保存的两项擅长')
        self.phone.doAction(alias='speciality', action='click')
        self.phone.getCurrentPage().addSpeciality(depart='外科', subDepart='神经外科', operate='颅骨和脑手术')
        self.phone.getCurrentPage().cleanSpeciality(depart='外科', subDepart='神经外科', operate='颅骨和脑手术')


    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')