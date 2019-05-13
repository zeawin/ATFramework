# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Home_caselib_case_publish_02(Case):
    """
    Description:
        病例发布
    preHandle:
        1.进入首页，点击右上角发布按钮，选择发布病例，进入病例撰写页面；
    testHandle:
        1.输入病例标题；
        2.点击【主诉病史】编辑框，进入病例详细编辑页面；在编辑框输入任意病例详情，点击完成，跳转到病例撰写页面，【主诉病史】与编辑内容一致；
        3.点击【查体辅查】编辑框，进入病例详细编辑页面；在编辑框输入任意描述信息，点击完成，跳转到病例撰写页面，【查体辅查】与编辑内容一致；
        4.点击【诊断治疗】编辑框，进入病例详细编辑页面；在编辑框输入任意描述信息，点击完成，跳转到病例撰写页面，【诊断治疗】与编辑内容一致；
        5.点击【随访讨论】编辑框，进入病例详细编辑页面；在编辑框输入任意描述信息，点击完成，跳转到病例撰写页面，【随访讨论】与编辑内容一致；
        6.添加科室后发布病例，发布成功，并在首页-动态中有发布的病例(标题检查)；
        7.点击进入病例详情页面，删除此病例，返回首页动态页面，删除成功。
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
        self.logStep('2.点击【主诉病史】编辑框，进入病例详细编辑页面；在编辑框输入任意病例详情，点击完成，跳转到病例撰写页面，【主诉病史】与编辑内容一致')
        self.phone.getCurrentPage().editCaseElementDetails(location='symptom')
        self.logStep('3.点击【查体辅查】编辑框，进入病例详细编辑页面；在编辑框输入任意描述信息，点击完成，跳转到病例撰写页面，【查体辅查】与编辑内容一致')
        self.phone.getCurrentPage().editCaseElementDetails(location='checked')
        self.logStep('4.点击【诊断治疗】编辑框，进入病例详细编辑页面；在编辑框输入任意描述信息，点击完成，跳转到病例撰写页面，【诊断治疗】与编辑内容一致')
        self.phone.getCurrentPage().editCaseElementDetails(location='diagnose')
        self.logStep('5.点击【随访讨论】编辑框，进入病例详细编辑页面；在编辑框输入任意描述信息，点击完成，跳转到病例撰写页面，【随访讨论】与编辑内容一致')
        self.phone.getCurrentPage().editCaseElementDetails(location='discuss')
        self.logStep('6.添加科室后发布病例，发布成功，并在首页-动态中有发布的病例(标题检查)')
        self.phone.getCurrentPage().addDepartment(depart='神经外科')
        self.phone.getCurrentPage().casePublish(title=title)
        self.logStep('7.点击进入病例详情页面，删除此病例，返回首页动态页面，删除成功')
        self.phone.getCurrentPage().scanCaseDetails(title=title)
        self.phone.getCurrentPage().deleteCase(confirm=True)
        try:
            self.phone.getElement(alias=title, way='name', force=True)
        except Exception:
            self.logger.passInfo('删除病例成功，我的病例页面没有展示')
        else:
            raise ATException('删除病例失败')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')