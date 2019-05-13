# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Home_caselib_case_publish_01(Case):
    """
    Description:
        病例发布
    preHandle:
        1.进入首页，点击右上角发布按钮，选择发布病例，进入病例撰写页面；
    testHandle:
        1.输入病例标题；
        2.点击【主诉病史】编辑框，进入病例详细编辑页面，在编辑框输入任意病例详情，点击返回，
            确认放弃编辑，返回病例撰写页面，【主诉病史】未编辑；
        3.点击【主诉病史】编辑框，进入病例详细编辑页面，在编辑框输入任意病例详情，点击返回，
            取消放弃编辑，页面不跳转，编辑内容不变，点击完成，跳转到病例撰写页面，【主诉病史】与编辑内容一致；
        4.添加科室
        5.发布病例，发布成功，并在首页-动态中有发布的病例(标题检查)；
        6.进入【我的】-【我的病例】页面，有成功发布的病例；
        7.点击进入病例详情页面，删除此病例，返回【我的病例】页面，删除成功
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入首页，点击右上角发布按钮，选择发布病例，进入病例撰写页面')
        self.phone.doAction(alias='publish', action='click')
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
        self.logStep('6.进入【我的】-【我的病例】页面，有成功发布的病例；')
        self.phone.doAction(alias="mine", action='click')
        self.phone.doAction(alias='my_cases', action='click')
        self.phone.getCurrentPage().scanCaseDetails(title=title)
        self.logStep('7.点击进入病例详情页面，删除此病例，返回【我的病例】页面，删除成功')
        self.phone.getCurrentPage().deleteCase(confirm=True)
        try:
            self.phone.getElement(alias=title, way='name', force=True)
        except Exception:
            self.logger.passInfo('删除病例成功，我的病例页面没有展示')
        else:
            raise ATException('删除病例失败')


    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')