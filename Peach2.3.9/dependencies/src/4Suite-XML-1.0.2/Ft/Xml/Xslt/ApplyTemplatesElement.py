########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/ApplyTemplatesElement.py,v 1.10 2005/04/06 23:05:47 jkloth Exp $
"""
Implementation of xsl:apply-templates instruction

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XSL_NAMESPACE, XsltRuntimeException, Error
from Ft.Xml.Xslt import CategoryTypes, AttributeInfo, ContentInfo
from Ft.Xml.Xslt.XPathExtensions import SortedExpression

class ApplyTemplatesElement(XsltElement):

    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Rep(
        ContentInfo.Alt(ContentInfo.QName(XSL_NAMESPACE, 'xsl:sort'),
                        ContentInfo.QName(XSL_NAMESPACE, 'xsl:with-param'))
        )
    legalAttrs = {
        'select' : AttributeInfo.Expression(),
        'mode' : AttributeInfo.QName(),
        }

    doesSetup = 1

    def setup(self):
        sort_keys = []
        self._params = []
        for child in self.children:
            # only XSL children are guaranteed by the validation
            name = child.expandedName[1]
            if name == 'sort':
                sort_keys.append(child)
            elif name == 'with-param':
                self._params.append((child, child._name, child._select))

        if sort_keys:
            self._select = SortedExpression(self._select, sort_keys)
        return

    # hooks for Fourthought extension element (mode as AVT)

    def _instantiate_mode(self, context):
        return self._mode

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        with_params = {}
        for (param, name, expr) in self._params:
            context.processorNss = param.namespaces
            context.currentInstruction = param
            with_params[name] = expr.evaluate(context)

        if self._select:
            node_set = self._select.evaluate(context)
            # it must really be a node-set, and if XSLT 1.0, not a result tree fragment
            if not isinstance(node_set, list):
                raise XsltRuntimeException(
                    Error.ILLEGAL_APPLYTEMPLATE_NODESET, self)
        else:
            node_set = context.node.childNodes

        # Iterate over the nodes
        state = context.copy()
        mode = context.mode
        context.mode = self._instantiate_mode(context)

        pos = 1
        size = len(node_set)
        for node in node_set:
            context.node, context.position, context.size = node, pos, size
            processor.applyTemplates(context, with_params)
            pos += 1

        context.mode = mode
        context.set(state)
        return
