# -*- coding: utf-8 -*-

"""
Effect : XML Parser
"""

import xml.etree.ElementTree as ElementTree
from Framework.Exception import ATException


class XMLParser:
    """Trans XML data to a dict consists of a list
    """
    def __init__(self):
        pass

    @classmethod
    def _xmlTreeToDict(cls, node):
        """Trans xml Element instance to a dict
        """
        if not isinstance(node, ElementTree.Element):
            raise ATException('_xmlTreeToDict(), param: [node] expected a xml.etree.ElementTree.Element')

        nodeDict = {}

        if len(node.items()) > 0:
            nodeDict.update(dict(node.items()))

        for child in node:
            childItemDict = cls._xmlTreeToDict(child)
            if child.tag in nodeDict:
                if isinstance(nodeDict[child.tag], list):
                    nodeDict[child.tag].append(childItemDict)
                else:
                    nodeDict[child.tag] = [nodeDict[child.tag], childItemDict]
            else:
                nodeDict[child.tag] = childItemDict

        text = ''
        if node.text is not None:
            text = node.text.strip()

        if len(nodeDict) > 0:
            if len(text) > 0:
                nodeDict[node.tag + '_text'] = text
        else:
            nodeDict = text

        return nodeDict

    @classmethod
    def getXMLData(cls, xmlFile):
        """Trans xml file to a dict
        """
        root = None
        if not isinstance(xmlFile, basestring):
            raise ATException('getXMLData(), param: [xmlFile] expected a file path string.')

        try:
            root = ElementTree.parse(xmlFile).getroot()
        except IOError as ie:
            raise IOError(ie)
        except ElementTree.ParseError as epe:
            raise ElementTree.ParseError(epe)

        if root is None:
            raise ATException('XML file [%s] has not root element.' % xmlFile)
        return dict({root.tag: cls._xmlTreeToDict(root)})

    @classmethod
    def __dictSearch(cls, tmpDict, key, value=None):
        """
        """
        tmpValue = tmpDict.get(key, None)
        if tmpValue is not None:
            if value is None:
                return tmpValue
            elif value is not None and tmpValue == value:
                return tmpDict
            elif value is not None and tmpValue != value:
                return None
        for child in tmpDict:
            tmpValue = cls.getSpecifiedKeyRawData(tmpDict[child], key, value)
            if tmpValue is not None:
                break
        return tmpValue

    @classmethod
    def getSpecifiedKeyRawData(cls, rawData, key, value=None):
        keywordValue = None

        if isinstance(rawData, dict):
            keywordValue = cls.__dictSearch(rawData, key, value)
        elif isinstance(rawData, list):
            for child in rawData:
                keywordValue = cls.getSpecifiedKeyRawData(child, key, value)
                if keywordValue is not None:
                    break
        return keywordValue