########################################################################
#
# File Name:            MessageElement.py
#
# Documentation:        http://docs.4suite.org/4XSLT/MessageElement.py.html
#
"""
Implementation of the XSLT Spec import stylesheet element.
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

import cStringIO
from Ft.Xml.Xslt import XsltElement, XsltRuntimeException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo
from Ft.Xml.Xslt import OutputParameters, XmlWriter

class MessageElement(XsltElement):
    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Template
    legalAttrs = {
        'terminate' : AttributeInfo.YesNo(default='no'),
        }

    def instantiate(self, context, processor):
        op = OutputParameters.OutputParameters()
        op.method = "xml"
        op.encoding = processor.writers[-1]._outputParams.encoding
        op.omitXmlDeclaration = 1
        stream = cStringIO.StringIO()
        processor.pushResult(XmlWriter.XmlWriter(op, stream))
        try:
            for child in self.children:
                child.instantiate(context, processor)
        finally:
            processor.popResult()
        msg = stream.getvalue()

        if self._terminate:
            raise XsltRuntimeException(Error.STYLESHEET_REQUESTED_TERMINATION, 
                                       self, msg)
        else:
            processor.xslMessage(msg)

        return

