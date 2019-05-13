# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case


class Home_caselib_contribution_casepub_01(Case):
    """
    Description:
        贡献排行榜显示
    preHandle:
        1.进入首页，切换到病例Tab，进入首页-病例页面；
        2.点击用户头像下【贡献排行榜】，进入排行榜页面；
        3.点击【发病例，提升排名】，进入发布病例页面；
    testHandle:
        1.输入病例标题；
        2.点击【主诉病史】编辑框，进入病例详细编辑页面，在编辑框输入任意病例详情，点击返回，
            确认放弃编辑，返回病例撰写页面，【主诉病史】未编辑；
        3.点击【主诉病史】编辑框，进入病例详细编辑页面，在编辑框输入任意病例详情，点击返回，
            取消放弃编辑，页面不跳转，编辑内容不变，点击完成，跳转到病例撰写页面，【主诉病史】与编辑内容一致；
        4.添加科室
        5.发布病例，发布成功，并在首页-动态中有发布的病例(标题检查)
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入首页，切换到病例Tab，进入首页-病例页面')
        self.phone.doAction(alias='case', action='click')

        self.logStep('2.点击用户头像下【贡献排行榜】，进入排行榜页面')
        self.phone.doAction(alias='top_contribution', action='click')

        self.logStep('3.点击【发病例，提升排名】，进入发布病例页面')
        self.phone.doAction(alias='pub_case', action='click')

    def testHandle(self):

        self.logStep('1.输入病例标题')
        title = self.phone.getCurrentPage().editCaseTitle()
        self.logStep('2.点击【主诉病史】编辑框，进入病例详细编辑页面，在编辑框输入任意病例详情，点击返回，\n\
            确认放弃编辑，返回病例撰写页面，【主诉病史】未编辑')
        self.phone.getCurrentPage().editCaseElementDetails(location='symptom', confirm=False)
        self.logStep('3.点击【主诉病史】编辑框，进入病例详细编辑页面，在编辑框输入任意病例详情，点击返回，\n\
            取消放弃编辑，页面不跳转，编辑内容不变，点击完成，跳转到病例撰写页面，【主诉病史】与编辑内容一致')
        self.phone.getCurrentPage().editCaseElementDetails(location='symptom', confirm=False, drop=False)
        self.logStep('4.添加科室')
        self.phone.getCurrentPage().addDepartment(depart='神经外科')
        self.logStep('5.发布病例，发布成功，并在首页-动态中有发布的病例(标题检查)')
        self.phone.getCurrentPage().casePublish(title=title)

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')