########################################################################
#
# File Name:            CallTemplateElement.py
#
# Documentation:        http://docs.4suite.org/4XSLT/CallTemplateElement.py.html
#
"""
Implementation of the XSLT Spec call-template stylesheet element.
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from xml.dom import Node
from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XsltRuntimeException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes, AttributeInfo, ContentInfo

class CallTemplateElement(XsltElement):

    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Rep(ContentInfo.QName(XSL_NAMESPACE, 'xsl:with-param'))
    legalAttrs = {
        'name' : AttributeInfo.QName(required=1),
        }

    doesSetup = doesPrime = 1

    def setup(self):
        self._tail_recursive = 0
        self._called_template = None
        self._params = map(lambda with_param:
                           (with_param, with_param._name, with_param._select),
                           self.children)
        return
        
    def prime(self, processor, context):
        self._called_template = processor._namedTemplates.get(self._name)
        if not self._called_template:
            return

        # check for tail recursion
        current = self.parent
        while current is not processor.stylesheet:
            if current is self._called_template:
                # we are within the template that we call
                if self.isLastChild():
                    use_tail = 1
                    node = self.parent
                    while node is not current:
                        if not (node.isLastChild() and \
                                (node.expandedName[0] == XSL_NAMESPACE and 
                                 node.expandedName[1] in ['choose', 'if',
                                                          'otherwise', 'when'])
                                ):
                            use_tail = 0
                            break
                        node = node.parent
                    self._tail_recursive = use_tail
                break
            current = current.parent
        return

    def instantiate(self, context, processor):
        # setup parameters for called template

        # This handles the case of top-level variables using call-templates
        if not self._called_template:
            self.prime(processor, context)
            self._called_template = processor._namedTemplates.get(self._name)
            if not self._called_template:
                raise XsltRuntimeException(Error.NAMED_TEMPLATE_NOT_FOUND,
                                           self, self._name)
            self._called_template.prime(processor, context)

        # We need to calculate the parameters before the variable context
        # is changed back in the template element
        params = {}
        for (param, name, expr) in self._params:
            context.processorNss = param.namespaces
            context.currentInstruction = param
            params[name] = expr.evaluate(context)

        if self._tail_recursive:
            context.recursiveParams = params
        else:
            context.currentNode = context.node
            self._called_template.instantiate(context, processor, params)
        return
