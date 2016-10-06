########################################################################
#
# File Name:            ApplyImportsElement.py
#
# Documentation:        http://docs.4suite.org/4XSLT/ApplyImportsElement.py.html
#
"""
Implementation of the XSLT Spec apply-imports stylesheet element.
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Xml.Xslt import XsltElement, XSL_NAMESPACE, XsltRuntimeException, Error
from Ft.Xml.Xslt import CategoryTypes, AttributeInfo, ContentInfo

class ApplyImportsElement(XsltElement):

    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Empty
    legalAttrs = {}

    def instantiate(self, context, processor):
        if not context.stylesheet:
            raise XsltRuntimeException(
                Error.APPLYIMPORTS_WITH_NULL_CURRENT_TEMPLATE, self)

        context.stylesheet.applyTemplates(context, processor,
                                          maxImport=self.importIndex)
        return
