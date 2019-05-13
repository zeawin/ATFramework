# -*- coding: utf-8 -*-

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Message_contacts_groupchart(Case):
    """
    Description:
        群聊
    preHandle:
        1.消息首页，点击通讯录进入通讯录页面；
    testHandle:
        1.点击发起群聊，任意选中2个或多个好友，创建群聊；
        2.点击设置按钮，进入群管理页面，修改群名后，所有群名显示正确；
        3.成功编辑并发送任意消息；
        4.解散此群，消息首页不在有此群显示。
    """

    def preHandle(self):
        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.消息首页，点击通讯录进入通讯录页面')
        self.phone.doAction(alias='message', action='click')
        self.phone.doAction(alias='contact', action='click')

    def testHandle(self):

        self.logStep('1.点击发起群聊，任意选中2个或多个好友，创建群聊')
        self.phone.getCurrentPage().createGroup()

        self.logStep('2.点击设置按钮，进入群管理页面，修改群名后，所有群名显示正确')
        title = self.phone.getCurrentPage().changeGroupName()

        self.logStep('3.成功编辑并发送任意消息')
        self.phone.getCurrentPage().chat()

        self.logStep('4.解散此群，消息首页不在有此群显示')
        self.phone.getCurrentPage().disbandGroup()
        try:
            self.phone.getElement(alias=title, way='name', force=True)
        except Exception:
            self.logger.passInfo('群解散成功')
        else:
            raise ATException('解散群失败')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')