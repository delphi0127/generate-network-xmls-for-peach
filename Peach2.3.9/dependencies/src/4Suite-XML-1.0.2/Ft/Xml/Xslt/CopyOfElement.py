########################################################################
#
# File Name:            CopyOfElement.py
#
# Documentation:        http://docs.4suite.org/4XSLT/CopyOfElement.py.html
#
"""
Implementation of the XSLT Spec copy-of element.
WWW: http://4suite.org/4XSLT        e-mail: support@4suite.org

Copyright (c) 1999-2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from xml.dom import Node
from Ft.Xml import EMPTY_NAMESPACE, XMLNS_NAMESPACE
from Ft.Xml.Xslt import XsltElement, XsltException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt import CategoryTypes, ContentInfo, AttributeInfo
from Ft.Xml.XPath import Conversions, NAMESPACE_NODE


class CopyOfElement(XsltElement):

    category = CategoryTypes.INSTRUCTION
    content = ContentInfo.Empty
    legalAttrs = {
        'select' : AttributeInfo.Expression(required=1),
        }

    def instantiate(self, context, processor):
        context.processorNss = self.namespaces
        context.currentInstruction = self

        writer = processor.writers[-1]
        result = self._select.evaluate(context)
        if hasattr(result, "nodeType"):
            writer.copyNodes(result)
        elif type(result) == type([]) :
            #FIXME: Should probably do a sort-doc-order first
            for child in result:
                writer.copyNodes(child)
        else:
            string = Conversions.StringValue(result)
            writer.text(string)

        return


def CopyNode(processor, node):
    processor.writers[-1].copyNodes(node)
    return


from Ft.Xml.Domlette import GetAllNs

def OldCopyNode(processor, node):
    if node.nodeType in [Node.DOCUMENT_NODE, Node.DOCUMENT_FRAGMENT_NODE]:
        for child in node.childNodes:
            CopyNode(processor, child)
    if node.nodeType == Node.TEXT_NODE:
        processor.writers[-1].text(node.data, node.xsltOutputEscaping)
    elif node.nodeType == Node.ELEMENT_NODE:
        #The GetAllNs is needed to copy the namespace nodes
        processor.writers[-1].startElement(node.nodeName, node.namespaceURI,
                                           extraNss=GetAllNs(node))
        for attr in node.attributes.values():
            if attr.namespaceURI != XMLNS_NAMESPACE:
                processor.writers[-1].attribute(attr.name, attr.value,
                                                attr.namespaceURI)
        for child in node.childNodes:
            CopyNode(processor, child)
        processor.writers[-1].endElement(node.nodeName, node.namespaceURI)
    elif node.nodeType == Node.ATTRIBUTE_NODE:
        if node.namespaceURI != XMLNS_NAMESPACE:
            processor.writers[-1].attribute(node.name, node.value,
                                            node.namespaceURI)
    elif node.nodeType == Node.COMMENT_NODE:
        processor.writers[-1].comment(node.data)
    elif node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
        processor.writers[-1].processingInstruction(node.target, node.data)
    elif node.nodeType == NAMESPACE_NODE:
        processor.writers[-1].namespace(node.nodeName, node.value)
    else:
        pass
    return

