# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case


class Home_caselib_question_publish_01(Case):
    """
    Description:
        病例发布
    preHandle:
        1.进入首页，点击右上角发布按钮，选择提问题，进入提问页面；
    testHandle:
        1.编辑问题标题和详情，点击返回，确认放弃此次提问，返回到之前页面；
        2.重新进入问题发布页面，编辑问题标题和详情；
        3.进入添加标签页面，点击发布按钮无响应；
        4.添加标签后，发布提问，发布成功，页面跳转到到【动态首页】，有发布的问题展现；
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入首页，点击右上角发布按钮，选择提问题，进入提问页面；')
        self.phone.doAction(alias='publish', action='click')
        self.phone.doAction(alias='pub_question', action='click')

    def testHandle(self):

        self.logStep('1.编辑问题标题和详情，点击返回，确认放弃此次提问，返回到之前页面；')
        self.phone.getCurrentPage().editQuestionDetails(confirm=False, drop=True)
        self.logStep('2.重新进入问题发布页面，编辑问题标题和详情')
        self.phone.doAction(alias='publish', action='click')
        self.phone.doAction(alias='pub_question', action='click')
        title = self.phone.getCurrentPage().editQuestionDetails()
        self.logStep('3.进入添加科室页面，点击发布按钮无响应')
        self.phone.getCurrentPage().questionPublish()
        self.logStep('4.选择科室后，发布提问，发布成功，页面跳转到到【动态首页】，有发布的问题展现')
        self.phone.getCurrentPage().addLabel(label='杂合血红蛋白S')
        self.phone.getCurrentPage().questionPublish(title=title)

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')