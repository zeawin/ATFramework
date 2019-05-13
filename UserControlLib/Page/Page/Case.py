# -*- coding: utf-8 -*-

"""
    Effect:
"""
from Framework.Exception import ATException
from UserControlLib.Page.DetailsPageBase import DetailsPageBase


class Case(DetailsPageBase):

    def __init__(self, phone, title):
        super(Case, self).__init__(phone, title)

    def deleteCase(self, confirm=True):
        ele = self.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id', force=True)
        self.doAction(element=ele, action='click')
        ele = self._hasSpecContent(key='删除')
        self.doAction(element=ele, action='click')
        ele = self._hasSpecContent(key='确定要删除病例？')
        if not ele:
            raise ATException('点击删除用例时，未弹出确认窗口')
        if confirm is True:
            ele = self.getElement(alias='删除', way='name', force=True)
            self.doAction(element=ele, action='click')
            self.phone.setCurrentPage(self.phone.getLastPage())
            self._isArrivedPage()
        else:
            ele = self.getElement(alias='取消', way='name', force=True)
            self._hasSpecContent(key='病例详情')
            if not ele:
               raise ATException('Canceled to delete a case but the page has changed.')


