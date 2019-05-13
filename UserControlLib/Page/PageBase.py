# -*- coding: utf-8 -*-

import re
import os

import time

from selenium.webdriver import ActionChains

from Framework.Exception import ATException
from Framework.Utils.Validate import validate
from UserControlLib.Utils.AndroidElement import AndroidElement
from appium.webdriver.webelement import WebElement
from Framework import Log

getAbsPath = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class PageBase(object):
    def __init__(self, phone, title):
        self.logger = Log.getLogger(self.__module__)
        self.title = title
        if self.title.find('_') >= 0:
            index = self.title.index('_')
            self.elementFile = getAbsPath('../Page/Element/%s/%s.xml' % (self.title[0:index], self.title))
        else:
            self.elementFile = getAbsPath('../Page/Element/%s.xml' % self.title)
        self.phone = phone
        self.element = {}
        self.driverElement = {}
        self.source = None
        self._initElements()
        self.actionChains = None

    def _initElements(self):
        self.source = AndroidElement.getElementData(self.elementFile)

        def initUsableElement(data):
            result = {}
            for item in data:
                if isinstance(data[item], dict):
                    if 'alias' in data[item]:
                        result.update({data[item]['alias']: AndroidElement(data[item])})
                        self.logger.info('The available Element in Page: [%s] alias by [%s]'
                                         % (self.title, data[item]['alias']))
                    result.update(initUsableElement(data[item]))

            return result

        self.element = initUsableElement(self.source)
        self.element['primary'] = []
        for item in self.element:
            if hasattr(self.element[item], 'primary'):
                self.element['primary'].append(self.element[item])
        if len(self.element['primary']) == 0:
            del self.element['primary']
        else:
            self.logger.info('The count of available primary Elements in Page[%s] is %s'
                             % (self.title, len(self.element['primary'])))

    def getElement(self, alias, force=False, way=None, text=None):
        """To get a WebElement instance of specified alias

        Args:
            text:
            alias:
            way:
            force:
        """
        if way == 'xpath':
            if alias and alias in self.driverElement and not force and not text:
                return self.driverElement[alias]
            else:
                androidEle = self._getElementData(alias)

                if isinstance(androidEle, list):
                    result = []
                    for item in androidEle:
                        self.logger.debug(
                            'Try to get a primary WebElement in current page '
                            'to confirm whether the current page is [%s].\n xpath: [%s]'
                            % (self.getTitle(), item.xpath))
                        result.append(self.phone.driver.find_element_by_xpath(item.xpath))
                    return result
                elif not hasattr(androidEle, 'xpath'):
                    raise ATException('AndroidElement instance: [%s] has no attribute named \'xpath\'' % alias)
                else:
                    if text is not None:
                        if text == 'ignore':
                            if 'text' in androidEle.xpath:
                                androidEle.xpath = re.sub("contains\(@text, \'.*?\'\) and ", '', androidEle.xpath)
                        else:
                            if 'text' in androidEle.xpath:
                                androidEle.xpath = re.sub("@text, \'.*?\'", '@text, \'%s\'' % text, androidEle.xpath)
                    self.logger.info('To get a WebElement, \n xpath: [%s]' % androidEle.xpath)
                    try:
                        ele = self.phone.driver.find_element_by_xpath(androidEle.xpath)
                        self.driverElement[alias] = ele
                    except Exception:
                        self.logger.warn('To get a WebElement instance of specified alias[%s] failed.' % alias)
                        return None
                    else:
                        return self.driverElement[alias]
        elif way == 'name':
            if alias and alias in self.driverElement and not force:
                return self.driverElement[alias]
            self.driverElement[alias] = self.phone.driver.find_element_by_name(name=alias)
            return self.driverElement[alias]

        elif way == 'id':
            if alias and alias in self.driverElement and not force:
                return self.driverElement[alias]
            self.driverElement[alias] = self.phone.driver.find_element_by_id(id_=alias)
            return self.driverElement[alias]

    def _getElementData(self, alias):

        if alias and alias in self.element:
            return self.element[alias]
        else:
            raise ATException(
                'There is no AndroidElement named [%s] in current page [%s], '
                'or the alias you provide have not be defined yet.' % (alias, self.getTitle()))

    def doAction(self, element=None, action=None, value=None, timeout=15):
        actionDict = {
            'double_click': self._doubleClick,
            'click': self._click,
            'swipe_up': self._swipeUp,
            'swipe_down': self._swipeDown,
            'swipe_left': self._swipeLeft,
            'swipe_right': self._swipeRight,
            'scroll_vertical': self._scrollToExact,
            'scroll_transverse': self._scrollToExact,
            'input': 'input'
        }
        if not action or action not in actionDict:
            raise ATException('%s Method [doAction] Param [action] must be specified.\n'
                              'The valid value are %s, [%s] is invalid.'
                              % (self.__class__, actionDict.keys(), action))
        if action == 'input':
            element.set_text(value)
        elif re.match('scroll_(.*)', action):
            matcher = re.match('scroll_(.*)', action)
            actionDict[action](element=element, direction=matcher.group(1), text=value)
        else:
            actionDict[action](element=element)

        self._waitActionDone(element=element, action=action, value=value, timeout=timeout)

    def _getAlias(self, element):
        if isinstance(element, AndroidElement):
            for item in self.element:
                if self.element[item] is element:
                    return item
        elif isinstance(element, WebElement):
            for item in self.driverElement:
                if self.driverElement[item] is element:
                    return item
        else:
            raise ATException(
                'Method: [_getAlias()] param [element] must be a instance of \'AndroidElement\' or \'WebElement\'.')

    def getTitle(self):
        return self.title

    def _swipeUp(self, element=None, startx=None, starty=None, tox=None, toy=None, length=None):
        if element:
            if isinstance(element, WebElement):
                androidEle = self.element[self._getAlias(element)]

            elif isinstance(element, AndroidElement):
                androidEle = element
            else:
                raise ATException(
                    'Method: [_swipeUp()] param [element] must be a instance of \'AndroidElement\' or \'WebElement\'.')
            size = androidEle.bounds
            matcher = re.search('\[(\d+),\s?(\d+)\]\[(\d+),\s?(\d+)\]$', size)
            xrate = float(int(AndroidElement.WIDTH) / int(self.phone.width))
            yrate = float(int(AndroidElement.HEIGHT) / int(self.phone.height))
            if matcher:
                sx = int(xrate * int(matcher.groups()[0])) + 1
                sy = int(yrate * int(matcher.groups()[1])) + 1
                tx = int(xrate * int(matcher.groups()[2])) - 1
                ty = int(yrate * int(matcher.groups()[3])) - 1
        if startx:
            sx = startx
        if starty:
            sy = starty
        if tox:
            tx = tox
        if toy:
            ty = toy

        if length:
            sy = ty - length

        if not sx or not sy or not tx or not ty:
            raise ATException('Method: [_swipeDown()] must specified one of the two groups params, \n'
                              ' [element] or [startx & starty & tox & toy]')

        self.phone.driver.swipe(
            start_x=(tx - sx) / 2 + sx,
            start_y=ty,
            end_x=(tx - sx) / 2 + sx,
            end_y=sy
        )

    def _swipeDown(self, element=None, startx=None, starty=None, tox=None, toy=None, length=None):
        if element:
            if isinstance(element, WebElement):
                androidEle = self.element[self._getAlias(element)]
            elif isinstance(element, AndroidElement):
                androidEle = element
            else:
                raise ATException(
                    'Method: [_swipeDown()] param [element] must be a instance of \'AndroidElement\' or \'WebElement\'.')
            size = androidEle.bounds
            matcher = re.search('\[(\d+),\s?(\d+)\]\[(\d+),\s?(\d+)\]$', size)
            xrate = float(int(AndroidElement.WIDTH) / int(self.phone.width))
            yrate = float(int(AndroidElement.HEIGHT) / int(self.phone.height))
            if matcher:
                sx = int(xrate * int(matcher.groups()[0])) + 1
                sy = int(yrate * int(matcher.groups()[1])) + 1
                tx = int(xrate * int(matcher.groups()[2])) - 1
                ty = int(yrate * int(matcher.groups()[3])) - 1
        if startx:
            sx = startx
        if starty:
            sy = starty
        if tox:
            tx = tox
        if toy:
            ty = toy
        if length:
            ty = sy + length

        if not sx or not sy or not tx or not ty:
            raise ATException('Method: [_swipeDown()] must specified one of the two groups params, \n'
                              ' [element] or [startx & starty & tox & toy]')

        self.phone.driver.swipe(
            start_x=(tx - sx) / 2 + sx,
            start_y=sy,
            end_x=(tx - sx) / 2 + sx,
            end_y=ty
        )

    def _swipeRight(self, element=None, startx=None, starty=None, tox=None, toy=None, length=None):
        if element:
            if isinstance(element, WebElement):
                androidEle = self.element[self._getAlias(element)]
            elif isinstance(element, AndroidElement):
                androidEle = element
            else:
                raise ATException(
                    'Method: [_swipeRight()] param [element] must be a instance of \'AndroidElement\' or \'WebElement\'.')
            size = androidEle.bounds
            matcher = re.search('\[(\d+),\s?(\d+)\]\[(\d+),\s?(\d+)\]$', size)
            xrate = float(int(AndroidElement.WIDTH) / int(self.phone.width))
            yrate = float(int(AndroidElement.HEIGHT) / int(self.phone.height))
            if matcher:
                sx = int(xrate * int(matcher.groups()[0])) + 1
                sy = int(yrate * int(matcher.groups()[1])) + 1
                tx = int(xrate * int(matcher.groups()[2])) - 1
                ty = int(yrate * int(matcher.groups()[3])) - 1

        if startx:
            sx = startx
        if starty:
            sy = starty
        if tox:
            tx = tox
        if toy:
            ty = toy
        if length:
            tx = sx + length

        if not sx or not sy or not tx or not ty:
            raise ATException('Method: [_swipeRight()] must specified one of the two groups params, \n'
                              ' [element] or [startx & starty & tox & toy]')

        self.phone.driver.swipe(
            start_x=sx,
            start_y=(ty - sy) / 2 + sy,
            end_x=tx,
            end_y=(ty - sy) / 2 + sy
        )

    def _swipeLeft(self, element=None, startx=None, starty=None, tox=None, toy=None, length=None):
        if element:
            if isinstance(element, WebElement):
                androidEle = self.element[self._getAlias(element)]
            elif isinstance(element, AndroidElement):
                androidEle = element
            else:
                raise ATException(
                    'Method: [_swipeLeft()] param [element] must be a instance of \'AndroidElement\' or \'WebElement\'.')
            size = androidEle.bounds
            matcher = re.search('\[(\d+),\s?(\d+)\]\[(\d+),\s?(\d+)\]$', size)
            xrate = float(int(AndroidElement.WIDTH) / int(self.phone.width))
            yrate = float(int(AndroidElement.HEIGHT) / int(self.phone.height))
            if matcher:
                sx = int(xrate * int(matcher.groups()[0])) + 1
                sy = int(yrate * int(matcher.groups()[1])) + 1
                tx = int(xrate * int(matcher.groups()[2])) - 1
                ty = int(yrate * int(matcher.groups()[3])) - 1

        if startx:
            sx = startx
        if starty:
            sy = starty
        if tox:
            tx = tox
        if toy:
            ty = toy
        if length:
            tx = sx - length

        if not sx or not sy or not tx or not ty:
            raise ATException('Method: [_swipeLeft()] must specified one of the two groups params, \n'
                              ' [element] or [startx & starty & tox & toy]')

        self.phone.driver.swipe(
            start_x=tx,
            start_y=(ty - sy) / 2 + sy,
            end_x=sx,
            end_y=(ty - sy) / 2 + sy
        )

    def _waitActionDone(self, element, action, value=None, timeout=15, priority=0):
        """Wait for action response
        """
        alias = self._getAlias(element=element)
        if not alias or re.match('.*?/', alias):
            return
        if action == 'input':
            timeindex = int(time.time())
            flag = False
            if not isinstance(element, WebElement):
                raise ATException('element must be a WebElement.')
            if value is None:
                raise ATException()
            if self.element[alias].getProperty(name='password') == 'true':
                return
            while int(time.time()) - timeindex <= timeout:
                temp = element.text
                if temp == value or temp.encode('utf-8') == value or re.match('请输入', temp.encode('utf-8')):
                    flag = True
                    break
                time.sleep(1)

            if flag is True:
                self.logger.debug('Input string successfully.')
            else:
                self.logger.warn('Input string unsuccessfully.')

        if alias in self.element and hasattr(self.element[alias], action):
            timeindex = int(time.time())
            target = self.element[alias].getProperty(name=action).split('|')
            flag = False
            for item in target:
                if item == "last":
                    self.phone.setCurrentPage(self.phone.getLastPage())
                elif item == 'current':
                    pass
                else:
                    self.phone.setCurrentPage(
                        self.phone.pageManager.getSpecPage(self.phone, item))
                value = 1
                while flag is False and value > 0:
                    value = timeindex + timeout - int(time.time())
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
                    break
            if flag is False:
                raise ATException('Arrive to the specified page %s failed, or timeout.' % str(target))
            else:
                pass

    def _doubleClick(self, element):
        if not self.actionChains:
            self.actionChains = ActionChains(self.phone.driver)
        self.actionChains.double_click(on_element=element)

    def scrollScreen(self, direction, count):
        try:
            ele = self.getElement(alias='net.medlinker.medlinker:id/pager', way='id')
        except Exception:
            self.logger.warn('The screen could not be scrolled on this page [%s].' % self.getTitle())
            return
        else:
            size = ele.size
            location = ele.location

            startx = int(size['width'] / 2 + location['x'])
            starty = int(size['height'] / 2 + location['y'])
            temp = {
                'up': int(location['y']),
                'down': int(location['y'] + size['height'])
            }
            count *= 2
            while count > 0:
                self.phone.driver.swipe(
                    start_x=startx,
                    start_y=starty,
                    end_x=startx,
                    end_y=temp[direction],
                    duration=500
                )
                # count -= 1

    def _scrollToExact(self, direction, text, element=None, alias=None):
        if element and isinstance(element, WebElement):
            ele = element
            ali = self._getAlias(element=ele)
        elif alias and isinstance(alias, str):
            ele = self.getElement(alias=alias, text='ignore')
            ali = alias
        else:
            raise ATException('Method _scrollToExact() must give the param element(WebElement) or alias(str).')
        txt = ele.text.encode('utf-8')
        direct = []
        flag = False
        if direction == 'vertical':
            if txt == text:
                flag = True
            else:
                try:
                    if int(text) > int(txt):
                        direct.append(self._swipeUp)
                    elif int(text) < int(txt):
                        direct.append(self._swipeDown)
                except Exception as e:
                    direct.append(self._swipeDown).append(self._swipeUp)
            len = ele.size['height']
        else:
            if txt == text:
                flag = True
            else:
                try:
                    if int(text) > int(txt):
                        direct.append(self._swipeLeft)
                    elif int(text) < int(txt):
                        direct.append(self._swipeRight)
                except Exception as e:
                    direct.append(self._swipeLeft).append(self._swipeRight)
            len = ele.size['width']
        len = int(len * 1.5)
        for func in direct:
            can = True
            while can:
                func(element=ele, length=len)
                if text == ele.text.encode('utf-8'):
                    flag = True
                    break
                if txt == ele.text.encode('utf-8'):
                    break
                txt = ele.text.encode('utf-8')
            if flag:
                break
        if flag is False:
            raise ATException('All the values are checked, but not find [%s], '
                              'or the located element cannot be scrolled.' % text)

    @validate(element=WebElement)
    def _click(self, element):
        if hasattr(element, 'click'):
            element.click()
        else:
            if not self.actionChains:
                self.actionChains = ActionChains(self.phone.driver)
            self.actionChains.context_click(on_element=element)

    def scanCaseDetails(self, title):
        ele = self._hasSpecContent(key=title, timeout=5)
        if ele:
            self.doAction(element=ele, action='click')
            self.phone.setCurrentPage(self.phone.pageManager.getSpecPage(phone=self.phone, title='Case_details'))
            self._hasSpecContent(key='病例详情')
            if not ele:
                raise ATException('From page[%s] click the specified case can not enter the case details display page.'
                                  % self.getTitle())
        else:
            raise ATException("There is no case named [%s] in current page [%s]" % (title, self.getTitle()))

    def _hasSpecContent(self, key, timeout=10):
        sign = False
        timeIndex = int(time.time())
        while int(time.time()) - timeIndex <= timeout:
            try:
                ele = self.getElement(alias=key, way='name', force=True)
            except Exception:
                time.sleep(0.5)
                continue
            else:
                return ele
        return sign

    def _isArrivedPage(self, timeout=10):
        flag = False
        timeindex = int(time.time())
        while flag is False and int(time.time()) - timeindex <= timeout:
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
