# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case


class Circle_dorcircle_pubpost(Case):
    """
    Description:
        发布圈子消息
    preHandle:
        1.进入圈子页面，点击医生圈进入医生圈页面
    testHandle:
        1.点击返回，能正常返回到首页之前页面；
        2.再次进入医生圈页面，点击发布按钮，进入消息发布页面；
        3.输入任意信息，点击取消，确认放弃此次发帖，返回医生圈页面；
        4.再次进入帖子编辑页面，编辑任意信息，点击发布，跳转到医生圈页面，有成功发布的帖子。
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入圈子页面，点击医生圈进入医生圈页面')
        self.phone.doAction(alias='circle', action='click')
        self.phone.getCurrentPage().enterDorCircle()

    def testHandle(self):

        self.logStep('1.点击返回，能正常返回到首页之前页面')
        self.phone.doAction(alias='back', action='click')

        self.logStep('2.再次进入医生圈页面，点击发布按钮，进入消息发布页面')
        self.phone.getCurrentPage().enterDorCircle()
        self.phone.doAction(alias='pub_post', action='click')

        self.logStep('3.输入任意信息，点击取消，确认放弃此次发帖，返回医生圈页面')
        details = self.phone.getCurrentPage().editPostDetails(confirm=False, drop=True)

        self.logStep('4.再次进入帖子编辑页面，编辑任意信息，点击取消，取消放弃此次发帖，点击发布，跳转到医生圈页面，有成功发布的帖子')
        self.phone.doAction(alias='pub_post', action='click')
        self.phone.getCurrentPage().editPostDetails(details=details, confirm=False, drop=False)
        self.phone.getCurrentPage().postPublish(title=details)

    def postHandle(self):
        self.phone.doAction(alias='back', action='click')
        self.phone.arriveSpecMainPage(main='home')