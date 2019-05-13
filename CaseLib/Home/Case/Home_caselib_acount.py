# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case


class Home_caselib_acount(Case):
    """
    Description:
        查看用户资料
    preHandle:
        1.进入首页，切换到病例Tab，进入首页-病例页面；
        2.点击科室气泡下用户头像，进入他的资料页面；
    testHandle:
        1.点击返回，能正常返回到首页之前页面；
        2.再次进入他的资料页面，显示有【基本资料】、【代表案例】、【学术交流】等个人信息
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入首页，切换到病例Tab，进入首页-病例页面')
        self.phone.doAction(alias='case', action='click')

        self.logStep('2.点击科室气泡下用户头像，进入他的资料页面')
        self.phone.doAction(alias='customer_icon', action='click')

    def testHandle(self):

        self.logStep('1.再次进入他的资料页面，显示有【基本资料】、【代表案例】、【学术交流】等个人信息')
        try:
            self.phone.getElement(alias='基本资料', force=True, way='name')
            self.phone.getElement(alias='基本资料', force=True, way='name')
            self.phone.getElement(alias='基本资料', force=True, way='name')
        except Exception as e:
            self.logError('进入他的资料页面，【基本资料】、【代表案例】、【学术交流】显示不完全等个人信息')
        else:
            self.logger.passInfo('进入他的资料页面，显示有【基本资料】、【代表案例】、【学术交流】等个人信息')

        self.logStep('2.点击返回，能正常返回到首页之前页面')
        self.phone.doAction(alias='back', action='click')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')