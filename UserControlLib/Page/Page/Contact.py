# -*- coding: utf-8 -*-

"""
    Effect:
"""

from UserControlLib.Page.DetailsPageBase import DetailsPageBase


class Contact(DetailsPageBase):

    def __init__(self, phone, title):
        super(Contact, self).__init__(phone, title)