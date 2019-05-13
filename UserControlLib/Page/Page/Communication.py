# -*- coding: utf-8 -*-

"""
    Effect:
"""
import time

import re

from Framework.Exception import ATException
from UserControlLib.Page.DetailsPageBase import DetailsPageBase


class Communication(DetailsPageBase):
    def __init__(self, phone, title):
        super(Communication, self).__init__(phone, title)

    def createGroup(self, friends=None):
        if not re.match('Communication_(more|contacts)', self.getTitle()):
            raise ATException('Page [%s] has no method createGroup()' % self.getTitle())
        self.__findEleAndClick(key='发起群聊')
        sign = self._hasSpecContent(key='邀请好友')
        if sign:
            self.logger.passInfo('Arrive all friend contact page')
        else:
            raise ATException('Arrive all friend contact page failed')

        if friends is None:
            friends = ['代杰文', '郭超']
        if not isinstance(friends, list):
            friends = [friends]
        if len(friends) > 1:
            title = '群聊(%s)' % (len(friends) + 1)
        else:
            title = friends[0]

        for item in friends:
            self.__findEleAndClick(key=item)

        self.__findEleAndClick(key='创建')

        sign = self._hasSpecContent(key=title)
        if sign:
            self.logger.passInfo('Create a chat [%s] success.' % title)
        else:
            raise ATException('Create a chat [%s] failed, maybe it has been timeout in 10s.' % title)
        # time.sleep(2)

    def __findEleAndClick(self, key, way='name'):
        ele = self.phone.getElement(alias=key, way=way, force=True)
        self.doAction(element=ele, action='click')

    def changeGroupName(self, name=None):
        if not re.match('Communication_(more|contacts)', self.getTitle()):
            raise ATException('Page [%s] has no method changeGroupName()' % self.getTitle())
        if not name:
            name = str(time.time())[-8:]
        self.__findEleAndClick(key='net.medlinker.medlinker:id/right_button_layout', way='id')
        sign = self._hasSpecContent(key='群管理')
        if sign:
            self.logger.passInfo('Arrived the chat group manage page.')
        else:
            raise ATException('Can not arrived the chat group manage page.')

        self.__findEleAndClick(key="net.medlinker.medlinker:id/rl_group_name", way='id')
        sign = self._hasSpecContent(key='群聊名称')
        if sign:
            self.logger.passInfo('Arrived the chat group name edit page.')
        else:
            raise ATException('Can not arrived the chat group name edit page.')

        ele = self.getElement(alias='net.medlinker.medlinker:id/edit_modify_name', way='id')
        self.doAction(element=ele, action='input', value=name)

        self.__findEleAndClick(key='net.medlinker.medlinker:id/left_button_layout', way='id')
        sign = self._hasSpecContent(key='群管理')
        if sign:
            self.logger.passInfo('Arrived the chat group manage page.')
        else:
            raise ATException('Can not arrived the chat group manage page.')

        if not self.getElement(alias=name, way='name', force=True):
            raise ATException('群名修改操作成功，但在群管理页面显示错误')

        self.__findEleAndClick(key='net.medlinker.medlinker:id/left_button_layout', way='id')
        sign = self._hasSpecContent(key='发送')
        if sign:
            self.logger.passInfo('Arrived the chat group send page.')
        else:
            raise ATException('Can not arrived the chat group send page.')
        title = self.getElement(alias='net.medlinker.medlinker:id/title', way='id').text.encode('utf-8')
        if not re.match(name, title):
            raise ATException('群名修改操作成功，但在聊天页面显示错误')
        return title

    def chat(self, message=None):
        if not re.match('Communication_(more|contacts)', self.getTitle()):
            raise ATException('Page [%s] has no method chat()' % self.getTitle())
        if not message:
            message = str(time.time())
        ele = self.getElement(alias='net.medlinker.medlinker:id/et_input', way='id')
        self.doAction(action='input', element=ele, value=message)
        self.__findEleAndClick(key='net.medlinker.medlinker:id/tv_send', way='id')

        if self.getElement(alias=message, way='name', force=True) and ele.text.encode('utf-8') != message:
            self.logger.passInfo('Send messgae [%s] successfully.')
        else:
            raise ATException('Send messgae [%s] failed.')

    def disbandGroup(self):
        if not re.match('Communication_(more|contacts)', self.getTitle()):
            raise ATException('Page [%s] has no method disbandGroup()' % self.getTitle())
        self.__findEleAndClick(key='net.medlinker.medlinker:id/right_button_layout', way='id')
        sign = self._hasSpecContent(key='群管理')
        if sign:
            self.logger.passInfo('Arrived the chat group manage page.')
        else:
            raise ATException('Can not arrived the chat group manage page.')

        self.__findEleAndClick(key='net.medlinker.medlinker:id/tv_to_chat', way='id')
        sign = self._hasSpecContent(key='确认解散此群')
        if not sign:
            raise ATException('Can not arrived the chat group manage page.')
        self.__findEleAndClick(key='net.medlinker.medlinker:id/positive_button', way='id')
        self.phone.setCurrentPage(self.phone.pageManager.getSpecPage(self.phone, title='Message_index'))
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
            self.logger.passInfo('Arrive page [Message_index].')
        else:
            raise ATException('Can not arrive page [Message_index].')
