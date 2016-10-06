########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/NullWriter.py,v 1.12 2006/08/22 00:38:32 jkloth Exp $
"""
Interface definition for XSLT output writers

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from xml.dom import Node

from Ft.Xml import EMPTY_NAMESPACE, XMLNS_NAMESPACE
from Ft.Xml.Domlette import GetAllNs
from Ft.Xml.XPath import NAMESPACE_NODE

from OutputParameters import OutputParameters


class NullWriter:
    """
    All XSLT output writers should subclass NullWriter
    """
    def __init__(self, outputParams=None):
        """
        outputParams - If given, an instance of
        Ft.Xml.Xslt.OutputParameters.OutputParameters, from which the
        standard XSLT output parameters can be read.
        """
        self._outputParams = outputParams or OutputParameters()
        return

    def getMediaType(self):
        """
        Returns the media type of the output, as a string.
        """
        return self._outputParams.mediaType

    def getStream(self):
        """
        If the output is being directed to a stream (Python file-like object),
        returns the stream without any encoding wrappers.
        """
        return None

    def getResult(self):
        """
        If the output is being buffered, returns the buffered result
        (as a byte string, usually).
        """
        return ''

    def startDocument(self):
        """
        Called once at the beginning of output writing.
        """
        return

    def endDocument(self):
        """
        Called once at the end of output writing.
        """
        return

    def text(self, text, escapeOutput=True):
        """
        Called when a text node is generated in the result tree.

        text - content of the text node.
        escapeOutput - deprecated; ignore.
        """
        return

    def attribute(self, name, value, namespace=EMPTY_NAMESPACE):
        """
        Called when an attribute node is generated in the result tree.

        name - the local name.
        value - the attribute value.
        namespace - the namespace URI.
        """
        return

    def processingInstruction(self, target, data):
        """
        Called when an processing instruction node is generated in the result tree.

        target - the instruction target.
        data - the instruction.
        """
        return

    def comment(self, body):
        """
        Called when a comment node is generated in the result tree.

        body - comment text.
        """
        return

    def startElement(self, name, namespace=EMPTY_NAMESPACE, extraNss=None):
        """
        Called when an element node is generated in the result tree.
        Subsequent method calls generate the element's attributes and content.

        name - the local name.
        namespace - the namespace URI.
        extraNss - new namespace bindings (dictionary of prefixes to URIs)
                   established by this element
        """
        return

    def endElement(self, name, namespace=EMPTY_NAMESPACE):
        """
        Called at the end of element node generation.

        name - the local name.
        namespace - the namespace URI.
        """
        return

    def namespace(self, prefix, namespace):
        """
        Called when a namespace node is explicitly generated in the result tree
        (as by the xsl:namespace instruction).

        prefix - the prefix.
        namespace - the namespace URI.
        """
        return

    def copyNodes(self, nodeOrNodelist):
        """
        Copies the given list of Domlette nodes by calling the appropriate methods.
        Generally does not need to be overridden.
        """
        if isinstance(nodeOrNodelist, list):
            for node in nodeOrNodelist:
                self.copyNodes(node)
            return
        node = nodeOrNodelist
        if node.nodeType in [Node.DOCUMENT_NODE, Node.DOCUMENT_FRAGMENT_NODE]:
            for child in node.childNodes:
                self.copyNodes(child)
        if node.nodeType == Node.TEXT_NODE:
            self.text(node.data, node.xsltOutputEscaping)
        elif node.nodeType == Node.ELEMENT_NODE:
            # The GetAllNs is needed to copy the namespace nodes
            self.startElement(node.nodeName, node.namespaceURI,
                              extraNss=GetAllNs(node))
            for attr in node.xpathAttributes:
                self.attribute(attr.name, attr.value, attr.namespaceURI)
            for child in node.childNodes:
                self.copyNodes(child)
            self.endElement(node.nodeName, node.namespaceURI)
        elif node.nodeType == Node.ATTRIBUTE_NODE:
            if node.namespaceURI != XMLNS_NAMESPACE:
                self.attribute(node.name, node.value, node.namespaceURI)
        elif node.nodeType == Node.COMMENT_NODE:
            self.comment(node.data)
        elif node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
            self.processingInstruction(node.target, node.data)
        elif node.nodeType == NAMESPACE_NODE:
            self.namespace(node.nodeName, node.value)
        else:
            pass
        return

