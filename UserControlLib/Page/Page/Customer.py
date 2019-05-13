# -*- coding: utf-8 -*-

"""
    Effect:
"""

from UserControlLib.Page.DetailsPageBase import DetailsPageBase


class Customer(DetailsPageBase):

    def __init__(self, phone, title):
        super(Customer, self).__init__(phone, title)