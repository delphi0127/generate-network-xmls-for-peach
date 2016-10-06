########################################################################
#
# File Name:            WithParamElement.py
#
# Documentation:        http://docs.4suite.org/4XSLT/WithParamElement.py.html
#
"""
Implementation of the XSLT Spec with-param stylesheet element.
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XSL_NAMESPACE
from Ft.Xml.Xslt import AttributeInfo, ContentInfo
from Ft.Xml.Xslt.XPathExtensions import RtfExpr

class WithParamElement(XsltElement):
    category = None
    content = ContentInfo.Template
    legalAttrs = {
        'name' : AttributeInfo.QName(required=1),
        'select' : AttributeInfo.Expression(),
        }

    doesSetup = 1
    
    def setup(self):
        if not self._select:
            self._select = RtfExpr(self.children)
        return
