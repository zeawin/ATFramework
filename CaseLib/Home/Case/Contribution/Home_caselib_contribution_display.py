# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Home_caselib_contribution_display(Case):
    """
    Description:
        贡献排行榜显示
    preHandle:
        1.进入首页，切换到病例Tab，进入首页-病例页面；
        2.点击用户头像下【贡献排行榜】，进入排行榜页面；
    testHandle:
        1.显示有【今日最佳贡献者】和【总排行榜】；
        2.点击返回，能正常返回到首页-病例页面；
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入首页，切换到病例Tab，进入首页-病例页面')
        self.phone.doAction(alias='case', action='click')

        self.logStep('2.点击用户头像下【贡献排行榜】，进入排行榜页面；')
        self.phone.doAction(alias='top_contribution', action='click')

    def testHandle(self):

        self.logStep('1.显示有【今日最佳贡献者】和【总排行榜】')
        try:
            self.phone.getElement(alias='今日最佳贡献者', force=True, way='name')
            self.phone.getElement(alias='总排行榜', force=True, way='name')
        except Exception as e:
            raise ATException('显示没有【最佳贡献者】和【总排行榜】')
        else:
            self.logger.passInfo('显示有【最佳贡献者】和【总排行榜】')

        self.logStep('2.点击返回，能正常返回到首页之前页面')
        self.phone.doAction(alias='back', action='click')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')