# -*- coding: utf-8 -*-

"""
    Effect:
"""

import time
import re

from Framework.Exception import ATException
from UserControlLib.Page.MainPageBase import MainPageBase


class Circle(MainPageBase):
    def __init__(self, phone, title):
        super(Circle, self).__init__(phone, title)

    def enterDorCircle(self):
        if self.getTitle() != 'Circle_index':
            raise ATException('Current page [%s] has no method enterDorCircle()')

        dorCircleEle = self.phone.driver.find_element_by_name(name='医生圈')
        self.doAction(element=dorCircleEle, action='click')
        self.phone.setCurrentPage(self.phone.pageManager.getSpecPage(phone=self.phone, title='Common_circle_doctor'))
        flag = False
        timeindex = int(time.time())
        while flag is False and int(time.time()) - timeindex <= 10:
            try:
                self.phone.getElement(alias='primary', force=True)
            except Exception as e:
                time.sleep(0.5)
                if re.match('There is no AndroidElement named', e.message):
                    break
                continue
            else:
                flag = True
                break
        if flag:
            pass
        else:
            raise ATException('Arrive to the specified page %s failed, or timeout.' % self.getTitle())
