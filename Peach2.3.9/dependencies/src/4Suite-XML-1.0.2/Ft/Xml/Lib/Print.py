########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Lib/Print.py,v 1.27.4.1 2006/10/16 04:14:27 uogbuji Exp $
"""
This module supports document serialization in XML or HTML syntax.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys
from xml.dom import Node
from Ft.Xml import XML_NAMESPACE, XMLNS_NAMESPACE
import XmlPrinter, XmlPrettyPrinter, HtmlPrinter, HtmlPrettyPrinter

class PrintVisitor:
    """
    Provides functions to recursively walk a DOM or Domlette object and
    generate SAX-like event calls for each node encountered. See the
    printer classes (XMLPrinter, HTMLPrinter, etc.) for the event
    handlers.
    """
    def __init__(self, stream, encoding, nsHints=None, isHtml=False,
                 indent=False, canonical=False, addedAttributes=None,
                 removedNsDecls=None):
        """
        Initializes an instance of the class, selecting the appropriate
        printer to use, depending on the isHtml and indent flags.
        nsHints, if given, is a dictionary of namespace mappings that
        help determine if namespace declarations need to be emitted when
        visiting the first Element node.
        """
        if indent and isHtml:
            self.writer = HtmlPrettyPrinter.HtmlPrettyPrinter(stream, encoding)
        elif indent:
            self.writer = XmlPrettyPrinter.XmlPrettyPrinter(stream, encoding)
        elif isHtml:
            self.writer = HtmlPrinter.HtmlPrinter(stream, encoding)
        elif canonical:
            self.writer = XmlPrinter.CanonicalXmlPrinter(stream, encoding)
        else:
            self.writer = XmlPrinter.XmlPrinter(stream, encoding)

        # Namespaces
        self._namespaces = [{'xml' : XML_NAMESPACE}]
        self._nsHints = nsHints
        self._addedAttributes = addedAttributes or {}
        self._removedNsDecls = removedNsDecls or []
        return

    _dispatch = {}
    def visit(self, node):
        """
        Starts walking the tree at the given node.
        """
        try:
            node_type = node.nodeType
        except AttributeError:
            raise ValueError('Not a valid DOM node %r' % node)

        try:
            visit = self._dispatch[node_type]
        except KeyError:
            # unknown node type, try and get a "pretty" name for the error
            node_types = {}
            for name in dir(Node):
                if name.endswith('_NODE'):
                    node_types[getattr(Node, name)] = name
            node_type = node_types.get(node.node_type, node.node_type)
            raise ValueError('Unknown node type %r' % node_type)
        else:
            visit(self, node)
        return

    def visitNotImplemented(self, node):
        """
        Called when an known but unsupported type of node is
        encountered, always raising a NotImplementedError exception. The
        unsupported node types are those that require DTD subset
        support: entity nodes, entity reference nodes, and notation
        nodes.
        """
        raise NotImplementedError('Printing of %r' % node)
    _dispatch[Node.ENTITY_REFERENCE_NODE] = visitNotImplemented
    _dispatch[Node.ENTITY_NODE] = visitNotImplemented
    _dispatch[Node.NOTATION_NODE] = visitNotImplemented

    def visitDocumentFragment(self, node):
        """
        Called when a DocumentFragment node is encountered. Just
        proceeds to the node's children.
        """
        for child in node.childNodes:
            self.visit(child)
        return
    _dispatch[Node.DOCUMENT_FRAGMENT_NODE] = visitDocumentFragment

    def visitDocument(self, node):
        """
        Called when a Document node is encountered. Just proceeds to the
        associated DocumentType node, if any, and then to the node's
        children.
        """
        self.writer.startDocument()
        hasDocTypeNode = False
        if hasattr(node, 'doctype'):
            # DOM Level 1/2/3
            if node.doctype:
                hasDocTypeNode = True
                self.visitDocumentType(node.doctype)
            children = [ x for x in node.childNodes if x != node.doctype ]
        if not hasDocTypeNode and hasattr(node, 'systemId'):
            # Domlette
            if node.documentElement:
                self.writer.doctype(node.documentElement.tagName,
                                    node.publicId, node.systemId)
            children = node.childNodes

        for child in children:
            self.visit(child)
        return
    _dispatch[Node.DOCUMENT_NODE] = visitDocument

    def visitDocumentType(self, node):
        """
        Called when a DocumentType node is encountered. Generates a
        doctype event for the printer.
        """
        self.writer.doctype(node.name, node.publicId,
                            node.systemId)
        return
    _dispatch[Node.DOCUMENT_TYPE_NODE] = visitDocumentType

    def visitElement(self, node):
        """
        Called when an Element node is encountered. Generates for the
        printer a startElement event, events for the node's children
        (including attributes), and an endElement event.
        """
        current_nss = self._namespaces[-1].copy()

        # Gather the namespaces and attributes for writing
        namespaces = {}
        if self._nsHints:
            for prefix, namespaceUri in self._nsHints.items():
                # See if this namespace needs to be emitted
                if current_nss.get(prefix, 0) != namespaceUri:
                    namespaces[prefix] = namespaceUri
            self._nsHints = None
        if self._addedAttributes:
            attributes = self._addedAttributes
            self._addedAttributes = None
        else:
            attributes = {}

        for attr in node.attributes.values():
            # xmlns="uri" or xmlns:foo="uri"
            if attr.namespaceURI == XMLNS_NAMESPACE:
                if not attr.prefix:
                    # xmlns="uri"
                    prefix = None
                else:
                    # xmlns:foo="uri"
                    prefix = attr.localName
                if current_nss.get(prefix, 0) != attr.value:
                    namespaces[prefix] = attr.value
            else:
                attributes[attr.name] = attr.value

        # The element's namespaceURI/prefix mapping takes precedence
        if node.namespaceURI or current_nss.get(None, 0):
            if current_nss.get(node.prefix, 0) != node.namespaceURI:
                namespaces[node.prefix] = node.namespaceURI or u""

        #The 
        for prefix in self._removedNsDecls:
            del namespaces[prefix]
        tagName = getattr(node, 'tagName', getattr(node, 'nodeName'))
        self.writer.startElement(node.namespaceURI, tagName, namespaces,
                                 attributes)
        if self._removedNsDecls:
            self._removedNsDecls = []

        # Update in scope namespaces with those we emitted
        current_nss.update(namespaces)
        self._namespaces.append(current_nss)

        # Write out this node's children
        for child in node.childNodes:
            self.visit(child)

        self.writer.endElement(node.namespaceURI, tagName)

        del self._namespaces[-1]
        return
    _dispatch[Node.ELEMENT_NODE] = visitElement

    def visitAttribute(self, node):
        """
        Called when an Attribute node is encountered. Generates an
        attribute event for the printer.
        """
        self.writer.attribute(None, node.name, node.value)
        return
    _dispatch[Node.ATTRIBUTE_NODE] = visitAttribute

    def visitText(self, node):
        """
        Called when a Text node is encountered. Generates a text event
        for the printer.
        """
        self.writer.text(node.data)
        return
    _dispatch[Node.TEXT_NODE] = visitText

    def visitCDATASection(self, node):
        """
        Called when a CDATASection node is encountered. Generates a
        cdataSection event for the printer.
        """
        self.writer.cdataSection(node.data)
        return
    _dispatch[Node.CDATA_SECTION_NODE] = visitCDATASection

    def visitComment(self, node):
        """
        Called when a Comment node is encountered. Generates a comment
        event for the printer.
        """
        self.writer.comment(node.data)
        return
    _dispatch[Node.COMMENT_NODE] = visitComment

    def visitProcessingInstruction(self, node):
        """
        Called when a ProcessingInstruction node is encountered.
        Generates a processingInstruction event for the printer.
        """
        self.writer.processingInstruction(node.target, node.data)
        return
    _dispatch[Node.PROCESSING_INSTRUCTION_NODE] = visitProcessingInstruction


def Print(root, stream=sys.stdout, encoding='UTF-8', asHtml=None):
    """
    Given a Node instance assumed to be the root of a DOM or Domlette
    tree, this function serializes the document to the given stream or
    stdout, using the given encoding (UTF-8 is the default). The asHtml
    flag can be used to force HTML-style serialization of an XML DOM.
    Otherwise, the DOM type (HTML or XML) is automatically determined.
    This function does nothing if root is not a Node.

    It is preferable that users import this from Ft.Xml.Domlette
    rather than directly from Ft.Xml.Lib.
    """
    from Ft.Xml.Domlette import SeekNss
    if not hasattr(root, "nodeType"):
        return
    ns_hints = SeekNss(root)
    # When asHtml is not specified, choose output method from interface
    # of document node (getElementsByName is an HTML DOM only method)
    if asHtml is None:
        asHtml = hasattr(root.ownerDocument or root, 'getElementsByName')
    visitor = PrintVisitor(stream, encoding, ns_hints, asHtml, 0)
    visitor.visit(root)
    return


def PrettyPrint(root, stream=sys.stdout, encoding='UTF-8', asHtml=None):
    """
    Given a Node instance assumed to be the root of a DOM or Domlette
    tree, this function serializes the document to the given stream or
    stdout, using the given encoding (UTF-8 is the default). Extra
    whitespace is added to the output for visual formatting. The asHtml
    flag can be used to force HTML-style serialization of an XML DOM.
    Otherwise, the DOM type (HTML or XML) is automatically determined.
    This function does nothing if root is not a Node.

    Please import this from Ft.Xml.Domlette
    rather than directly from Ft.Xml.Lib.
    """
    from Ft.Xml.Domlette import SeekNss
    if not hasattr(root, "nodeType"):
        return
    ns_hints = SeekNss(root)
    # When asHtml is not specified, choose output method from interface
    # of document node (getElementsByName is an HTML DOM only method)
    if asHtml is None:
        asHtml = hasattr(root.ownerDocument or root, 'getElementsByName')
    visitor = PrintVisitor(stream, encoding, ns_hints, asHtml, 1)
    visitor.visit(root)
    stream.write('\n')
    return


def CanonicalPrint(root, stream=sys.stdout, exclusive=False,
                   inclusivePrefixes=None):
    """
    Given a Node instance assumed to be the root of an XML DOM or Domlette
    tree, this function serializes the document to the given stream or
    stdout, using c14n serialization, according to
    http://www.w3.org/TR/xml-c14n (the default) or
    http://www.w3.org/TR/xml-exc-c14n/
    This function does nothing if root is not a Node.

    exclusive - if true, apply exclusive c14n according to
        http://www.w3.org/TR/xml-exc-c14n/
    inclusivePrefixes - if exclusive is True, use this as a list of namespaces
        representing the "InclusiveNamespacesPrefixList" list in exclusive c14n

    Please import this from Ft.Xml.Domlette
    rather than directly from Ft.Xml.Lib.
    """
    from Ft.Xml.Domlette import SeekNss
    if not hasattr(root, "nodeType"):
        return
    added_attributes = {}  #All the contents should be XML NS attrs
    nshints = {}
    if not exclusive:
        #Roll in ancestral xml:* attributes
        parent_xml_attrs = root.xpath(u'ancestor::*/@xml:*')
        for attr in parent_xml_attrs:
            aname = (attr.namespaceURI, attr.nodeName)
            if (aname not in added_attributes
                and aname not in root.attributes):
                added_attributes[attr.nodeName] = attr.value
    nsnodes = root.xpath('namespace::*')
    inclusivePrefixes = inclusivePrefixes or []
    if u'#default' in inclusivePrefixes:
        inclusivePrefixes.remove(u'#default')
        inclusivePrefixes.append(u'')
    decls_to_remove = []
    if exclusive:
        used_prefixes = [ node.prefix for node in root.xpath('self::*|@*') ]
        declared_prefixes = []
        for ans, anodename in root.attributes:
            if ans == XMLNS_NAMESPACE:
                attr = root.attributes[ans, anodename]
                prefix = attr.localName
                declared_prefixes.append(prefix)
                #print attr.prefix, attr.localName, attr.nodeName
                if attr.localName not in used_prefixes:
                    decls_to_remove.append(prefix)
        #for prefix in used_prefixes:
        #    if prefix not in declared_prefixes:
        #        nshints[ns.nodeName] = ns.value
    #Roll in ancestral  NS nodes
    for ns in nsnodes:
        prefix = ns.nodeName
        if (ns.value != XML_NAMESPACE
            and (XMLNS_NAMESPACE, ns.nodeName) not in root.attributes
            and (not exclusive or ns.localName in inclusivePrefixes)):
            #added_attributes[(XMLNS_NAMESPACE, ns.nodeName)] = ns.value
            nshints[prefix] = ns.value
        elif (exclusive
              and prefix in used_prefixes
              and prefix not in declared_prefixes):
            nshints[prefix] = ns.value
    visitor = PrintVisitor(stream, 'UTF-8', nshints, False,
                           0, True, added_attributes, decls_to_remove)
    visitor.visit(root)
    return

