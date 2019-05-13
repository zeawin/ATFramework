# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Visits_order_mgr(Case):
    """
    Description:
        订单管理
    preHandle:
        1.进入出诊页面，选择我的订单管理，进入我的订单页面；
    testHandle:
        1.能正常切换tab【进行中】、【待评分】、【已完成】、【全部订单】
        2.点击返回，能返回到出诊页面。
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入出诊页面，选择我的订单管理，进入我的订单页面')
        self.phone.doAction(alias='visits', action='click')
        self.phone.doAction(alias='my_order', action='click')

    def testHandle(self):

        self.logStep('1.能正常切换tab【进行中】、【待评分】、【已完成】、【全部订单】')
        dealingEle = self.phone.getElement(alias='dealing')
        scoringEle = self.phone.getElement(alias='scoring')
        completedEle = self.phone.getElement(alias='completed')
        allOrdersEle = self.phone.getElement(alias='all_orders')
        self.phone.doAction(element=dealingEle, action='click')
        if dealingEle.is_selected() and scoringEle.is_selected():
            raise ATException('不能正常切换tab【进行中】、【待评分】、【已完成】、【全部订单】')

        self.phone.doAction(element=scoringEle, action='click')
        if dealingEle.is_selected() and scoringEle.is_selected():
            raise ATException('不能正常切换tab【进行中】、【待评分】、【已完成】、【全部订单】')

        self.phone.doAction(element=completedEle, action='click')
        if completedEle.is_selected() and scoringEle.is_selected():
            raise ATException('不能正常切换tab【进行中】、【待评分】、【已完成】、【全部订单】')

        self.phone.doAction(element=allOrdersEle, action='click')
        if allOrdersEle.is_selected() and scoringEle.is_selected():
            raise ATException('不能正常切换tab【进行中】、【待评分】、【已完成】、【全部订单】')

        self.logger.passInfo('能正常切换tab【进行中】、【待评分】、【已完成】、【全部订单】')

        self.logStep('2.点击返回，能返回到出诊页面')
        self.phone.doAction(alias='back', action='click')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')