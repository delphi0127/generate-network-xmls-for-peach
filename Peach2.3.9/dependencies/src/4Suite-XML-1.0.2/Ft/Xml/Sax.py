########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Sax.py,v 1.8 2006/04/12 21:06:09 uogbuji Exp $
"""
Abstraction module for Domlette SAX usage.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys
from Ft.Xml.cDomlettec import CreateParser

# Alias function definition to allow for use with xml.sax.make_parser()
# To create a parser using this method, use the following:
#   parser = xml.sax.make_parser(['Ft.Xml.Sax'])
create_parser = CreateParser

# 4Suite-specific SAX features
from Ft.Xml.cDomlettec import FEATURE_PROCESS_XINCLUDES
from Ft.Xml.cDomlettec import FEATURE_GENERATOR

# 4Suite-specific SAX properties
from Ft.Xml.cDomlettec import PROPERTY_WHITESPACE_RULES
from Ft.Xml.cDomlettec import PROPERTY_YIELD_RESULT

from Ft.Xml import XMLNS_NAMESPACE
from Ft.Xml.Lib.XmlPrinter import XmlPrinter

class ContentHandler:
    """Interface for receiving logical document content events.

    This is the main callback interface for the Parser. The order of
    events in this interface mirrors the order of the information in the
    document."""

    def setDocumentLocator(self, locator):
        """Called by the parser to give the application a locator for
        locating the origin of document events.

        The locator allows the application to determine the end
        position of any document-related event, even if the parser is
        not reporting an error. Typically, the application will use
        this information for reporting its own errors (such as
        character content that does not match an application's
        business rules). The information returned by the locator is
        probably not sufficient for use with a search engine.

        Note that the locator will return correct information only
        during the invocation of the events in this interface. The
        application should not attempt to use it at any other time."""

    def startDocument(self):
        """Receive notification of the beginning of a document.

        The parser will invoke this method only once, before any
        other methods in this interface."""

    def endDocument(self):
        """Receive notification of the end of a document.

        The parser will invoke this method only once, and it will
        be the last method invoked during the parse. The parser shall
        not invoke this method until it has either abandoned parsing
        (because of an unrecoverable error) or reached the end of
        input."""

    def startPrefixMapping(self, prefix, uri):
        """Begin the scope of a prefix-URI Namespace mapping.

        The information from this event is not necessary for normal
        Namespace processing: the XmlParser will automatically replace
        prefixes for element and attribute names.

        There are cases, however, when applications need to use
        prefixes in character data or in attribute values, where they
        cannot safely be expanded automatically; the
        start/endPrefixMapping event supplies the information to the
        application to expand prefixes in those contexts itself, if
        necessary.

        Note that start/endPrefixMapping events are not guaranteed to
        be properly nested relative to each-other: all
        startPrefixMapping events will occur before the corresponding
        startElementNS event, and all endPrefixMapping events will occur
        after the corresponding endElementNS event, but their order is
        not guaranteed."""

    def endPrefixMapping(self, prefix):
        """End the scope of a prefix-URI mapping.

        See startPrefixMapping for details. This event will always
        occur after the corresponding endElementNS event, but the order
        of endPrefixMapping events is not otherwise guaranteed."""

    def startElementNS(self, (uri, localName), qualifiedName, atts):
        """Signals the start of an element.

        The uri parameter is None for elements which have no namespace,
        the qualifiedName parameter is the raw XML name used in the source
        document, and the atts parameter holds an instance of the
        Attributes class containing the attributes of the element.
        """

    def endElementNS(self, (uri, localName), qualifiedName):
        """Signals the end of an element.

        The uri parameter is None for elements which have no namespace,
        the qualifiedName parameter is the raw XML name used in the source
        document."""

    def characters(self, content):
        """Receive notification of character data.

        The parser will call this method to report each chunk of
        character data.   The parser will return all contiguous
        character data in a single chunk."""


class Locator:
    """Interface for associating a parse event with a document
    location. A locator object will return valid results only during
    calls to ContentHandler methods; at any other time, the results are
    unpredictable."""

    def getColumnNumber(self):
        """Return the column number where the current event ends."""

    def getLineNumber(self):
        """Return the line number where the current event ends."""

    def getSystemId(self):
        """Return the system identifier for the current event."""


class Attributes:
    """Interface for a set of XML attributes.

    Contains a set of XML attributes, accessible by expanded name."""

    def getValue(self, name):
        """Returns the value of the attribute with the given name."""

    def getQNameByName(self, name):
        """Returns the qualified name of the attribute with the given name."""

    def __len__(self):
        """Returns the number of attributes in the list."""
        return len(self._values)

    def __getitem__(self, name):
        """Alias for getValue."""

    def __delitem__(self, name):
        """Removes the attribute with the given name."""

    def __contains__(self, name):
        """Alias for has_key."""

    def has_key(self, name):
        """Returns True if the attribute name is in the list,
        False otherwise."""

    def get(self, name, alternative=None):
        """Return the value associated with attribute name; if it is not
        available, then return the alternative."""

    def keys(self):
        """Returns a list of the names of all attribute in the list."""

    def items(self):
        """Return a list of (attribute_name, value) pairs."""

    def values(self):
        """Return a list of all attribute values."""


class DomBuilder(ContentHandler):
    """
    A ContentHandler that is used to construct a Domlette Document.
    """

    def __init__(self):
        self._ownerDoc = None
        return

    def getDocument(self):
        """
        Returns the newly constructed Document instance.
        """
        return self._ownerDoc

    def startDocument(self):
        from Ft.Xml.Domlette import implementation
        self._ownerDoc = implementation.createRootNode()
        self._namespaces = {}
        self._nodeStack = [self._ownerDoc]
        return

    def endDocument(self):
        del self._nodeStack[-1]
        assert len(self._nodeStack) == 0, "orphaned node stack"
        return

    def startPrefixMapping(self, prefix, uri):
        self._namespaces[prefix] = uri
        return

    def startElementNS(self, expandedName, qualifiedName, attributes):
        namespaceURI, localName = expandedName
        element = self._ownerDoc.createElementNS(namespaceURI, qualifiedName)

        for prefix in self._namespaces:
            if prefix:
                qualifiedName = u'xmlns:' + prefix
            else:
                qualifiedName = u'xmlns'
            value = self._namespaces[prefix]
            element.setAttributeNS(XMLNS_NAMESPACE, qualifiedName, value)
        self._namespaces = {}

        for expandedName in attributes:
            namespaceURI, localName = expandedName
            qualifiedName = attributes.getQNameByName(expandedName)
            value = attributes[expandedName]
            element.setAttributeNS(namespaceURI, qualifiedName, value)

        self._nodeStack.append(element)
        return

    def endElementNS(self, expandedName, qualifiedName):
        element = self._nodeStack.pop()
        self._nodeStack[-1].appendChild(element)
        return

    def characters(self, data):
        text = self._ownerDoc.createTextNode(data)
        self._nodeStack[-1].appendChild(text)
        return


class SaxPrinter(ContentHandler):
    """
    A ContentHandler that serializes the result using a 4Suite printer
    """

    def __init__(self, printer=XmlPrinter(sys.stdout, 'utf-8')):
        self._printer = printer
        try:
            self._printer.reset()
        except AttributeError:
            pass
        self._namespaces = {}
        return

    def startDocument(self):
        self._printer.startDocument()
        return

    def endDocument(self):
        self._printer.endDocument()
        return

    def startPrefixMapping(self, prefix, uri):
        self._namespaces[prefix] = uri
        return

    def startElementNS(self, (namespaceURI, localName), qualifiedName,
                       attributes):
        attributes = dict([ (attributes.getQNameByName(name), value)
                            for name, value in attributes.items() ])
        self._printer.startElement(namespaceURI, qualifiedName,
                                   self._namespaces, attributes)
        self._namespaces = {}
        return

    def endElementNS(self, (namespaceURI, localName), qualifiedName):
        self._printer.endElement(namespaceURI, qualifiedName)
        return

    def characters(self, data):
        self._printer.text(data)
        return

