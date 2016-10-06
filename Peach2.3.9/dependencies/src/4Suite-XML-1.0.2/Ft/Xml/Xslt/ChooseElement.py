########################################################################
#
# File Name:            ChooseElement.py
#
# Documentation:        http://docs.4suite.org/4XSLT/ChooseElement.py.html
#
"""
Implementation of the XSLT Spec choose instruction
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Xml.Xslt import XsltElement, XsltException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes
from Ft.Xml.Xslt import ContentInfo, AttributeInfo
from Ft.Xml.XPath import Conversions

class WhenElement(XsltElement):
    category = None
    content = ContentInfo.Template
    legalAttrs = {
        'test' : AttributeInfo.BooleanExpression(required=1),
        }


class OtherwiseElement(XsltElement):
    category = None
    content = ContentInfo.Template
    legalAttrs = {}


class ChooseElement(XsltElement):

    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Seq(
        ContentInfo.Rep1(ContentInfo.QName(XSL_NAMESPACE, 'xsl:when')),
        ContentInfo.Opt(ContentInfo.QName(XSL_NAMESPACE, 'xsl:otherwise')),
        )
    legalAttrs = {}

    doesSetup = 1

    def setup(self):
        if not self.children:
            raise XsltException(Error.CHOOSE_REQUIRES_WHEN)
        return

    def instantiate(self, context, processor):

        chosen = None
        for child in self.children:
            context.processorNss = child.namespaces
            context.currentInstruction = child
            if isinstance(child, WhenElement):
                if Conversions.BooleanValue(child._test.evaluate(context)):
                    chosen = child
                    break
            else:
                # xsl:otherwise
                chosen = child

        if chosen:
            for child in chosen.children:
                child.instantiate(context, processor)

        return
