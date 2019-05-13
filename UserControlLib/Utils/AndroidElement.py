# -*- coding: utf-8 -*-

import re
import xml.etree.ElementTree as ElementTree
from Framework.Exception import ATException

PROPERTIES = (
    'index', 'text', 'resource_id', 'classalias', 'package', 'content_desc', 'checkable', 'checked', 'clickable',
    'enabled', 'focusable', 'focused', 'scrollable', 'long_clickable', 'password', 'selected', 'bounds', 'xpath',
    'alias', 'click', 'swipe_left', 'swipe_right', 'primary', 'doubleclick'
)


class AndroidElement(object):
    WIDTH = 0
    HEIGHT = 0

    def __init__(self, params):
        for pro in PROPERTIES:
            if pro in params:
                exec ('self.%s = params[\'%s\']' % (pro, pro))
            elif re.sub('_', '-', pro) in params:
                exec ('self.%s = params[\'%s\']' % (pro, re.sub('_', '-', pro)))
            elif 'class' in params:
                self.classalias = params['class']

    @classmethod
    def __xmlTreeToDict(cls, node):
        """Trans xml Element instance to a dict
        """
        if not isinstance(node, ElementTree.Element):
            raise ATException('_xmlTreeToDict(), param: [node] expected a xml.etree.ElementTree.Element')

        nodeDict = {}

        if len(node.items()) > 0:
            nodeDict.update(dict(node.items()))

        for child in node:
            childItemDict = cls.__xmlTreeToDict(child)
            nodeDict[child.tag + '_' + child.attrib['index']] = childItemDict

        return nodeDict

    @classmethod
    def __getXMLData(cls, xmlFile):
        """Trans xml file to a dict
        """
        root = None
        if not isinstance(xmlFile, basestring):
            raise ATException('getXMLData(), param: [xmlFile] expected a file path string.')

        try:
            tree = ElementTree.parse(xmlFile)
            root = tree.getroot()
        except IOError as ie:
            raise IOError(ie)
        except ElementTree.ParseError as epe:
            raise ElementTree.ParseError(epe)

        if root is None:
            raise ATException('XML file [%s] has not root element.' % xmlFile)
        result = {}
        temp = cls.__xmlTreeToDict(root)
        for key in temp.iterkeys():
            if key.startswith('node'):
                result[key] = temp[key]
        return result

    # @classmethod
    # def getElementData(cls, file):
    #
    #     data = cls.__getXMLData(file)
    #
    #     if cls.HEIGHT == 0:
    #         size = data['node_0']['bounds']
    #         matcher = re.search('\[(\d+),\s?(\d+)\]$', size)
    #         if matcher:
    #             cls.WIDTH = matcher.groups()[0]
    #             cls.HEIGHT = matcher.groups()[1]
    #
    #     def addXpath(dictx, prefix='/'):
    #         if not isinstance(dictx, dict):
    #             raise ATException('addXpath(): param [dictx] must be a dict.')
    #         matcher = None
    #         for key in dictx:
    #             if isinstance(dictx[key], dict) and 'class' in dictx[key]:
    #                 matcher = re.match('node_(\d+)', key)
    #                 if matcher and int(matcher.groups()[0]) > 0:
    #                     if len(prefix) > 1:
    #                         dictx[key].update(
    #                             {'xpath': '%s[%s]/%s' % (prefix, matcher.groups()[0], dictx[key]['class'])})
    #                     else:
    #                         dictx[key].update(
    #                             {'xpath': '%s/[%s]%s' % (prefix, matcher.groups()[0], dictx[key]['class'])})
    #                 else:
    #                     dictx[key].update({'xpath': '%s/%s' % (prefix, dictx[key]['class'])})
    #                 addXpath(dictx[key], dictx[key]['xpath'])
    #         return dictx
    #
    #     return addXpath(data)

    @classmethod
    def getElementData(cls, file):

        data = cls.__getXMLData(file)

        if cls.HEIGHT == 0:
            size = data['node_0']['bounds']
            matcher = re.search('\[(\d+),\s?(\d+)\]$', size)
            if matcher:
                cls.WIDTH = matcher.groups()[0]
                cls.HEIGHT = matcher.groups()[1]

        def addXpath(dictx, prefix='/'):
            if not isinstance(dictx, dict):
                raise ATException('addXpath(): param [dictx] must be a dict.')
            matcher = None
            for key in dictx:
                if isinstance(dictx[key], dict) and 'class' in dictx[key]:
                    matcher = re.match('node_(\d+)', key)
                    if matcher:
                        if 'alias' in dictx[key]:
                            if re.search('EditText', dictx[key]['class'], re.I) or re.search('_text', dictx[key]['alias'], re.I):
                                dictx[key]['xpath'] = '//%s[contains(@resource-id, \'%s\') and contains(@index, \'%s\')]' \
                                           % (dictx[key]['class'], dictx[key]['resource-id'], dictx[key]['index'])
                            else:
                                dictx[key]['xpath'] = '//%s[contains(@text, \'%s\') and contains(@resource-id, \'%s\') and contains(@index, \'%s\')]' \
                                           % (dictx[key]['class'], dictx[key]['text'], dictx[key]['resource-id'],
                                              dictx[key]['index'])
                    addXpath(dictx[key])
            return dictx

        return addXpath(data)

    def getProperty(self, name=None):
        if not name:
            result = {}
            for item in PROPERTIES:
                if hasattr(self, item):
                    exec ('result[%s] = self.%s' % (item, item))
        elif name in PROPERTIES:
            pro = eval('self.%s' % name)
            return pro
        else:
            raise ATException('AndroidElement has no property named [%s].' % name)
