########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XLink/XLinkElements.py,v 1.9 2005/09/14 21:38:44 jkloth Exp $
"""
Classes representing XLink elements

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from xml.dom import Node

from Ft.Xml import Domlette
from Ft.Xml.XLink import XLINK_NAMESPACE


def Create(node, baseUri):
    """
    Given an XLink element node, returns an object (one of the classes
    defined in this module) that contains the node, its principal XLink
    attribute values, and a 'process' method that can be invoked in order
    to process (follow or otherwise act upon) the element.

    Used by the Ft.Xml.XLink.Processor.Processor.
    """
    elemType = node.getAttributeNS(XLINK_NAMESPACE, u'type')
    return TypeMap.get(elemType, Literal)(node, baseUri)


class Literal:
    """
    Base class for an XLink element.
    """
    type = None

    def __init__(self, node, iSrc):
        self.resource = node
        self.input_source = iSrc

    def process(self):
        return


class Simple(Literal):
    """
    A 'simple'-type XLink element.
    """

    type = "simple"

    def __init__(self, node, iSrc):
        Literal.__init__(self, node, iSrc)
        self.href = node.getAttributeNS(XLINK_NAMESPACE, u'href')
        self.role = node.getAttributeNS(XLINK_NAMESPACE, u'role')
        self.arcrole = node.getAttributeNS(XLINK_NAMESPACE, u'arcrole')
        self.title = node.getAttributeNS(XLINK_NAMESPACE, u'title')
        self.show = node.getAttributeNS(XLINK_NAMESPACE, u'show')
        self.actuate = node.getAttributeNS(XLINK_NAMESPACE, u'actuate')
        self.attributes = filter(lambda x: x.namespaceURI != XLINK_NAMESPACE,
                                 node.attributes.values())

    def process(self):
        """
        Processes a simple XLink element according to the following
        guidelines:

        If xlink:actuate='onLoad' and xlink:show='replace', then the remote
        resource's document element's content (not the document element itself)
        and the content of the XLink element (if any) will together replace the
        XLink element.

        If xlink:actuate='onLoad' and xlink:show='embed', then the remote
        resource's document element will replace the XLink element.

        Any other XLink attribute combinations are ignored.

        These behaviors constitute a reasonable approximation of the resource
        loading suggestions in XLink 1.0 sec. 5.6.1.
        """
        resource = self.resource
        if self.actuate == "onLoad":
            doc = resource.rootNode
            if self.show == 'replace':
                # 1. parse the remote resource
                # FIXME: support XPointer
                newSrc = self.input_source.resolve(self.href, hint='XLink')
                newDoc = Domlette.NonvalidatingReader.parse(newSrc)
                # 2. copy the XLink element's children and non-XLink attrs
                #    into the parsed remote resource's document element
                #    (but why bother with the attrs if we don't use them?)
                for node in self.attributes:
                    newDoc.documentElement.setAttributeNS(node.namespaceURI,
                                                          node.nodeName,
                                                          node.value)
                for child in resource.childNodes[:]:
                    nChild = doc.importNode(child, True)
                    newDoc.documentElement.appendChild(nChild)

                # 3. copy the parsed remote resource's document element's
                #    children (its original ones plus those from step 2)
                #    and insert them before the XLink element, then remove
                #    the XLink element
                if resource.parentNode is not None:
                    parent = resource.parentNode
                else:
                    parent = doc
                for child in newDoc.documentElement.childNodes[:]:
                    newDoc.documentElement.removeChild(child)
                    child = doc.importNode(child, True)
                    parent.insertBefore(child, resource)
                parent.removeChild(resource)

            elif self.show == 'embed':
                # 1. parse the remote resource
                # FIXME: support XPointer
                newSrc = self.input_source.resolve(self.href, hint='XLink')
                newDoc = Domlette.NonvalidatingReader.parse(newSrc)
                # 2. replace the XLink element with the parsed remote resource's
                #    document element
                child = doc.importNode(newDoc.documentElement, True)
                if resource.parentNode is not None:
                    resource.parentNode.replaceChild(child, resource)
                else:
                    doc.replaceChild(child, resource)


class Extended(Literal):
    type = "extended"

class Locator(Literal):
    type = "locator"

class Arc(Literal):
    type = "arc"

class Resource(Literal):
    type = "resource"

class Title(Literal):
    type = "title"

TypeMap = {
    'simple' : Simple,
    'extended' : Extended,
    'locator' : Locator,
    'arc' : Arc,
    'resource' : Resource,
    'title' : Title,
    }

