# -*- coding: utf-8 -*-

"""
    Effect:
"""
import re
import time

from Framework.Exception import ATException
from UserControlLib.Page.PageBase import PageBase


class Common(PageBase):
    def __init__(self, phone, title):
        super(Common, self).__init__(phone, title)

    def getElement(self, alias, force=False, way=None, text=None):
        """To get a WebElement instance of specified alias

        Args:
            text:
            alias:
            way:
            force:
        """
        if self.getTitle() == 'Common_set_checked' or self.getTitle() == 'Common_date_chose':
            def find_element(alias, force=False, way=None, text=None):
                if way == 'xpath':
                    if alias and alias in self.driverElement and not force and not text:
                        return self.driverElement[alias]
                    else:
                        androidEle = self._getElementData(alias)
                        if not hasattr(androidEle, 'xpath'):
                            raise ATException('AndroidElement instance: [%s] has no attribute named \'xpath\'' % alias)
                        else:
                            if text is not None:
                                if text == 'ignore':
                                    if 'text' in androidEle.xpath:
                                        androidEle.xpath = re.sub("contains\(@text, \'.*?\'\) and ", '',
                                                                  androidEle.xpath)
                                else:
                                    if 'text' in androidEle.xpath:
                                        androidEle.xpath = re.sub("@text, \'.*?\'", '@text, \'%s\'' % text,
                                                                  androidEle.xpath)
                            self.logger.info('To get a WebElement, \n xpath: [%s]' % androidEle.xpath)
                            try:
                                self.driverElement[alias] = self.phone.driver.find_elements_by_xpath(androidEle.xpath)
                            except Exception as e:
                                self.logger.error(e.message)
                                return None
                return self.driverElement[alias]

            if alias == 'month':
                self.driverElement[alias] = find_element(alias=alias, force=force, way=way, text=text)
                if isinstance(self.driverElement[alias], list) and len(self.driverElement[alias]) > 1:
                    self.driverElement[alias] = self.driverElement[alias][1]
            elif alias == 'year':
                self.driverElement[alias] = find_element(alias=alias, force=force, way=way, text=text)
                if isinstance(self.driverElement[alias], list) and len(self.driverElement[alias]) > 1:
                    self.driverElement[alias] = self.driverElement[alias][0]
            else:
                return PageBase.getElement(self, alias=alias, force=force, way=way, text=text)
            return self.driverElement[alias]
        else:
            return PageBase.getElement(self, alias=alias, force=force, way=way, text=text)

    def addSpeciality(self, depart, subDepart, operate):
        if self.getTitle() != 'Common_speciality':
            raise ATException('Page object [%s] has no method addSpeciality().')
        if not operate:
            return

        def find_and_click(by_name, way='name'):
            if way == 'name':
                ele = self.phone.driver.find_element_by_name(by_name)
            elif way == 'id':
                ele = self.phone.driver.find_element_by_id(by_name)
            if isinstance(ele, list):
                self.logger.debug(
                    '%s WebElement have been find by [%s], but return the first one.' % (len(ele), by_name))
                ele = ele[0]
            self._click(element=ele)
            # time.sleep(0.5)

        find_and_click(depart)
        find_and_click(subDepart)
        if isinstance(operate, list):
            for item in operate:
                find_and_click(item)
        else:
            find_and_click(operate)

        find_and_click(by_name=r'net.medlinker.medlinker:id/left_button_layout', way='id')

        self.phone.doAction(alias='commit', action='click')
        self.phone.doAction(alias='speciality', action='click')
        try:
            if isinstance(operate, list):
                for item in operate:
                    self.phone.driver.find_element_by_name(item)
            else:
                self.phone.driver.find_element_by_name(operate)
        except Exception:
            raise ATException('addSpeciality() failed.')
        else:
            self.logger.passInfo('Add speciality successfully.')

    def cleanSpeciality(self, depart, subDepart, operate):
        clean = []
        if isinstance(operate, list):
            for item in operate:
                try:
                    self.phone.driver.find_element_by_name(item)
                except Exception:
                    pass
                else:
                    clean.append(item)
        else:
            try:
                self.phone.driver.find_element_by_name(operate)
            except Exception:
                pass
            else:
                clean.append(operate)
        if len(clean) > 0:
            self.logger.warn('The specialities %s have been add already, clean the first.' % clean)
        if not clean:
            return

        def find_and_click(by_name, way='name'):
            if way == 'name':
                ele = self.phone.driver.find_element_by_name(by_name)
            elif way == 'id':
                ele = self.phone.driver.find_element_by_id(by_name)
            if isinstance(ele, list):
                self.logger.debug(
                    '%s WebElement have been find by [%s], but return the first one.' % (len(ele), by_name))
                ele = ele[0]
            self._click(element=ele)

        find_and_click(depart)
        find_and_click(subDepart)
        if isinstance(clean, list):
            for item in clean:
                find_and_click(item)

        find_and_click(by_name=r'net.medlinker.medlinker:id/left_button_layout', way='id')

        self.phone.doAction(alias='commit', action='click')
        self.phone.doAction(alias='speciality', action='click')
        try:
            if isinstance(clean, list):
                for item in clean:
                    self.phone.driver.find_element_by_name(item)
            else:
                self.phone.driver.find_element_by_name(operate)
        except Exception:
            self.logger.info('addSpeciality() failed.')
        else:
            raise ATException('Add speciality successfully.')

    def doAction(self, element=None, action=None, value=None, timeout=15):
        lastpage = self.phone.getLastPage()
        curtitle = self.getTitle()
        PageBase.doAction(self, element=element, action=action, value=value, timeout=timeout)
        if curtitle == 'Common_case_or_question':
            self.phone.setLastPage(lastpage)

    def editCaseTitle(self, title=None):
        if self.getTitle() != 'Common_case_edit':
            raise ATException('Current page is [%s], there is no method named editCaseTitle()')
        if not title:
            title = str(time.time())
        self.phone.doAction(alias='case_title', action='input', value=title)
        return title

    def editCaseElementDetails(self, location, text=None, confirm=True, drop=True):
        if self.getTitle() != 'Common_case_edit':
            raise ATException('Current page is [%s], there is no method named editCaseElementDetails()')
        locations = ('symptom', 'checked', 'diagnose', 'discuss')
        if location in locations:
            self.phone.doAction(alias=location, action='click')
            editEle = self.phone.getElement(alias='net.medlinker.medlinker:id/case_content_edit', way='id')
            if text is None:
                text = str(time.time())
            self.phone.doAction(element=editEle, action='input', value=text)
        else:
            raise ATException('The location must be specified a valid value in %s, but get \'%s\''
                              % (str(locations), location))
        if confirm is True:
            commitEle = self.phone.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id')
            self.phone.doAction(element=commitEle, action='click')
        else:
            cancelEle = self.phone.getElement(alias='net.medlinker.medlinker:id/left_button_layout', way='id')
            self.phone.doAction(element=cancelEle, action='click')
            if drop is True:
                positive = self.phone.getElement(alias='net.medlinker.medlinker:id/positive_button', way='id')
                self.phone.doAction(element=positive, action='click')
            else:
                negative = self.phone.getElement(alias='net.medlinker.medlinker:id/negative_button', way='id')
                self.phone.doAction(element=negative, action='click')
                commitEle = self.phone.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id')
                self.phone.doAction(element=commitEle, action='click')

        if (self.phone.getSpecElementText(alias=location + '_text') == text) ^ confirm:
            self.logger.error('The %s text is not the expected result.')
        else:
            self.logger.passInfo('The %s text is the expected result.')

    def addDepartment(self, depart):
        if self.getTitle() != 'Common_case_edit':
            raise ATException('Current page is [%s], there is no method named addDepartment()')
        self.phone.doAction(alias='next', action='click')
        searchEle = self.phone.getElement(alias='net.medlinker.medlinker:id/line_search_layout', way='id')
        self.phone.doAction(element=searchEle, action='click')
        searchEditEle = self.phone.getElement(alias='net.medlinker.medlinker:id/search_edittext', way='id')
        self.phone.doAction(element=searchEditEle, action='input', value=depart)
        timeIndex = int(time.time())
        while int(time.time()) - timeIndex <= 15:
            eles = self.phone.driver.find_elements_by_name(name=depart)
            if len(eles) >= 2:
                self.phone.doAction(element=eles[1], action='click')
                time.sleep(1)
                break
            else:
                time.sleep(1)
                continue

    def casePublish(self, title):
        if self.getTitle() != 'Common_case_edit':
            raise ATException('Current page is [%s], there is no method named casePublish()')
        pubEle = self.phone.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id')
        self.phone.doAction(element=pubEle, action='click')
        # self.phone.scrollScreen(direction='up')
        self.phone.setCurrentPage(self.phone.pageManager.getSpecPage(self.phone, title='Home_dynamic'))

        timeIndex = int(time.time())
        while int(time.time()) - timeIndex <= 15:
            try:
                self.getElement(alias=title, way='name')
            except Exception:
                time.sleep(1)
                continue
            else:
                self.logger.passInfo('Publish case [%s] success.' % title)
                break

    def editQuestionDetails(self, title=None, details=None, confirm=True, drop=True):
        if self.getTitle() != 'Common_question_edit':
            raise ATException('Current page is [%s], there is no method named editCaseElementDetails()')

        # self.phone.doAction(alias="title", action='click')
        editEle = self.phone.getElement(alias='net.medlinker.medlinker:id/que_edit_title', way='id')
        if title is None:
            title = str(time.time())
        self.phone.doAction(element=editEle, action='input', value=title)

        if details:
            editContextEle = self.phone.getElement(alias='net.medlinker.medlinker:id/que_edit_content', way='id')
            self.phone.doAction(element=editContextEle, action='input', value=details)

        if confirm is True:
            commitEle = self.phone.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id')
            self.phone.doAction(element=commitEle, action='click')
        else:
            cancelEle = self.phone.getElement(alias='net.medlinker.medlinker:id/left_button_layout', way='id')
            self.phone.doAction(element=cancelEle, action='click')
            if drop is True:
                positive = self.phone.getElement(alias='net.medlinker.medlinker:id/positive_button', way='id')
                self.phone.doAction(element=positive, action='click')
                self.phone.setCurrentPage(self.phone.getLastPage())
            else:
                negative = self.phone.getElement(alias='net.medlinker.medlinker:id/negative_button', way='id')
                self.phone.doAction(element=negative, action='click')
                commitEle = self.phone.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id')
                self.phone.doAction(element=commitEle, action='click')

        return title

    def questionPublish(self, title=None):
        if self.getTitle() != 'Common_question_edit':
            raise ATException('Current page is [%s], there is no method named casePublish()')
        pubEle = self.phone.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id')
        self.phone.doAction(element=pubEle, action='click')
        # self.phone.scrollScreen(direction='up')
        time.sleep(1)
        try:
            self.phone.driver.find_element_by_name(name='添加标签')
        except Exception as e:
            self.phone.setCurrentPage(self.phone.pageManager.getSpecPage(self.phone, title='Home_dynamic'))
            if title is None:
                self.logger.passInfo('The current page is [%s]' % self.phone.getCurrentPage().getTitle())
            else:
                self.logger.fail(
                    'The current page is [%s], publish question failed' % self.phone.getCurrentPage().getTitle())
        else:
            if title is None:
                self.logger.passInfo(
                    'The current page is [%s], publish question failed.' % self.phone.getCurrentPage().getTitle())
                return

        timeIndex = int(time.time())
        sign = False
        while int(time.time()) - timeIndex <= 15:
            try:
                self.getElement(alias='%s？' % title, way='name')
            except Exception:
                time.sleep(1)
                continue
            else:
                sign = True
                break
        if sign:
            self.logger.passInfo('Publish case [%s] success.' % title)
        else:
            self.logger.fail('Publish case [%s] failed, cannot find the published question.' % title)

    def addLabel(self, label):
        if self.getTitle() != 'Common_question_edit':
            raise ATException('Current page is [%s], there is no method named addLabel()')
        # self.phone.doAction(alias='next', action='click')
        searchEle = self.phone.getElement(alias='net.medlinker.medlinker:id/line_search_layout', way='id')
        self.phone.doAction(element=searchEle, action='click')
        searchEditEle = self.phone.getElement(alias='net.medlinker.medlinker:id/search_edittext', way='id')
        self.phone.doAction(element=searchEditEle, action='input', value=label)
        timeIndex = int(time.time())
        while int(time.time()) - timeIndex <= 15:
            eles = self.phone.driver.find_elements_by_name(name=label)
            if len(eles) >= 2:
                self.phone.doAction(element=eles[1], action='click')
                time.sleep(1)
                break
            else:
                time.sleep(1)
                continue

    def editPostDetails(self, details=None, confirm=True, drop=True):
        if self.getTitle() != 'Common_circle_doctor':
            raise ATException('Current page is [%s], there is no method named editPostDetails()')

        # self.phone.doAction(alias="title", action='click')
        editEle = self.phone.getElement(alias='net.medlinker.medlinker:id/edit_content', way='id')
        if details is None:
            details = str(time.time())
        self.phone.doAction(element=editEle, action='input', value=details)

        if confirm is True:
            commitEle = self.phone.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id')
            self.phone.doAction(element=commitEle, action='click')
        else:
            cancelEle = self.phone.getElement(alias='net.medlinker.medlinker:id/left_button_layout', way='id')
            self.phone.doAction(element=cancelEle, action='click')
            if drop is True:
                positive = self.phone.getElement(alias='net.medlinker.medlinker:id/positive_button', way='id')
                self.phone.doAction(element=positive, action='click')
                timeIndex = int(time.time())
                sign = False
                while int(time.time()) - timeIndex <= 5:
                    try:
                        self.getElement(alias=details, way='name')
                    except Exception:
                        time.sleep(1)
                        continue
                    else:
                        sign = True
                        break
                if sign:
                    raise ATException('Publish post [%s] success.' % details)
                else:
                    self.logger.passInfo('Publish post [%s] failed, the post has not been published.' % details)
            else:
                negative = self.phone.getElement(alias='net.medlinker.medlinker:id/negative_button', way='id')
                self.phone.doAction(element=negative, action='click')

        return details

    def postPublish(self, title=None):
        if self.getTitle() != 'Common_circle_doctor':
            raise ATException('Current page is [%s], there is no method named postPublish()')
        pubEle = self.phone.getElement(alias='net.medlinker.medlinker:id/right_button_layout', way='id')
        self.phone.doAction(element=pubEle, action='click')
        # self.phone.scrollScreen(direction='up')
        time.sleep(1)
        try:
            self.phone.driver.find_element_by_name(name='发布')
        except Exception as e:
            self.phone.setCurrentPage(self.phone.pageManager.getSpecPage(self.phone, title='Common_circle_doctor'))
            if title is None:
                self.logger.passInfo('The current page is [%s]' % self.phone.getCurrentPage().getTitle())
            else:
                self.logger.fail(
                    'The current page is [%s], publish post failed' % self.phone.getCurrentPage().getTitle())
        else:
            if title is None:
                self.logger.passInfo(
                    'The current page is [%s], publish post failed.' % self.phone.getCurrentPage().getTitle())
                return

        timeIndex = int(time.time())
        sign = False
        while int(time.time()) - timeIndex <= 15:
            try:
                self.getElement(alias=title, way='name')
            except Exception:
                time.sleep(1)
                continue
            else:
                sign = True
                break
        if sign:
            self.logger.passInfo('Publish post [%s] success.' % title)
        else:
            self.logger.fail('Publish post [%s] failed, cannot find the published post.' % title)

    def choseDepart(self, depart, subDepart):

        departEle = self.phone.driver.find_element_by_name(name=depart)
        self.doAction(element=departEle, action='click')
        subDepartEle = self.phone.driver.find_element_by_name(name=subDepart)
        self.doAction(element=subDepartEle, action='click')
        self.phone.setCurrentPage(self.phone.pageManager.getSpecPage(self.phone, title='InfoEdit_index'))
        timeIndex = int(time.time())
        sign = False
        while int(time.time()) - timeIndex <= 10:
            time.sleep(1)
            try:
                self.getElement(alias='primary', force=True)
            except Exception:
                continue
            else:
                sign = True
                break
        if sign:
            self.logger.passInfo('Arrive page [InfoEdit_index].')
        else:
            raise ATException('Can not arrive page [InfoEdit_index].')
