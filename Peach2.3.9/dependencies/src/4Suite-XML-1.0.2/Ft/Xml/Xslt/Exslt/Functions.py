"""
EXSLT 2.0 - Functions (http://www.exslt.org/func/index.html)
WWW: http://4suite.org/XSLT        e-mail: support@4suite.org

Copyright (c) 2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Xml import XPath
from Ft.Xml.Xslt import XSL_NAMESPACE, XsltElement
from Ft.Xml.Xslt import XsltRuntimeException
from Ft.Xml.Xslt import ContentInfo, AttributeInfo
from Ft.Xml.Xslt.Exslt.MessageSource import Error as ExsltError
from Ft.Xml.Xslt.XPathExtensions import RtfExpr

EXSL_FUNCTIONS_NS = 'http://exslt.org/functions'

class FunctionElement(XsltElement):

    content = ContentInfo.Seq(
        ContentInfo.Rep(ContentInfo.QName(XSL_NAMESPACE, 'xsl:param')),
        ContentInfo.Template,
        )

    legalAttrs = {
        'name' : AttributeInfo.QNameButNotNCName(required=1),
        }

    doesPrime = True

    def prime(self, processor, context):
        context.addFunction(self._name, self)
        return

    def __call__(self, context, *args):
        processor = context.processor

        # Save context state as XPath is side-effect free
        ctx_state = context.copy()
        ctx_namespaces = context.processorNss
        ctx_instruction = context.currentInstruction

        context.processorNss = self.namespaces
        context.currentInstruction = self

        # Set the parameter list
        counter = 0
        self.result = u''
        for child in self.children:
            if child.expandedName == (XSL_NAMESPACE, 'param'):
                if counter < len(args):
                    context.varBindings[child._name] = args[counter]
                else:
                    # default
                    child.instantiate(context, processor)
                counter = counter + 1
            else:
                child.instantiate(context, processor)

        # Restore context state
        context.currentInstruction = ctx_instruction
        context.processorNss = ctx_namespaces
        context.set(ctx_state)
        
        return self.result


class ResultElement(XsltElement):
    """
    When an func:result element is instantiated, during the
    instantiation of a func:function element, the function returns
    with its value.
    """

    content = ContentInfo.Template
    legalAttrs = {
        'select' : AttributeInfo.Expression(),
        }

    doesSetup = doesPrime = True

    def setup(self):
        if not self._select:
            self._select = RtfExpr(self.children)
        return

    def prime(self, processor, context):
        self._function = None
        current = self.parent
        while current:
            # this loop will stop when it hits the top of the tree
            if current.expandedName == (EXSL_FUNCTIONS_NS, 'function'):
                self._function = current
                break
            current = current.parent

        if not self._function:
            raise XsltRuntimeException(ExsltError.RESULT_NOT_IN_FUNCTION, self)

        if not self.isLastChild():
            siblings = self.parent.children
            for node in siblings[siblings.index(self)+1:]:
                if node.expandedName != (XSL_NAMESPACE, 'fallback'):
                    raise XsltRuntimeException(ExsltError.ILLEGAL_RESULT_SIBLINGS,
                                               self)
        return

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self
        self._function.result = self._select.evaluate(context)
        return


class ScriptElement(XsltElement):
    """
    NOT YET IMPLEMENTED

    The top-level func:script element provides an implementation of
    extension functions in a particular namespace.
    """
    pass


ExtNamespaces = {
    EXSL_FUNCTIONS_NS : 'func',
    }

ExtFunctions = {}

ExtElements = {
    (EXSL_FUNCTIONS_NS, 'function'): FunctionElement,
    (EXSL_FUNCTIONS_NS, 'result'): ResultElement,
    #(EXSL_FUNCTIONS_NS, 'script'): ScriptElement,
    }
