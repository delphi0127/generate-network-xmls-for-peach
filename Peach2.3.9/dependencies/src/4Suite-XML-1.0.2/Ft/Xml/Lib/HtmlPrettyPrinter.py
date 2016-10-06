########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Lib/HtmlPrettyPrinter.py,v 1.12 2005/02/09 09:12:06 mbrown Exp $
"""
This module supports formatted document serialization in HTML syntax.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Xml import EMPTY_NAMESPACE

from HtmlPrinter import HtmlPrinter


class HtmlPrettyPrinter(HtmlPrinter):
    """
    An HtmlPrettyPrinter instance provides functions for serializing an
    XML or XML-like document to a stream, based on SAX-like event calls
    initiated by an Ft.Xml.Lib.Print.PrintVisitor instance.

    The methods in this subclass of HtmlPrinter attempt to emit a
    document conformant to the HTML 4.01 syntax, with extra whitespace
    added for visual formatting. The indent attribute is the string used
    for each level of indenting. It defaults to 2 spaces.
    """

    # The amount of indent for each level of nesting
    indent = '  '

    def __init__(self, stream, encoding):
        HtmlPrinter.__init__(self, stream, encoding)
        self._level = 0

        # indenting control variables
        self._isInline = [1]  # prevent newline before first element
        self._inNoIndent = [0]
        self._indentForbidden = 0
        self._indentEndTag = False
        return

    def startElement(self, namespaceUri, tagName, namespaces, attributes):
        if self._inElement:
            self.writeAscii('>')
            self._inElement = False

        # Create the lookup key for the various lookup tables
        key = (namespaceUri, tagName.lower())

        # Get the inline flag for this element
        inline = key in self.inlineElements

        if not inline and not self._isInline[-1] and not self._indentForbidden:
            self.writeAscii('\n' + (self.indent * self._level))

        HtmlPrinter.startElement(self, namespaceUri, tagName, namespaces,
                                 attributes)

        # Setup indenting rules for this element
        self._isInline.append(inline)
        self._inNoIndent.append(key in self.noIndentElements)
        self._indentForbidden += self._inNoIndent[-1]
        self._level += 1
        self._indentEndTag = False
        return

    def endElement(self, namespaceUri, tagName):
        # Undo changes to indenting rules for this element
        self._level -= 1
        inline = self._isInline.pop()

        if self._inElement:
            # An empty non-null namespace element (use XML short form)
            self.writeAscii('/>')
            self._inElement = False
        else:
            if not inline and not self._indentForbidden and self._indentEndTag:
                self.writeAscii('\n' + (self.indent * self._level))

            HtmlPrinter.endElement(self, namespaceUri, tagName)

        self._indentForbidden -= self._inNoIndent.pop()
        self._indentEndTag = not inline
        return

    def processingInstruction(self, target, data):
        if self._inElement:
            self.writeAscii('>')
            self._inElement = False

        # OK to indent end-tag
        self._indentEndTag = True

        # try to indent
        if not self._isInline[-1] and not self._indentForbidden:
            self.writeAscii('\n' + (self.indent * self._level))
        HtmlPrinter.processingInstruction(self, target, data)
        return

    def comment(self, data):
        if self._inElement:
            self.writeAscii('>')
            self._inElement = False

        # OK to indent end-tag
        self._indentEndTag = True

        # try to indent
        if not self._isInline[-1] and not self._indentForbidden:
            self.writeAscii('\n' + (self.indent * self._level))
        HtmlPrinter.comment(self, data)
        return

    # Elements that should never be emitted on a new line.
    inlineElements = {}
    for name in ['tt', 'i', 'b', 'u', 's', 'strike', 'big', 'small', 'em',
                 'strong', 'dfn', 'code', 'samp', 'kbd', 'var', 'cite',
                 'abbr', 'acronym', 'a', 'img', 'applet', 'object', 'font',
                 'basefont', 'script', 'map', 'q', 'sub', 'sup', 'span',
                 'bdo', 'iframe', 'input', 'select', 'textarea', 'label',
                 'button']:
        inlineElements[(EMPTY_NAMESPACE, name)] = True

    # Elements that should never be emitted with additional
    # whitespace in their content; i.e., once you're inside
    # one, you don't do any more indenting.
    noIndentElements = {}
    for name in ['script', 'style', 'pre', 'textarea', 'xmp']:
        noIndentElements[(EMPTY_NAMESPACE, name)] = True

    del name
