########################################################################
#
# File Name:            ProcessingInstructionElement.py
#
# Documentation:        http://docs.4suite.org/4XSLT/ProcessingInstructionElement.py.html
#
"""
Implementation of the XSLT Spec processing-instruction stylesheet element.
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Xml.Xslt import XsltElement, XsltRuntimeException, Error
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo

class ProcessingInstructionElement(XsltElement):
    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Template
    legalAttrs = {
        'name' : AttributeInfo.NCNameAvt(required=1),
        }

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        target = self._name.evaluate(context)
        if target.lower() == 'xml':
            raise XsltRuntimeException(Error.ILLEGAL_XML_PI, self)

        processor.pushResultString()
        had_nontext = 0
        try:
            for child in self.children:
                child.instantiate(context, processor)
                if processor.writers[-1].had_nontext:
                    had_nontext = 1
        finally:
            if had_nontext:
                raise XsltRuntimeException(Error.NONTEXT_IN_PI, self)
            content = processor.popResult()

        # Per the spec, PI data can't contain '?>', but we are allowed
        # to replace it with '? >' instead of signalling an error.
        data = content.replace(u'?>', u'? >')
        processor.writers[-1].processingInstruction(target, data)

        return
