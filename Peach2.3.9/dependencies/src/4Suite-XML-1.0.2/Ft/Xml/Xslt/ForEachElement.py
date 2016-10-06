########################################################################
#
# File Name:            ForEachElement.py
#
# Documentation:        http://docs.4suite.org/4XSLT/ForEachElement.py.html
#
"""
Implementation of the XSLT Spec for-each stylesheet element.
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XsltRuntimeException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo
from Ft.Xml.Xslt.XPathExtensions import SortedExpression

from Ft.Xml.Xslt.SortElement import SortElement

class ForEachElement(XsltElement):

    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Seq(
        ContentInfo.Rep(ContentInfo.QName(XSL_NAMESPACE, 'xsl:sort')),
        ContentInfo.Template)
    legalAttrs = {
        'select' : AttributeInfo.NodeSetExpression(required=1),
        }
    
    doesSetup = 1

    def setup(self):
        sort_keys = filter(lambda x: isinstance(x, SortElement), self.children)
        if sort_keys:
            self._select = SortedExpression(self._select, sort_keys)
        return

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        if self._select:
            node_set = self._select.evaluate(context)
            if type(node_set) != type([]):
                raise XsltRuntimeException(Error.INVALID_FOREACH_SELECT, self)
        else:
            node_set = context.node.childNodes

        state = context.copy()
        pos = 1
        size = len(node_set)
        for node in node_set:
            context.node, context.position, context.size = node, pos, size
            context.currentNode = node
            for child in self.children:
                child.instantiate(context, processor)
            pos += 1

        context.set(state)
        return
