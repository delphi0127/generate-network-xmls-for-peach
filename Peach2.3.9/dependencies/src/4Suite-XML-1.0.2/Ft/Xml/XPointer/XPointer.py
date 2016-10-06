########################################################################
#
# File Name:   XPointer.py
#
# Docs:        http://docs.4suite.org/XPointer/XPointer.py.html
#
"""
A Parsed Token that represents a list of XPointers
WWW: http://4suite.org/XPointer        e-mail: support@4suite.org

Copyright (c) 2000-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from xml.dom import Node, XML_NAMESPACE, XMLNS_NAMESPACE

from Ft.Xml.XPointer import XPtrContext
from Ft.Xml.Lib.XmlString import XmlStrStrip, IsNCName

__all__ = ['Pointer', 'Shorthand', 'SchemeBased', 'PointerPart',
           'ElementScheme', 'XmlnsScheme', 'XPointerScheme', 'Scheme',
           ]

import XPtrExprParserc
_xpointerSchemeParser = XPtrExprParserc.XPtrExprParser()
del XPtrExprParserc

class Pointer:

    def pprint(self, indent=''):
        print indent + str(self)

    def __str__(self):
        return "<%s at %s: %r>" % (self.__class__.__name__, id(self), self)

    def __repr__(self):
        raise NotImplementedError


class Shorthand(Pointer):

    def __init__(self, identifier):
        self.identifier = identifier

    def select(self, context):
        doc = context.node.rootNode
        element = doc.getElementById(self.identifier)
        if element is None:
            return []
        return [element]

    def __repr__(self):
        return self.identifier


class SchemeBased(Pointer):

    def __init__(self, parts):
        self.parts = parts

    def select(self, context):
        for part in self.parts:
            node_set = part.evaluate(context)
            if node_set:
                return node_set
        # No schemes found an node
        return []

    def pprint(self, indent=''):
        print indent + str(self)
        for part in self.parts:
            part.pprint(indent + '  ')

    def __repr__(self):
        return ' '.join(map(repr, self.parts))


class PointerPart(Pointer):
    """
    Implementation of an unsupported XPointer scheme.
    """
    # The constructor is not needed by subclasses
    def __init__(self, name, data):
        self.name = name
        self.data = data

    def evaluate(self, context):
        return []

    def pprint(self, indent=''):
        print indent + str(self)

    def __str__(self):
        return "<%s at %s: %r>" % (self.__class__.__name__, id(self), self)

    def __repr__(self):
        return '%s(%s)' % (self.name, self.data)


class ElementScheme(PointerPart):
    """
    Implementation of XPointer element() scheme.
    """
    def __init__(self, name, data):
        sequence = data.split('/')
        self.identifier = sequence[0]
        if self.identifier and not IsNCName(self.identifier):
            raise SyntaxError("parse error, expecting NCName or '/'")
        self.sequence = []
        for item in sequence[1:]:
            try:
                item = int(item)
            except ValueError:
                item = -1
            if item <= 0:
                raise SyntaxError('parse error, expecting Integer')
            self.sequence.append(item)
        return

    def evaluate(self, context):
        node = context.node.rootNode
        if self.identifier:
            node = node.getElementById(self.identifier)
            if node is None:
                return []

        for index in self.sequence:
            elements = [ child for child in node.childNodes
                         if child.nodeType == Node.ELEMENT_NODE ]
            try:
                node = elements[index-1]
            except IndexError:
                return []
        return [node]

    def __repr__(self):
        result = self.identifier
        for index in self.sequence:
            result = result + '/%d' % index
        return 'element(%s)' % result


class XmlnsScheme(PointerPart):
    """
    Implementation of XPointer xmlns() scheme.
    """

    def __init__(self, name, data):
        try:
            prefix, uri = data.split('=', 1)
        except:
            raise SyntaxError('parse error, expected =')
        else:
            prefix = XmlStrStrip(prefix)
            uri = XmlStrStrip(uri)
        if not (prefix and IsNCName(prefix)):
            raise SyntaxError('parse error, expected NCName')
        if not uri:
            raise SyntaxError('parse error, expected EscapedNamespaceName')
        self.prefix = prefix
        self.uri = uri

    def evaluate(self, context):
        if self.prefix != u'xml' and self.uri not in (XML_NAMESPACE,
                                                      XMLNS_NAMESPACE):
            context.processorNss[self.prefix] = self.uri
        return []

    def __repr__(self):
        return 'xmlns(%s=%s)' % (self.prefix, self.uri)


class XPointerScheme(PointerPart):
    """
    Implementation of XPointer xpointer() scheme.
    """

    def __init__(self, name, data):
        self.expr = _xpointerSchemeParser.parse(data)

    def evaluate(self, context):
        return self.expr.evaluate(context)

    def pprint(self, indent=''):
        print indent + str(self)
        self.expr.pprint(indent+'  ')

    def __repr__(self):
        return 'xpointer(%r)' % self.expr


def Scheme(name, data):
    try:
        scheme = Schemes[name]
    except KeyError:
        scheme = PointerPart
    return scheme(name, data)


Schemes = {
    'element' : ElementScheme,
    'xmlns' : XmlnsScheme,
    'xpointer' : XPointerScheme,
    }

