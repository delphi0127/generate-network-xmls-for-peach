########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/AttributeElement.py,v 1.18 2005/04/06 23:05:47 jkloth Exp $
"""
Implementation of xsl:attribute element

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XsltRuntimeException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo

class AttributeElement(XsltElement):
    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Template
    legalAttrs = {
        'name' : AttributeInfo.RawQNameAvt(required=1),
        'namespace' : AttributeInfo.UriReferenceAvt(isNsName=1),
        }

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        (prefix, local) = self._name.evaluate(context)
        if prefix is not None:
            name = prefix + ':' + local
        else:
            name = local
        if name == 'xmlns':
            raise XsltRuntimeException(Error.BAD_ATTRIBUTE_NAME, self, name)

        # From sec. 7.1.3 of the XSLT spec,
        #  1. if 'namespace' attr is not present, use ns in scope, based on prefix
        #    from the element QName in the 'name' attr value; if no prefix, use
        #    empty namespace
        #  2. if 'namespace' attr is present and empty string, use empty ns ALWAYS
        #  3. if 'namespace' attr is present, namespace is attr value
        #
        if not self._namespace:
            if prefix is not None:
                if not self.namespaces.has_key(prefix):
                    raise XsltRuntimeException(Error.UNDEFINED_PREFIX,
                                               self, prefix)
                namespace = self.namespaces[prefix]
            else:
                namespace = EMPTY_NAMESPACE
        else:
            namespace = (self._namespace and self._namespace.evaluate(context)
                         or EMPTY_NAMESPACE)

        processor.pushResultString()
        had_nontext = 0
        try:
            for child in self.children:
                child.instantiate(context, processor)
                if processor.writers[-1].had_nontext:
                    had_nontext = 1
        finally:
            if had_nontext:
                raise XsltRuntimeException(Error.NONTEXT_IN_ATTRIBUTE, self)
            content = processor.popResult()

        processor.writers[-1].attribute(name, content, namespace)
        return

