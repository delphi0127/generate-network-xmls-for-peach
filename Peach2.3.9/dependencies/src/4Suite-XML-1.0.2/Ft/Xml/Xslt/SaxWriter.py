########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/SaxWriter.py,v 1.9 2005/03/18 23:47:19 jkloth Exp $
"""
SAX2 event writer for XSLT output

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os

from Ft.Xml import EMPTY_NAMESPACE, XMLNS_NAMESPACE
from Ft.Xml import CheckVersion
from Ft.Xml.Domlette import implementation
from Ft.Xml.Lib.XmlString import IsXmlSpace, SplitQName
from Ft.Xml.XPath import Util
from Ft.Xml.Xslt import XSL_NAMESPACE, TextSax
from Ft.Xml.Xslt import OutputParameters


class ElementData:
    def __init__(self, name, attrs, extraNss=None):
        self.name = name
        self.attrs = attrs
        self.extraNss = extraNss or {}


try:
    from xml.dom.ext.reader import Sax, Sax2, HtmlSax
except ImportError:
    #It will be caught if a SaxWriter is created
    pass

class SaxWriter:
    """
    Requires PyXML (will be checked at instantiation time).
    """
    def __init__(self, outputParams, saxHandler=None, fragment=False):
        CheckVersion(feature="4XSLT's SaxWriter")
        self.__fragment = fragment
        self.__firstElementFlag = True
        self.__orphanedNodes = []
        self.__saxHandlerClass = None
        self.__saxHandler = None
        self.__stateStack = []
        self.__currElement = None
        self.__currText = u''
        self._outputParams = outputParams or OutputParameters.OutputParameters()
        if saxHandler:
            self.__saxHandler = saxHandler
        elif self.__outputParams.method == 'xml':
            self.__initSaxHandler(Sax2.XmlDomGenerator)
            if self.__outputParams.omitXmlDeclaration in [None, 'no']:
                self.__saxHandler.xmlDecl(
                    self.__outputParams.version,
                    self.__outputParams.encoding,
                    self.__outputParams.standalone
                    )
        elif self.__outputParams.method == 'html':
            self.__initSaxHandler(HtmlSax.HtmlDomGenerator)
        elif self.__outputParams.method == 'text':
            self.__initSaxHandler(TextSax.TextGenerator)

    def startDocument(self):
        return

    def endDocument(self):
        return

    def complete(self):
        return self.__saxHandler and self.__saxHandler.getRootNode() or None

    def getResult(self):
        self.__completeTextNode()
        return self.__saxHandler.getRootNode()

    def __initSaxHandler(self, saxHandlerClass):
        self.__saxHandlerClass = saxHandlerClass
        self.__saxHandler = saxHandlerClass(keepAllWs=1)
        for o_node in self.__orphanedNodes:
            if o_node[0] == 'pi':
                self.__saxHandler.processingInstruction(o_node[1], o_node[2])
            elif o_node[0] == 'comment':
                self.__saxHandler.comment(o_node[1])
        del self.__orphanedNodes
        return

    def __initSax2Doc(self, doctype):
        self.__firstElementFlag = False
        if not self.__fragment:
            if not self.__saxHandler:
                self.__initSaxHandler(Sax2.XmlDomGenerator)
                if self.__outputParams.omitXmlDeclaration in [None, 'no']:
                    self.__saxHandler.xmlDecl(
                        self.__outputParams.version,
                        self.__outputParams.encoding,
                        self.__outputParams.standalone
                        )
            self.__saxHandler.startDTD(doctype, self.__outputParams.doctypeSystem, self.__outputParams.doctypePublic)
            self.__saxHandler.endDTD()
        return

    def __initHtmlSaxDoc(self, doctype):
        self.__firstElementFlag = False
        if not self.__saxHandler:
            self.__initSaxHandler(HtmlSax.HtmlDomGenerator)
        #self.__saxHandler._4dom_startDTD(doctype, self.__outputParams.doctypeSystem, self.__outputParams.doctypePublic)
        #self.__saxHandler.endDTD()

    def __completeTextNode(self):
        #FIXME: This does not allow multiple root nodes, which is required to be supported
        if self.__currText:
            if IsXmlSpace(self.__currText):
                self.__saxHandler.ignorableWhitespace(self.__currText)
            else:
                self.__saxHandler.characters(self.__currText)
            self.__currText = u''
        return

    def startElement(self, name, namespace=EMPTY_NAMESPACE, extraNss=None):
        extraNss = extraNss or {}
        attrs = {}
        if self.__firstElementFlag:
            if not self.__outputParams.method:
                if not namespace and name.upper() == 'HTML':
                    self.__outputParams.method = 'html'
                else:
                    self.__outputParams.method = 'xml'
            if self.__outputParams.method == 'xml':
                self.__initSax2Doc(name)
            else:
                self.__initHtmlSaxDoc(name)
            self.__firstElementFlag = False
        self.__completeTextNode()
        if self.__currElement:
            self.__saxHandler.startElement(self.__currElement.name, self.__currElement.attrs)
            self.__currElement = None
        self.__currElement = ElementData(name, attrs, extraNss)
        if self.__outputParams.method == 'xml':
            if namespace:
                (prefix, local) = SplitQName(name)
                if prefix:
                    self.__currElement.attrs["xmlns:"+prefix] = namespace
                else:
                    self.__currElement.attrs["xmlns"] = namespace
            for prefix in extraNss.keys():
                if prefix:
                    new_element.setAttributeNS(XMLNS_NAMESPACE,
                                               u'xmlns:'+prefix,
                                               extraNss[prefix])
                else:
                    new_element.setAttributeNS(XMLNS_NAMESPACE,
                                               u'xmlns',
                                               extraNss[''])
        return

    def endElement(self, name):
        self.__completeTextNode()
        if self.__currElement:
            self.__saxHandler.startElement(
                self.__currElement.name,
                self.__currElement.attrs
                )
            self.__currElement = None
        self.__saxHandler.endElement(name)
        return

    def text(self, text, escapeOutput=True):
        if self.__currElement:
            self.__saxHandler.startElement(
                self.__currElement.name,
                self.__currElement.attrs
                )
            self.__currElement = None
        self.__saxHandler.characters(text)
        return

    def attribute(self, name, value, namespace=EMPTY_NAMESPACE):
        self.__currElement.attrs[name] = value
        if namespace:
            (prefix, local) = SplitQName(name)
            if prefix:
                self.__currElement.attrs[u"xmlns:"+prefix] = namespace
        return

    def processingInstruction(self, target, data):
        self.__completeTextNode()
        if self.__saxHandler:
            self.__saxHandler.processingInstruction(target, data)
        else:
            self.__orphanedNodes.append(('pi', target, data))
        return

    def comment(self, body):
        self.__completeTextNode()
        if self.__saxHandler:
            self.__saxHandler.comment(body)
        else:
            self.__orphanedNodes.append(('comment', body))
        return

