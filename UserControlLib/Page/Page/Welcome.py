# -*- coding: utf-8 -*-

from UserControlLib.Page.PageBase import PageBase


class Welcome(PageBase):

    def __init__(self, phone, title):
        super(Welcome, self).__init__(phone, title)
