# -*- coding: utf-8 -*-

"""
    Effect:
"""
import time

from Framework.Engine.Case import Case
from Framework.Exception import ATException


class Mine_info_edit_myschool(Case):
    """
    Description:
        编辑学历信息
    preHandle:
        1.进入我的-首页，进入资料编辑页面；
        2.点击毕业院校，进入我的学校页面；
    testHandle:
        1.点击返回，能正常返回到资料编辑页面；
        2.再次进入我的学校页面，任意编辑一项不完整学历点击返回，弹出提示信息不完整,点击确认，返回资料编辑页面，毕业院校信息未更改；
        3.再次进入我的学校页面，任意编辑一项学历，输入入学时间，输入毕业时间不晚于入学时间，输入不成功，完成此项学历编辑；
        4.任意编辑一项未编辑的学历，输入毕业时间，输入入学时间不早于毕业时间，输入不成功，完成此项学历编辑；
        5.点击返回，我的学校显示最高学历信息。
    """

    def preHandle(self):

        self.phone = self.resource.getAndroidPhone(id='0')
        self.phone.login()
        self.logStep('1.进入我的-首页，进入资料编辑页面')
        self.phone.doAction(alias='mine', action='click')
        self.phone.doAction(alias='info_edit', action='click')

        self.logStep('1.点击毕业院校，进入我的学校页面')
        self.phone.doAction(alias='college', action='click')

    def testHandle(self):

        self.logStep('1.点击返回，能正常返回到资料编辑页面')
        self.phone.doAction(alias='back', action='click')

        self.logStep('2.再次进入我的学校页面，任意编辑一项不完整学历点击返回，弹出提示信息不完整,点击确认，返回资料编辑页面，毕业院校信息未更改')
        dCollege = str(time.time())
        self.phone.doAction(alias='college', action='click')

        self.phone.doAction(alias='doctor', action='input', value=dCollege)
        self.phone.doAction(alias='doctor_major', action='input', value='')
        self.phone.doAction(alias='back', action='click')
        self.phone.doAction(alias='commit', action='click')
        if self.phone.getSpecElementText(alias="college_text") != dCollege:
            self.logger.passInfo('毕业院校信息未更改')
        else:
            raise ATException('任意编辑一项不完整学历点击返回，弹出提示信息不完整,点击确认，返回资料编辑页面，毕业院校信息已经更改')

        self.logStep('3.再次进入我的学校页面，任意编辑一项学历，输入入学时间，输入毕业时间不晚于入学时间，输入不成功，完成此项学历编辑')
        self.phone.doAction(alias='college', action='click')

        self.phone.doAction(alias='doctor', action='input', value=dCollege)
        self.phone.doAction(alias='doctor_major', action='input', value='爆破')
        self.phone.doAction(alias='doctor_start_date', action='click', text='ignore')
        self.phone.doAction(alias='year', action='scroll_vertical', value='1998', text='ignore')
        self.phone.doAction(alias='month', action='scroll_vertical', value='8', text='ignore')
        self.phone.doAction(alias='commit', action='click')
        self.phone.doAction(alias='doctor_end_date', action='click', text='ignore')
        self.phone.doAction(alias='year', action='scroll_vertical', value='1997', text='ignore')
        self.phone.doAction(alias='month', action='scroll_vertical', value='8', text='ignore')
        self.phone.doAction(alias='commit', action='click')
        import re
        if not re.search('1997', self.phone.getSpecElementText(alias="doctor_end_date")):
            self.logger.passInfo('输入毕业时间不晚于入学时间，输入不成功')
        else:
            raise ATException('输入毕业时间不晚于入学时间，输入成功')

        self.phone.doAction(alias='doctor_end_date', action='click', text='ignore')
        self.phone.doAction(alias='year', action='scroll_vertical', value='1999', text='ignore')
        self.phone.doAction(alias='month', action='scroll_vertical', value='8', text='ignore')
        self.phone.doAction(alias='commit', action='click')

        self.logStep('4.任意编辑一项未编辑的学历，输入毕业时间，输入入学时间不早于毕业时间，输入不成功，完成此项学历编辑')
        mCollege = str(time.time())
        self.phone.doAction(alias='master', action='input', value=mCollege)
        self.phone.doAction(alias='master_major', action='input', value='爆破')

        self.phone.doAction(alias='master_end_date', action='click', text='ignore')
        self.phone.doAction(alias='year', action='scroll_vertical', value='1997', text='ignore')
        self.phone.doAction(alias='month', action='scroll_vertical', value='1', text='ignore')
        self.phone.doAction(alias='commit', action='click', text='ignore')

        self.phone.doAction(alias='master_start_date', action='click', text='ignore')
        self.phone.doAction(alias='year', action='scroll_vertical', value='1998', text='ignore')
        self.phone.doAction(alias='month', action='scroll_vertical', value='2', text='ignore')
        self.phone.doAction(alias='commit', action='click')

        if not re.search('1998', self.phone.getSpecElementText(alias="master_start_date")):
            self.logger.passInfo('输入入学时间不早于毕业时间，输入不成功')
        else:
            raise ATException('输入入学时间不早于毕业时间，输入成功')

        self.phone.doAction(alias='master_start_date', action='click', text='ignore')
        self.phone.doAction(alias='year', action='scroll_vertical', value='1996', text='ignore')
        self.phone.doAction(alias='month', action='scroll_vertical', value='2', text='ignore')
        self.phone.doAction(alias='commit', action='click')

        self.logStep('1.点击返回，我的学校显示最高学历信息')
        self.phone.doAction(alias='back', action='click')
        if self.phone.getSpecElementText(alias="college_text") == dCollege:
            self.logger.passInfo('我的学校显示最高学历信息')
        else:
            raise ATException('我的学校未显示最高学历信息')

    def postHandle(self):
        self.phone.arriveSpecMainPage(main='home')