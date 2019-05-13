# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case


class Mine_info_walkall(Case):
    """
    Description:
        遍历页面元素
    preHandle:
        1.登录App，进入我的-首页
    testHandle:
        1.点击个人头像，进入个人名片页面，能正常返回；
        2.点击【我的病例】，进入我的病例页面，能正常返回；
        3.点击【我的问答】，进入我的问答页面，能正常返回；
        4.点击【我的关注】， 进入我的关注页面，能正常返回；
        5.点击【我的视频】， 进入我的视频页面，能正常返回；
        6.点击【我的圈子】， 进入我的圈子页面，能正常返回；
        7.点击【黑名单】， 进入我的黑名单页面，能正常返回；
        8.点击【草稿箱】， 进入我的草稿箱单页面，能正常返回；
        9.点击【我的钱包】，进入我的钱包页面，能正常返回；
    """

    def preHandle(self):
        self.logStep('1.登录App，进入我的-首页')
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.phone.doAction(alias='mine', action='click')

    def testHandle(self):

        self.logStep('1.点击个人头像，进入个人名片页面，能正常返回')
        self.phone.doAction(alias='user_icon', action='click')
        self.phone.doAction(alias='back', action='click')

        self.logStep('2.点击【我的病例】，进入我的病例页面，能正常返回')
        self.phone.doAction(alias='my_cases', action='click')
        self.phone.doAction(alias='back', action='click')

        self.logStep('3.点击【我的问答】，进入我的问答页面，能正常返回')
        self.phone.doAction(alias='my_qa', action='click')
        self.phone.doAction(alias='back', action='click')

        self.logStep('4.点击【我的关注】， 进入我的关注页面，能正常返回')
        self.phone.doAction(alias='my_focus', action='click')
        self.phone.doAction(alias='back', action='click')

        self.logStep('5.点击【我的视频】， 进入我的视频页面，能正常返回')
        self.phone.doAction(alias='my_video', action='click')
        self.phone.doAction(alias='back', action='click')

        self.logStep('6.点击【我的圈子】， 进入我的圈子页面，能正常返回')
        self.phone.doAction(alias='my_group', action='click')
        self.phone.doAction(alias='back', action='click')

        self.logStep('7.点击【黑名单】， 进入我的黑名单页面，能正常返回')
        self.phone.doAction(alias='my_blacklist', action='click')
        self.phone.doAction(alias='back', action='click')

        self.logStep('8.点击【草稿箱】， 进入我的草稿箱单页面，能正常返回')
        self.phone.doAction(alias='my_drafts', action='click')
        self.phone.doAction(alias='back', action='click')

        self.logStep('9.点击【我的钱包】，进入我的钱包页面，能正常返回')
        self.phone.doAction(alias='my_money', action='click')
        self.phone.doAction(alias='back', action='click')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')