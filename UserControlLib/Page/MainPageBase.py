# -*- coding: utf-8 -*-

"""
    Effect:
"""

from UserControlLib.Page.PageBase import PageBase


class MainPageBase(PageBase):
    def __init__(self, phone, title):
        super(MainPageBase, self).__init__(phone, title)

    def toHome(self):
        element = self.getElement(alias='home')
        self.doAction(element=element, action='click')

    def toVisits(self):
        element = self.getElement(alias='visits')
        self.doAction(element=element, action='click')

    def toCircle(self):
        element = self.getElement(alias='circle')
        self.doAction(element=element, action='click')

    def toMessage(self):
        element = self.getElement(alias='message')
        self.doAction(element=element, action='click')

    def toMine(self):
        element = self.getElement(alias='mine')
        self.doAction(element=element, action='click')
