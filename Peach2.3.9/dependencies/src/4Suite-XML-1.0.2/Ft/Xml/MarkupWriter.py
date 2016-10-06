########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/MarkupWriter.py,v 1.6 2005/09/13 22:59:35 uogbuji Exp $
"""
MarkupWriter provides a very friendly interface for generating XML content

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys
from Ft.Xml import XML_NAMESPACE, EMPTY_NAMESPACE, EMPTY_PREFIX, XMLNS_NAMESPACE
#from Ft.Xml import MessageSource

class MarkupWriter(object):
    """
    General-purpose utility class for generating XML (may eventually be
    expanded to produce more output types)

    Sample usage:
    
    from Ft.Xml import MarkupWriter
    writer = MarkupWriter(indent=u"yes")
    writer.startDocument()
    writer.startElement(u'xsa')
    writer.startElement(u'vendor')
    #Element with simple text (#PCDATA) content
    writer.simpleElement(u'name', content=u'Centigrade systems')
    #Note writer.text(content) still works
    writer.simpleElement(u'email', content=u"info@centigrade.bogus")
    writer.endElement(u'vendor')
    #Element with an attribute
    writer.startElement(u'product', attributes={u'id': u"100\u00B0"})
    #Note writer.attribute(name, value, namespace=None) still works
    writer.simpleElement(u'name', content=u"100\u00B0 Server")
    #XML fragment
    writer.xmlFragment('<version>1.0</version><last-release>20030401</last-release>')
    #Empty element
    writer.simpleElement(u'changes')
    writer.endElement(u'product')
    writer.endElement(u'xsa')
    writer.endDocument()

    Note on the difference between 4Suite writers and printers
    Writer  - module that exposes a broad public API for building output
              bit by bit
    Printer - module that simply takes a DOM and creates output from it
              as a whole, within one API invokation
    """
    def __init__(self, stream=sys.stdout, **wargs):
        """
        Convenience factory function for Markup writers (based on
        xsl:output in XSLT)
        """
        from Ft.Xml.Xslt.XmlWriter import XmlWriter
        from Ft.Xml.Xslt.OutputParameters import OutputParameters
        oparams = OutputParameters()
        for arg in wargs:
            setattr(oparams, arg, wargs[arg])
        self.writer = XmlWriter(oparams, stream)
        #self.__doc__ += self.writer.__doc__
        return

    def __getattr__(self, value):
        #Delegate to writer
        #if hasattr(self, value):
        #    return object.self.__dict, value)
        return getattr(self.writer, value)
        
    def startElement(self, tagName, namespace=EMPTY_NAMESPACE, extraNss=None,
                     attributes=None):
        """
        Create a start tag with optional attributes.  Must eventually
        be matched with an endElement call
        
        Note: all "strings" in these parameters must be unicode objects
        tagName - qualified name of the element (must be unicode)
        namespace - optional namespace URI
        attributes - optional dictionary mapping name to unicode value
                    the name can either be a unicode QName or a tuple
                    of (QName, namespace URI)
        extraNss - optional dictionary (defaults to an empty one) that
                   creates additional namespace declarations that the
                   user wants to place on the specific element. Each key
                   is a ns prefix, and each value a ns name (URI).
                   You do not need to use extraNss if you will be using
                   a similar namespace parameter.  In fact, most people
                   will never need this parameter.
        """
        if tagName.startswith('xml:'):
            #We can use such a raw test because of the very special case
            #nature of the XML prefix
            namespace = XML_NAMESPACE
        if namespace == EMPTY_NAMESPACE and u':' in tagName:
            #If they supplied a prefix, but not a namespace, complain
            #raise MarkupWriterException(MarkupWriterException.ELEM_PREFIX_WITHOUT_NAMESPACE)
            raise TypeError("Prefixed name %s specified without namespace.  Namespace should be provided in the second parameter."%(tagName))
        self.writer.startElement(tagName, namespace, extraNss)
        if attributes is not None:
            for name in attributes:
                if isinstance(name, tuple):
                    qname, namespace = name
                    value = attributes[name]
                    self.writer.attribute(qname, value, namespace)
                else:
                    if u':' in tagName:
                        #If they supplied a prefix, but not a namespace, complain
                        raise TypeError("Prefixed name %s specified without namespace.  Namespace should be provided by using the attribute name form (<qualified-name>, <namespace>)."%(name))
                    value = attributes[name]
                    self.writer.attribute(name, value)
        return

    def simpleElement(self, tagName, namespace=EMPTY_NAMESPACE, extraNss=None,
                      attributes=None, content=u""):
        """
        Create a simple tag with optional attributes and content.  The
        complete element, start tag, optional text content, end tag, will
        all be generated by this one call.  Must *not* be matched with
        an endElement call.

        Note: all "strings" in these parameters must be unicode objects
        tagName - qualified name of the element
        namespace - optional namespace URI
        attributes - optional dictionary mapping name to unicode value
                    the name can either be a unicode QName or a tuple
                    of (QName, namespace URI)
        content   - optional unicode object with the text body of the
                    simple element
        extraNss - optional dictionary (defaults to an empty one) that
                   creates additional namespace declarations that the
                   user wants to place on the specific element. Each key
                   is a ns prefix, and each value a ns name (URI).
                   You do not need to use extraNss if you will be using
                   a similar namespace parameter.  In fact, most people
                   will never need this parameter.
        """
        if tagName.startswith('xml:'):
            #We can use such a raw test because of the very special case
            #nature of the XML prefix
            namespace = XML_NAMESPACE
        self.startElement(tagName, namespace, extraNss, attributes)
        if content:
            self.writer.text(content)
        self.writer.endElement(tagName, namespace)
        return

    def xmlFragment(self, fragment):
        """
        Incorporate a well-formed general entity into the output.
        fragment of
        fragment - string (must not be a Unicode object) to be incorporated
                   verbatim into the output, after testing for wellp-formedness
        """
        from Ft.Xml.Domlette import EntityReader
        #Essentially just a WF test.
        #We don't actually use the resulting docfrag
        docfrag = EntityReader.parseString(
            fragment, 'urn:bogus:Ft.Xml.Xslt.MarkupWriter.xmlFragment')
        self.writer._stream.write(fragment)
        return


## from Ft import FtException
## class MarkupWriterException(FtException):
##     """
##     Exception class for errors specific to MarkupWriter
##     """
##     ELEM_PREFIX_WITHOUT_NAMESPACE = 100
##     ATTR_PREFIX_WITHOUT_NAMESPACE = 100

##     def __init__(self, errorCode, *args):
##         FtException.__init__(self, errorCode, MessageSource.MARKUPWRITER, args)
##         return


