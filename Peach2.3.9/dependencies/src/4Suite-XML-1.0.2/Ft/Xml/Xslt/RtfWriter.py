########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/RtfWriter.py,v 1.20 2006/08/22 00:38:32 jkloth Exp $
"""
Result Tree Fragment writer for XSLT output

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Xml import XMLNS_NAMESPACE, EMPTY_NAMESPACE
from Ft.Xml.Domlette import implementation, Text
from Ft.Xml.Xslt.NullWriter import NullWriter

class RtfWriter(NullWriter):
    """
    A special, simple writer for capturing result-tree fragments
    """
    def __init__(self, outputParams, baseUri, implementation=implementation):
        """
        Note: The implementation must support createRootNode(baseUri).
        """
        NullWriter.__init__(self, outputParams)
        self._document = implementation.createRootNode(baseUri)
        self._destination_node = self._document
        self._characterData = []
        self._escapeOutput = True
        return

    def __completeTextNode(self):
        # Dump accumulated character data into a single text node;
        # called by the methods that will be generating other nodes.
        if self._characterData:
            data = u''.join(self._characterData)
            if self._escapeOutput:
                text = self._document.createTextNode(data)
            else:
                text = _UnescapedText(self._document, data)
            self._destination_node.appendChild(text)
            del self._characterData[:]
        return

    def getResult(self):
        self.__completeTextNode()
        assert self._destination_node is self._document, \
               "endElement not called (top of stack: '%s')" % (self._destination_node.nodeName)

        return self._document

    def startElement(self, name, namespace=EMPTY_NAMESPACE, extraNss=None):
        self.__completeTextNode()

        # Add the new element to the document
        element = self._document.createElementNS(namespace, name)
        self._destination_node.appendChild(element)

        # Add the additional namespaces to the added element
        namespaces = extraNss or {}
        for prefix, uri in namespaces.items():
            if prefix:
                nodeName = u'xmlns:' + prefix
            elif not uri:
                # no prefix and no uri indicates default namespace NOT set
                continue
            else:
                nodeName = u'xmlns'
            element.setAttributeNS(XMLNS_NAMESPACE, nodeName, uri)

        self._destination_node = element
        return

    def endElement(self, name, namespace=EMPTY_NAMESPACE):
        self.__completeTextNode()

        # Using assert since they are stripped when running optimized (-O)
        # (shouldn't happen anyway)
        assert name == self._destination_node.nodeName, \
               "nodeName mismatch for startElement/endElement"

        self._destination_node = self._destination_node.parentNode
        return

    def attribute(self, name, value, namespace=EMPTY_NAMESPACE):
        # From XSLT 1.0 Section 7.1.3 (we implement recovery here,
        # if processing gets this far):
        # - Adding an attribute to an element after children have been added
        #   to it; implementations may either signal the error or ignore the
        #   attribute.
        # - Adding an attribute to a node that is not an element;
        #   implementations may either signal the error or ignore the
        #   attribute.
        if self._destination_node.attributes is not None and \
               not self._destination_node.childNodes:
            self._destination_node.setAttributeNS(namespace, name, value)
        return

    def text(self, data, escapeOutput=True):
        if self._escapeOutput != escapeOutput:
            self.__completeTextNode()
            self._escapeOutput = escapeOutput
        self._characterData.append(data)
        return

    def processingInstruction(self, target, data):
        self.__completeTextNode()
        node = self._document.createProcessingInstruction(target, data)
        self._destination_node.appendChild(node)
        return

    def comment(self, data):
        self.__completeTextNode()
        node = self._document.createComment(data)
        self._destination_node.appendChild(node)
        return


class _UnescapedText(Text):
    xsltOutputEscaping = False