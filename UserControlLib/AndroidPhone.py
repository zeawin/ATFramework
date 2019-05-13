# -*- coding: utf-8 -*-

import time
import os

import datetime

import re
from appium import webdriver
from appium.webdriver.webelement import WebElement

from Framework.Utils.Validate import validate
from Framework.Exception import ATException
from Framework import Log
from UserControlLib.Manager import Manager
from UserControlLib.Page.MainPageBase import MainPageBase
from UserControlLib.Page.PageBase import PageBase


class AndroidPhone(object):
    NAME_LIST = {}

    @validate(command_executor=str, params=dict)
    def __init__(self, command_executor='http://127.0.0.1:4444/wd/hub', params=dict()):
        """create a AndroidPhone
        Args:
            params(dict):
                like: params = {
                    'platformName': {'types': str, 'optional': False},
                    'platformVersion': {'types': str, 'optional': False},
                    'deviceName': {'types': str, 'optional': False},
                    'appPackage': {'types': str, 'optional': False},
                    'app': {'types': str, 'optional': True}
                }
        """
        self.logger = Log.getLogger(self.__module__)
        self.desired = {}
        self.id = params.pop('id')
        self.platform = 'Android'
        while params['name'] in AndroidPhone.NAME_LIST:
            params['name'] += str(time.time())
            AndroidPhone.NAME_LIST.update({self.id: params['name']})
        self.name = params['name']

        self.desired['platformName'] = self.platform
        self.desired['platformVersion'] = params.get('version')
        self.desired['deviceName'] = params.get('name')
        self.desired['appPackage'] = params.get('app_package')
        self.desired['app'] = os.path.abspath(params.get('app_location'))
        self.desired['unicodeKeyboard'] = True
        self.desired['resetKeyboard'] = True
        self.desired['newCommandTimeout'] = 240

        self.account = params.get('account', {})
        self.logger.debug('To connect an android device: \n Platform[%s]\n Version[%s]\n Name[%s]'
                          % (self.desired['platformName'], self.desired['platformVersion'], self.desired['deviceName']))
        self.command_executor = command_executor
        self.driver = None
        self.__lastPage = None
        self.__currentPage = None
        self.pageManager = Manager(self)
        self.__initDriver(command_executor=self.command_executor, params=self.desired)
        self.width = 480
        self.height = 800
        if self.driver:
            size = self.driver.get_window_size()
            self.width = size['width']
            self.height = size['height']
        self.logger.debug('The Android[%s] window size: width[%s] height[%s].' %
                          (self.getPhoneId(), str(self.width), str(self.height)))

    def __waitInitComplete(self):
        self.__lastPage = None
        self.__currentPage = self.pageManager.getSpecPage(self, 'Welcome')
        sign = False
        timeIndex = int(time.time())
        while int(time.time()) - timeIndex <= 30:
            try:
                ele = self.getElement(alias='start', force=True)
            except Exception:
                time.sleep(1)
                continue
            else:
                if not ele:
                    time.sleep(1)
                    continue
                sign = True
                break
        if sign:
            self.logger.debug('The initialization of Android device [%s] is complete.' % self.id)
        else:
            self.logger.error('The initialization of Android device [%s] is timeout in 30 seconds.' % self.id)

    def __initDriver(self, command_executor, params):
        self.driver = webdriver.Remote(command_executor, params, keep_alive=True)
        self.__waitInitComplete()

    def getElement(self, alias=None, force=False, way='xpath', text=None):
        """To get a WebElement instance of specified alias
        Args:
            way     (str) : 获取元素方式，默认为'xpath', 'xpath', 'id', 'name'可选
            alias   (str) : 元素别名
            force   (str) : 是否强制获取
            text    (str) : way是xpath时，覆盖xpath的text过滤属性,text为ignore时，去掉text的过滤属性
        """
        try:
            ele = self.__currentPage.getElement(alias=alias, force=force, way=way, text=text)
        except Exception as e:
            raise ATException(e.message)
        else:
            return ele

    def getSpecElementText(self, element=None, alias=None):
        """To get the text value of a WebElement instance
        Args:
            element (WebElement) : 元素别名
            alias   (str)        : 是否强制获取
        """
        txt = ''
        if element and isinstance(element, WebElement):
            try:
                txt = element.text.encode('utf-8')
            except Exception as e:
                pass
            else:
                txt = element.text
        elif alias and isinstance(alias, str):
            ele = self.getElement(alias=alias, force=True)
            try:
                txt = ele.text.encode('utf-8')
            except Exception as e:
                txt = ele.text

        else:
            raise ATException('Method getSpecElementText() must give a param element(WebElement) or alias(str).')
        self.logger.debug('The text value of the specified element is \'%s\'.' % txt)
        return txt

    def doAction(self, alias=None, element=None, action=None, value=None, text=None):
        """deal with the events of element

        Args:
            alias   (str)       : 元素在xml文件中的别名，与element互斥

            element (WebElement): 处理事件的元素对象，与alias互斥

            action  (str)       : 事件名称
                     name        |    description
                =================================
                click            |       单击元素
                double_click     |       单击元素
                swipe_up         |       向上滑动
                swipe_down       |       向下滑动
                swipe_right      |       向右滑动
                swipe_left       |       向左滑动
                scroll_vertical  |       上下滚动元素
                scroll_transverse|       左右滚动元素
                input            |       字符输入

            value   (str)       : 输入的字符

            text:   (str)       : 指定alias参数时，覆盖xpath的text过滤属性,text为ignore时，去掉text的过滤属性
        """
        if alias:
            ele = self.getElement(alias=alias, text=text)
            if not ele:
                raise ATException('The WebElement alias[%s] can not be located in current page[%s]'
                                  % (alias, self.getCurrentPage().getTitle()))
            self.logger.info("In current page [%s], the located element is [%s] and will do action [%s]."
                             % (self.__currentPage.getTitle(), alias, action))
            self.getCurrentPage().doAction(element=ele, action=action, value=value)
        elif element:
            if isinstance(element, WebElement):
                self.logger.info("In current page [%s], the located element is [%s] and will do action [%s]."
                                 %
                                 (self.getCurrentPage().getTitle(), self.getCurrentPage()._getAlias(element=element), action))
                self.__currentPage.doAction(element=element, action=action, value=value)
            else:
                raise ATException('Function: [doAction] param: [element] must '
                                  'be a instance of appium.webdriver.webelement.WebElement, \nbut is [%s]'
                                  % type(element))
        else:
            raise ATException('Function: [doAction] param: [element] or [alias] must '
                              'be specified only and at least one.')

    def setCurrentPage(self, page):
        """
        """
        if isinstance(page, PageBase):
            if page != self.__currentPage:
                self.__lastPage = self.__currentPage
                self.__currentPage = page
        else:
            raise ATException('Object [%s] property must be a instance of PageBase.' % page)
        self.logger.info("To set the current page: [%s] successfully." % self.__currentPage.getTitle())

    def getCurrentPage(self):
        self.logger.info("To get the current page: [%s] successfully." % self.__currentPage.getTitle())
        return self.__currentPage

    def getLastPage(self):
        self.logger.info("To get the current page: [%s] successfully." % self.__lastPage.getTitle())
        return self.__lastPage

    def setLastPage(self, page):
        if isinstance(page, PageBase):
            self.__lastPage = page
        else:
            raise ATException('Object [%s] property must be a instance of PageBase.' % page)
        self.logger.debug("To set the last page: [%s] successfully." % self.__lastPage.getTitle())


    def setPhoneId(self, id):
        self.id = id

    def getPhoneId(self):
        return self.id

    def getScreenShot(self, desPath=None):
        """
        """
        if self.driver:
            pngName = '%s.png' % datetime.datetime.now().strftime('%Y-%m-%d-%H_%M_%S')
            if desPath:
                pngFile = os.path.join(desPath, pngName)
            else:
                pngFile = os.path.join(Log.baseConfig['logDir'], pngName)
            self.driver.get_screenshot_as_file(pngFile)
            self.logger.info('Capture the screen of the current page [%s] successfully,\nFile: [%s]'
                             % (self.__currentPage.getTitle(), pngFile))
            return
        self.logger.info(
            'Capture the screen of the current page [%s] failed, because the driver unavailable.' % self.__currentPage.getTitle())

    def __wetherCurrentIsMainPage(self):
        try:
            if self.driver.find_element_by_name('首页') and self.driver.find_element_by_name('出诊') \
                    and self.driver.find_element_by_name('我的'):
                return True
            else:
                return False
        except Exception as e:
            return False

    def login(self, way=None, name=None, password=None):
        """To login APP

        Args:
                way     (str): 登录方式，'password' or 'code'
                name    (str): 登录账号
                password(str): 登录密码或验证码
        """
        if self.__currentPage.getTitle() == 'Welcome':
            self.doAction(alias='start', action='click')
            if not way:
                if self.account['way'] == 'password':
                    self.doAction(alias='account_frame', action='swipe_left')
                    time.sleep(2)
                    self.doAction(alias='username_edit_text', action='input', value=self.account['user'])
                    self.doAction(alias='pwd_edit_text', action='input', value=self.account['password'])
                    self.doAction(alias='start', action='click')
                elif self.account['way'] == 'code':
                    self.doAction(alias='user_edit_text', action='input', value=self.account['user'])
                    time.sleep(2)
                    self.doAction(alias='pwd_edit_text', action='input', value=self.account['password'])
            if self.getCurrentPage().getTitle() != 'Home_dynamic':
                raise ATException('Login app failed.')
        elif isinstance(self.__currentPage, MainPageBase):
            self.arriveSpecMainPage(main='home')
        else:
            self.rebootApp()
            self.login()

    def rebootApp(self):
        """reboot app
        """
        if self.driver:
            self.driver.quit()
            self.__initDriver(command_executor=self.command_executor, params=self.desired)
            self.__waitInitComplete()
        else:
            self.__initDriver(command_executor=self.command_executor, params=self.desired)
            self.__waitInitComplete()

    def __del__(self):

        try:
            self.logger.info("Exit the connected Android Phone ID: [%s]" % self.getPhoneId())
            self.driver.quit()
        except ATException:
            pass

    def arriveSpecMainPage(self, main='home'):
        """到达指定的主页面
        Args
            main    (str) : 主页面名称, home, visits, mine, message, circle
        """
        if self.__wetherCurrentIsMainPage():
            self.setCurrentPage(self.pageManager.getSpecPage(phone=self, title='Home_dynamic'))
            self.doAction(alias=main, action='click')
        elif self.getCurrentPage().getTitle() == 'Welcome':
            self.login()
        elif re.match('Login', self.getCurrentPage().getTitle()):
            if self.account['way'] == 'password':
                self.doAction(alias='account_frame', action='swipe_left')
                time.sleep(2)
                self.doAction(alias='username_edit_text', action='input', value=self.account['user'])
                self.doAction(alias='pwd_edit_text', action='input', value=self.account['password'])
                self.doAction(alias='start', action='click')
            elif self.account['way'] == 'code':
                self.doAction(alias='account_frame', action='swipe_right')
                self.doAction(alias='user_edit_text', action='input', value=self.account['user'])
                time.sleep(2)
                self.doAction(alias='pwd_edit_text', action='input', value=self.account['password'])
                self.doAction(alias='start', action='click')
        else:
            try:
                ele = self.getCurrentPage().getElement(
                    alias='net.medlinker.medlinker:id/positive_button', way='id', force=True)
            except Exception:
                pass
            else:
                self.doAction(element=ele, action='click')
                self.arriveSpecMainPage(main=main)

            try:
                ele = self.getCurrentPage().getElement(
                    alias='net.medlinker.medlinker:id/left_button_layout', way='id', force=True)
            except Exception:
                pass
            else:
                self.doAction(element=ele, action='click')
                self.arriveSpecMainPage(main=main)

    def scrollToExact(self, direction, text, element=None, alias=None):
        self.__currentPage._scrollToExact(direction=direction, text=text, element=element, alias=alias)

    def scrollScreen(self, direction, count=1):
        self.__currentPage.scrollScreen(direction=direction, count=count)
