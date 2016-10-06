########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/DomWriter.py,v 1.15 2005/03/28 09:04:20 mbrown Exp $
"""
DOM DocumentFragment writer for XSLT output

Much inspired by RtfWriter.

Copyright (c) 2000-2001 Alexandre Fayolle (France).

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation.

THIS PROGRAM IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
"""

from xml.dom import Node

from Ft.Xml import XMLNS_NAMESPACE, EMPTY_NAMESPACE
from Ft.Xml.Domlette import implementation
from Ft.Xml.Lib.XmlString import SplitQName
from Ft.Xml.Xslt import NullWriter


class DomWriter(NullWriter.NullWriter):
    def __init__(self, ownerDoc=None, implementation=implementation, outputParams=None):
        """
        Note: if no ownerDoc, there is no way to set the document's base URI.
        """
        NullWriter.NullWriter.__init__(self)
        if not ownerDoc:
            ownerDoc = implementation.createDocument(None, None, None)
            self._root = ownerDoc
        else:
            self._root = ownerDoc.createDocumentFragment()
        self._ownerDoc = ownerDoc
        self._nodeStack = [self._root]
        self._currElement = None
        self._currText = ''
        return

    def _completeTextNode(self):
        if self._currText and len(self._nodeStack) and self._nodeStack[-1].nodeType != Node.DOCUMENT_NODE:
            new_text = self._ownerDoc.createTextNode(self._currText)
            self._nodeStack[-1].appendChild(new_text)
        self._currText = ''
        return

    def getResult(self):
        self._completeTextNode()
        return self._root

    def startElement(self, name, namespace=EMPTY_NAMESPACE, extraNss=None):
        self._completeTextNode()
        new_element = self._ownerDoc.createElementNS(namespace, name)
        self._nodeStack.append(new_element)
        extraNss = extraNss or {}
        prefix, localName = SplitQName(name)
        for prefix in extraNss.keys():
            if prefix:
                new_element.setAttributeNS(XMLNS_NAMESPACE,
                                           'xmlns:'+prefix,
                                           extraNss[prefix])
            else:
                new_element.setAttributeNS(XMLNS_NAMESPACE,
                                           'xmlns',
                                           extraNss[None] or u'')
        return

    def endElement(self, name, namespace=EMPTY_NAMESPACE):
        self._completeTextNode()
        new_element = self._nodeStack[-1]
        del self._nodeStack[-1]
        self._nodeStack[-1].appendChild(new_element)
        return

    def text(self, text, escapeOutput=True):
        """
        The escapeOutput parameter is ignored
        """
        #new_text = self._ownerDoc.createTextNode(text)
        #self._nodeStack[-1].appendChild(new_text)
        self._currText = self._currText + text
        return

    def attribute(self, name, value, namespace=EMPTY_NAMESPACE):
        # Attributes can only occur in element scope for result trees
        if self._nodeStack[-1].nodeType == Node.ELEMENT_NODE:
            self._nodeStack[-1].setAttributeNS(namespace, name, value)
        return

    def processingInstruction(self, target, data):
        self._completeTextNode()
        pi = self._ownerDoc.createProcessingInstruction(target,data)
        self._nodeStack[-1].appendChild(pi)
        return

    def comment(self, text):
        self._completeTextNode()
        comment = self._ownerDoc.createComment(text)
        self._nodeStack[-1].appendChild(comment)
        return

