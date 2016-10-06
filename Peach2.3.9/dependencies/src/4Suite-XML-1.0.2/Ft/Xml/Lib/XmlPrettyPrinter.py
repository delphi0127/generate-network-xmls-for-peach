########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Lib/XmlPrettyPrinter.py,v 1.10 2005/02/09 09:11:13 mbrown Exp $
"""
This module supports formatted document serialization in XML syntax.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from XmlPrinter import XmlPrinter

class XmlPrettyPrinter(XmlPrinter):
    """
    An XmlPrettyPrinter instance provides functions for serializing an
    XML or XML-like document to a stream, based on SAX-like event calls
    initiated by an Ft.Xml.Lib.Print.PrintVisitor instance.

    The methods in this subclass of XmlPrinter produce the same output
    as the base class, but with extra whitespace added for visual
    formatting. The indent attribute is the string used for each level
    of indenting. It defaults to 2 spaces.
    """

    # The amount of indent for each level of nesting
    indent = '  '

    def __init__(self, stream, encoding):
        XmlPrinter.__init__(self, stream, encoding)
        self._level = 0
        self._canIndent = False  # don't indent first element
        return

    def startElement(self, namespaceUri, tagName, namespaces, attributes):
        if self._inElement:
            self.writeAscii('>')
            self._inElement = False
        if self._canIndent:
            self.writeAscii('\n' + (self.indent * self._level))
        XmlPrinter.startElement(self, namespaceUri, tagName, namespaces,
                                attributes)
        self._level += 1
        self._canIndent = True
        return

    def endElement(self, namespaceUri, tagName):
        self._level -= 1
        # Do not break short tag form (<tag/>)
        if self._canIndent and not self._inElement:
            self.writeAscii('\n' + (self.indent * self._level))
        XmlPrinter.endElement(self, namespaceUri, tagName)
        # Allow indenting after endtags
        self._canIndent = True
        return

    def text(self, data, disableEscaping=0):
        XmlPrinter.text(self, data, disableEscaping)
        # Do not allow indenting for elements with mixed content
        self._canIndent = False
        return

    def cdataSection(self, data):
        XmlPrinter.cdataSection(self, data)
        # Do not allow indenting for elements with mixed content
        self._canIndent = False
        return

    def processingInstruction(self, target, data):
        if self._inElement:
            self.writeAscii('>')
            self._inElement = False
        if self._canIndent:
            self.writeAscii('\n' + (self.indent * self._level))
        XmlPrinter.processingInstruction(self, target, data)
        # Allow indenting after processing instructions
        self._canIndent = True
        return

    def comment(self, data):
        if self._inElement:
            self.writeAscii('>')
            self._inElement = False
        if self._canIndent:
            self.writeAscii('\n' + (self.indent * self._level))
        XmlPrinter.comment(self, data)
        # Allow indenting after comments
        self._canIndent = True
        return
