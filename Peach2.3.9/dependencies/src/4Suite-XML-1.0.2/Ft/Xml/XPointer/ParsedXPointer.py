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

#import types, string
from Ft.Xml.XPath import CoreFunctions
from Ft.Xml.XPointer import XPtrContext, XPtrException
from Ft.Xml.Domlette import GetAllNs

class BareName:
    def __init__(self, name):
        self.name = name

    def select(self, context):
        doc = context.node.rootNode
        result = CoreFunctions._FindIds(doc, self.name, [])
        if len(result) > 1:
            raise Exception("ID must be unique")
        elif result:
            return result[0].ownerElement
        raise XPtrException(XPtrException.SUB_RESOURCE_ERROR)

    def pprint(self, indent=''):
        print indent + str(self)

    def __str__(self):
        return '<BareName at %x: %s>' % (id(self), self.name)

    def __repr__(self):
        return self.name


class ChildSequence:
    def __init__(self, sequence):
        if type(sequence[0]) != type(1):
            self.bareName = sequence[0]
            self.sequence = sequence[1:]
        else:
            self.bareName = None
            self.sequence = sequence

    def select(self, context):
        if self.bareName:
            node = self.bareName.select(context)
        else:
            node = context.node.rootNode
        for index in self.sequence:
            try:
                node = node.childNodes[index]
            except IndexError:
                raise XPtrException(XPtrException.SUB_RESOURCE_ERROR)
        return node

    def pprint(self, indent=''):
        print indent + str(self)

    def __str__(self):
        return '<ChildSequence at %x: %s>' % (id(self), repr(self))

    def __repr__(self):
        result = self.bareName and repr(self.bareName) or ''
        for index in self.sequence:
            result = result + '/%d' % index
        return result


class FullXPtr:
    def __init__(self, parts):
        self.parts = parts

    def select(self, document, contextNode, nss=None):
        nss = nss or {}
        nss.update(GetAllNs(document))
        context = XPtrContext.XPtrContext(document, 1, 1, contextNode, nss)
        for part in self.parts:
            node_set = part.evaluate(context)
            if len(node_set) == 1:
                return node_set[0]
            elif node_set:
                # The scheme found more than 1 node
                raise XPtrException(XPtrException.SUB_RESOURCE_ERROR)
            # Nothing found, try the next one
        # No schemes found an node
        raise XPtrException(XPtrException.SUB_RESOURCE_ERROR)

    def pprint(self, indent=''):
        print indent + str(self)
        for part in self.parts:
            part.pprint(indent + '  ')

    def __str__(self):
        return '<FullXPtr at %x: %s>' % (id(self), repr(self))

    def __repr__(self):
        return reduce(lambda result, part:
                      result + ' ' + repr(part),
                      self.parts, '')

