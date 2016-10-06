########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Lib/__init__.py,v 1.8 2006/01/06 00:41:57 jclark Exp $
"""
Module providing XML support utilities (including serialization and tree comparison)

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os
from xml.dom import Node

from Ft.Xml import XML_NAMESPACE
from Ft.Lib import Uri

__all__ = ['Language', 'BaseUri']


def Language(node):
    """
    This function returns the language property of the given instance of
    xml.dom.Node, based on xml:lang attributes present on the node or
    its ancestors. If no xml:lang attribute is present, returns None.

    The language code, if any, is returned as an uppercase string.
    """
    while node:
        if node.nodeType == Node.DOCUMENT_NODE:
            break
        elif hasattr(node, 'hasAttributeNS') and node.hasAttributeNS(XML_NAMESPACE, 'lang'):
            # found an xml:lang
            value = node.getAttributeNS(XML_NAMESPACE, 'lang')
            if value:
                #Remove suffix if there is one (why?)
                #index = value.find('-')
                #if index != -1:
                #    value = value[:index]
                value = value.upper()
            # u'' -> None because XML 1.0 3rd Edition says xml:lang=""
            # undefines the language. RDF/XML Syntax (Revised) agrees.
            return value or None
        else:
            # go on to next ancestor
            node = node.nodeType == Node.ATTRIBUTE_NODE and \
                node.ownerElement or node.parentNode

    # reached a Document node without finding an xml:lang
    return None


def BaseUri(node, fallback=None):
    """
    `BaseUri` is an implementation of the `node.baseURI` attribute that
    should be attached to DOM Level 3 nodes, but which is currently broken
    in 4Suite XML.  Where you would use `node.baseURI` according to DOM
    Level 3, use `BaseUri(node)` (this function) instead.

    `BaseUri` returns the absolute base URI for a given `node` in a Domlette
    tree, or `None` if no such *absolute* base URI exists.

    If `fallback` is specified, then it is used to construct a base URI when
    everything else fails.
    """

    baseUriPart = ''
    xmlBaseAncestorList = node.xpath('ancestor-or-self::*[@xml:base][1]')
    if len(xmlBaseAncestorList) > 0:
        node = xmlBaseAncestorList[0]
        baseUriPart = node.getAttributeNS(XML_NAMESPACE, 'base')

    # If the xml:base in scope for the current node is not absolute, we find
    # the element where that xml:base was declared, then Absolutize our
    # relative xml:base against the base URI of the parent of declaring
    # element, recursively.
    if (not Uri.IsAbsolute(baseUriPart) and node.parentNode is not None):
        baseUriPart = Uri.Absolutize(baseUriPart,
                                     BaseUri(node.parentNode))

    # If we still don't have an absolute base URI, resolve against the
    # document's URI.
    if not Uri.IsAbsolute(baseUriPart):
        if hasattr(node, 'createElementNS'):
          baseUriPart = Uri.Absolutize(baseUriPart,
                                       node.documentURI)
        else:
          baseUriPart = Uri.Absolutize(baseUriPart,
                                       node.ownerDocument.documentURI)
    
    # Next, we try resolving against the fallback base URI, if one has been
    # provided.
    if not Uri.IsAbsolute(baseUriPart) and fallback is not None:
        baseUriPart = Uri.Absolutize(baseUriPart, fallback)

    # And if we *still* don't have an absolute base URI, well, there's not
    # much more we can do.  No biscuit.  Do we want to generate one if we
    # get to this case, instead of returning `None`?
    if not Uri.IsAbsolute(baseUriPart):
        return None
    else:
        return baseUriPart
