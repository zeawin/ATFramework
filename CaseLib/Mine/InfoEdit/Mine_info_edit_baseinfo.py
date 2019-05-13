# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case


class Mine_info_edit_baseinfo(Case):
    """
    Description:
        编辑个人基本信息
    preHandle:
        1.进入我的-首页，进入资料编辑页面；
    testHandle:
        1.编辑个人性别，点击返回，再次进入编辑信息页面，显示信息为上次编辑信息。
    """

    def preHandle(self):
        self.logStep('1.进入我的-首页，进入资料编辑页面')
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.phone.doAction(alias='mine', action='click')
        self.phone.doAction(alias='info_edit', action='click')

    def testHandle(self):

        self.logStep('1.编辑个人性别，点击返回，再次进入编辑信息页面，显示信息未上次编辑信息。')
        self.phone.doAction(alias='sex', action='click')
        self.phone.doAction(alias='male', action='click')
        self.phone.doAction(alias='back', action='click')
        self.phone.doAction(alias='info_edit', action='click')
        if self.phone.getSpecElementText(alias='sex_text') != u'男':
            self.logError('用户性别编辑失败')
        else:
            self.logger.passInfo('用户性别编辑成功')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')