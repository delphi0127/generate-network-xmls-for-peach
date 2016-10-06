########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/ElementElement.py,v 1.14 2005/04/06 23:05:47 jkloth Exp $
"""
Implementation of xsl:element element

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XsltRuntimeException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo

class ElementElement(XsltElement):
    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Template
    legalAttrs = {
        'name' : AttributeInfo.RawQNameAvt(required=1),
        'namespace' : AttributeInfo.UriReferenceAvt(isNsName=1),
        'use-attribute-sets' : AttributeInfo.QNames(),
        }

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        (prefix, local) = self._name.evaluate(context)
        if prefix is not None:
            name = prefix + u':' + local
        else:
            name = local

        # From sec. 7.1.2 of the XSLT spec,
        #  1. if 'namespace' attr is not present, use ns in scope, based on prefix
        #    from the element QName in the 'name' attr value; if no prefix, use
        #    default ns in scope
        #  2. if 'namespace' attr is present and empty string, use empty ns ALWAYS
        #  3. if 'namespace' attr is present, namespace is attr value
        #
        if not self._namespace:
            if prefix is not None:
                if not self.namespaces.has_key(prefix):
                    raise XsltRuntimeException(Error.UNDEFINED_PREFIX, self, prefix)
                namespace = self.namespaces[prefix]
            else:
                namespace = self.namespaces[None]

        else:
            namespace = (self._namespace and self._namespace.evaluate(context)
                         or EMPTY_NAMESPACE)

        self.execute(context, processor, name, namespace)
        return

    def execute(self, context, processor, name, namespace):
        #FIXME: Use proper pysax AttributeList objects
        processor.writers[-1].startElement(name, namespace)
        for attr_set_name in self._use_attribute_sets:
            try:
                attr_set = processor.attributeSets[attr_set_name]
            except KeyError:
                raise XsltRuntimeException(Error.UNDEFINED_ATTRIBUTE_SET, self, attr_set_name)
            attr_set.instantiate(context, processor)

        for child in self.children:
            child.instantiate(context, processor)

        processor.writers[-1].endElement(name, namespace)
        return

