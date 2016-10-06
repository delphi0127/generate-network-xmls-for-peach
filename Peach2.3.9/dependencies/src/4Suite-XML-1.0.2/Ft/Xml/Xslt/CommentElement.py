########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/CommentElement.py,v 1.9.2.1 2006/12/08 18:16:13 jkloth Exp $
"""
xsl:comment instruction implementation

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""
from Ft.Xml.Xslt import XSL_NAMESPACE, XsltElement
from Ft.Xml.Xslt import XsltRuntimeException, Error
from Ft.Xml.Xslt import CategoryTypes, ContentInfo

class CommentElement(XsltElement):

    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Template
    legalAttrs = {}

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        processor.pushResultString()
        had_nontext = 0
        try:
            for child in self.children:
                child.instantiate(context, processor)
                if processor.writers[-1].had_nontext:
                    had_nontext = 1
        finally:
            if had_nontext:
                raise XsltRuntimeException(Error.NONTEXT_IN_COMMENT, self)
            content = processor.popResult()

        # Per the spec, comment data can't contain '--' or end with '-',
        # but we are allowed to add a space. (XSLT 1.0 sec. 7.4)
        content = content.replace(u'--', u'- -')
        if content[-1:] == u'-':
            content += u' '

        processor.writers[-1].comment(content)

        return
