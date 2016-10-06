from xml.dom import Node
from Ft.Xml import XML_NAMESPACE, EMPTY_NAMESPACE
from Ft.Xml.Lib.XmlString import IsXmlSpace

def StripElements(node,stripElements,stripState=0):
    if node.nodeType == Node.DOCUMENT_NODE:
        for c in node.childNodes:
            StripElements(c,stripElements,stripState)
    elif node.nodeType == Node.ELEMENT_NODE:

        #See if we need to change the strip state
        if node.getAttributeNS(XML_NAMESPACE, 'space') == 'preserve':
            #Force the state to preserve
            stripState = 0
        elif node.getAttributeNS(XML_NAMESPACE, 'space'):
            #Force to strip
            stripState = 1
        else:
            #See if it is a perserve or strip element
            for (uri, local, strip) in stripElements:
                if (uri, local) in [
                    (node.namespaceURI, node.localName),
                    (EMPTY_NAMESPACE, '*'),
                    (node.namespaceURI, '*')
                    ]:
                    stripState = strip
                    break

        for c in node.childNodes:
            StripElements(c,stripElements,stripState)
    elif node.nodeType == Node.TEXT_NODE:
        if stripState and IsXmlSpace(node.data):
            #Kill'em all
            node.parentNode.removeChild(node)


