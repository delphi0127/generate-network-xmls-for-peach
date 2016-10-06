########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/LiteralElement.py,v 1.12 2005/04/06 23:05:47 jkloth Exp $
"""
Implementation of XSLT literal result elements

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Xml.XPath import RuntimeException as XPathRuntimeException
from Ft.Xml.Xslt import XsltElement, XsltRuntimeException, Error

class LiteralElement(XsltElement):

    # usually not supplied so default it
    _use_attribute_sets = []

    # This will be called by the stylesheet if it contains any
    # xsl:namespace-alias declarations
    def fixupAliases(self, namespaceAliases):
        # handle the element itself
        if self._output_namespace in namespaceAliases:
            alias_info = namespaceAliases[self._output_namespace]
            self._output_namespace, prefix = alias_info
            if prefix:
                self.nodeName = u':'.join([prefix, self.expandedName[1]])
            else:
                self.nodeName = self.expandedName[1]

        # reprocess the attributes
        pos = 0
        for qname, namespace, value in self._output_attrs:
            # NOTE - attributes do not use the default namespace
            if namespace and namespace in namespaceAliases:
                namespace, prefix = namespaceAliases[namespace]
                local = qname.split(':')[-1]
                if prefix:
                    qname = u':'.join([prefix, local])
                else:
                    qname = local
                self._output_attrs[pos] = (qname, namespace, value)
            pos += 1

        # handle the namespaces
        for prefix, namespace in self._output_nss.items():
            if namespace in namespaceAliases:
                # remove the old entry
                del self._output_nss[prefix]
                # get the aliased namespace and set that pairing
                namespace, prefix = namespaceAliases[namespace]
                self._output_nss[prefix] = namespace

        return

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        processor.writers[-1].startElement(self.nodeName,
                                           self._output_namespace,
                                           self._output_nss)

        for (qname, namespace, value) in self._output_attrs:
            try:
                value = value.evaluate(context)
            except XPathRuntimeException, e:
                import MessageSource
                e.message = MessageSource.EXPRESSION_POSITION_INFO % (
                    self.baseUri, self.lineNumber, self.columnNumber,
                    value.source, str(e))
                raise
            except XsltRuntimeException, e:
                import MessageSource
                e.message = MessageSource.XSLT_EXPRESSION_POSITION_INFO % (
                    str(e), value.source)
                raise
            except Exception, e:
                import MessageSource
                import cStringIO, traceback
                tb = cStringIO.StringIO()
                tb.write("Lower-level traceback:\n")
                traceback.print_exc(1000, tb)
                raise RuntimeError(MessageSource.EXPRESSION_POSITION_INFO % (
                    self.baseUri, self.lineNumber, self.columnNumber,
                    value.source, tb.getvalue()))

            processor.writers[-1].attribute(qname, value, namespace)

        for attr_set_name in self._use_attribute_sets:
            try:
                attr_set = processor.attributeSets[attr_set_name]
            except KeyError:
                raise XsltRuntimeException(Error.UNDEFINED_ATTRIBUTE_SET,
                                           self, attr_set_name)
            attr_set.instantiate(context, processor)

        for child in self.children:
            child.instantiate(context, processor)

        processor.writers[-1].endElement(self.nodeName,
                                         self._output_namespace)
        return
