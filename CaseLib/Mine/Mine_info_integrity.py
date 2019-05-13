# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case


class Mine_info_integrity(Case):
    """
    Description:
        完善资料完整度
    preHandle:
        1.登录App，进入我的-首页
    testHandle:
        1.点击资料完整度，进入完善资料页面；
        2.点击返回，返回到我的-首页；
        3.进入完善资料页面，对性别，编辑成功；
        4.点击下一步，进入添加擅长页面；
        5.点击下一步，进入添加代表作页面，点击完成，返回到我的主页。
    """

    def preHandle(self):
        self.logStep('1.登录App，进入我的-首页')
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.phone.doAction(alias='mine', action='click')

    def testHandle(self):

        self.logStep('1.点击资料完整度，进入完善资料页面')
        self.phone.doAction(alias='info_integrity', action='click')

        self.logStep('2.点击返回，返回到我的-首页')
        self.phone.doAction(alias='back', action='click')

        self.logStep('3.进入完善资料页面，对性别，所属医院，职务进行编辑，编辑成功')
        self.phone.doAction(alias='info_integrity', action='click')
        self.phone.doAction(alias='sex', action='click')
        self.phone.doAction(alias='male', action='click')
        if self.phone.getSpecElementText(alias='sex_text') != u'男':
            self.logError('用户性别编辑失败')
        else:
            self.logger.passInfo('用户性别编辑成功')

        self.logStep('4.点击下一步，进入添加擅长页面')
        self.phone.doAction(alias='next_step', action='click')

        self.logStep('5.点击下一步，进入添加代表作页面，点击完成，返回到我的主页')
        self.phone.doAction(alias='next_step', action='click')
        self.phone.doAction(alias='commit', action='click')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')