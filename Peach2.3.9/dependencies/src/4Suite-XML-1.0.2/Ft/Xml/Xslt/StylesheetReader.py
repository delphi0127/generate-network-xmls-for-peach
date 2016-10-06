########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/StylesheetReader.py,v 1.56 2005/10/29 05:34:25 jkloth Exp $
"""
Classes for the creation of a stylesheet object

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import cStringIO
from xml.dom import Node
from xml.sax import SAXParseException
from xml.sax.handler import property_dom_node

from Ft.Xml import XMLNS_NAMESPACE, Sax, InputSource
from Ft.Xml.Xslt import XsltException, Error, XSL_NAMESPACE
from Ft.Xml.Xslt.StylesheetHandler import StylesheetHandler


# Utility function for fromInstant()
def _change_node(xslt_node, attributes, importIndex=0):
    xslt_node.__dict__.update(attributes)
    xslt_node.importIndex += importIndex
    for child in xslt_node.children or []:
        _change_node(child, attributes, importIndex)
    return


# Whitespace stripping rules for a stylesheet:
#   preserve all whitespace within xsl:text elements;
#   strip whitespace from all other elements
STYLESHEET_WHITESPACE_RULES = [(XSL_NAMESPACE, 'text', False),
                               (None, '*', True)]

class StylesheetReader(StylesheetHandler):
    """
    This class can be used to read, from a variety of sources, a
    stylesheet and all its included and imported stylesheets, building
    from them a single, compact representation of an XSLT stylesheet
    tree (an Ft.Xml.Xslt.Stylesheet.Stylesheet object).

    This is done with the most efficient parsing method available, and
    avoids creating a Domlette document for each document it reads.
    """
    def __init__(self, altBaseUris=None, ownerDocument=None,
                 importIndex=0, globalVars=None, extElements=None,
                 visitedStyUris=None):
        StylesheetHandler.__init__(self, importIndex, globalVars, extElements,
                                   visitedStyUris)
        self._alt_base_uris = altBaseUris or []
        self._ownerDoc = ownerDocument
        return

    def reset(self):
        StylesheetHandler.reset(self)
        self._ownerDoc = None
        self._input_source = None
        return

    def clone(self):
        return self.__class__(self._alt_base_uris, self._ownerDoc,
                              self._import_index, self._global_vars,
                              self._extElements, self._visited_stylesheet_uris)

    def fromInstant(self, instant, baseUri='', is_import=0):
        """
        Read in an "instant" stylesheet (a pickled stylesheet tree) and add
        it to the stylesheet tree.
        """
        root = instant.root
        if baseUri and root.baseUri != baseUri:
            update_attrs = {'baseUri' : baseUri}
        else:
            update_attrs = {}

        if self._ownerDoc:
            # this is an inclusion; change the document and importIndex
            update_attrs['ownerDocument'] = self._ownerDoc
            _change_node(root, update_attrs, self._import_index + (is_import and 1 or 0))
            self._ownerDoc.primeInstructions.extend(root.primeInstructions)
            self._ownerDoc.idleInstructions.extend(root.idleInstructions)
        elif update_attrs:
            _change_node(root, update_attrs)

        # Update the state of the reader
        if not self._ownerDoc:
            self._ownerDoc = root
        self._import_index = root.stylesheet.importIndex

        return root.stylesheet

    def fromDocument(self, document, baseUri='', factory=None):
        """
        Read in a stylesheet source document from a Domlette and add it to
        the stylesheet tree. If a document with the same URI has already been
        read, the cached version will be used instead (so duplicate imports,
        includes, or stylesheet appends do not result in multiple reads).
        """
        if not baseUri:
            if hasattr(document, 'documentURI'):
                baseUri = document.documentURI
            elif hasattr(document, 'baseURI'):
                baseUri = document.baseURI
            else:
                raise TypeError('baseUri required')

        if factory is None:
            factory = InputSource.DefaultFactory

        # check cache
        if self._ownerDoc is not None:
            # We prefer to use an already-parsed doc, as it has had its
            # external entities and XIncludes resolved already
            if uri in self._ownerDoc.sourceNodes:
                document = self._ownerDoc.sourceNodes[baseUri]
            # It's OK to use cached string content, but we have no idea
            # whether we're using the same InputSource class as was used to
            # parse it the first time, and we don't cache external entities
            # or XIncludes, so there is the possibility of those things
            # being resolved differently this time around. Oh well.
            elif uri in self._ownerDoc.sources:
                content = self._ownerDoc.sources[baseUri]
                isrc = factory.fromString(content, baseUri)
                # temporarily uncache it so fromSrc will process it;
                # fromSrc will add it back to the cache when finished
                del self._ownerDoc.sources[baseUri]
                return self.fromSrc(isrc)

        isrc = factory.fromStream(None, baseUri)
        features = []
        properties = [(property_dom_node, document)]
        stylesheet = self._parseSrc(isrc, features, properties)

        # Cache for XSLT document() function
        self._ownerDoc.sourceNodes[baseUri] = document

        return stylesheet


    def fromSrc(self, isrc, extElements=None):
        """
        Read in a stylesheet source document from an InputSource and add it to
        the stylesheet tree. If a document with the same URI has already been
        read, the cached version will be used instead (so duplicate imports,
        includes, or stylesheet appends do not result in multiple reads).
        """
        uri = isrc.uri

        #Check cache
        content = ''
        if self._ownerDoc is not None:
            # We prefer to use an already-parsed doc, as it has had its
            # external entities and XIncludes resolved already
            if uri in self._ownerDoc.sourceNodes:
                doc = self._ownerDoc.sourceNodes[uri]
                # temporarily uncache it so fromDocument will process it;
                # fromDocument will add it back to the cache when finished
                del self._ownerDoc.sourceNodes[uri]
                return self.fromDocument(doc, baseUri=uri, isf=isrc.factory)
            # It's OK to use cached string content, but we have no idea
            # whether we're using the same InputSource class as was used to
            # parse it the first time, and we don't cache external entities
            # or XIncludes, so there is the possibility of those things
            # being resolved differently this time around. Oh well.
            elif uri in self._ownerDoc.sources:
                content = self._ownerDoc.sources[uri]
                isrc = isrc.factory.fromString(content, uri)

        if not content:
            content = isrc.stream.read()
            isrc = isrc.clone(cStringIO.StringIO(content))

        # Add any extension elements, if given
        if extElements is not None:
            self._extElements.update(extElements)

        features = [(Sax.FEATURE_PROCESS_XINCLUDES, isrc.processIncludes)]
        properties = []
        stylesheet = self._parseSrc(isrc, features, properties)
        
        # Cache the string content for subsequent uses
        # e.g., xsl:import/xsl:include and document()
        self._ownerDoc.sources[uri] = content

        return stylesheet

    def _parseSrc(self, isrc, features, properties):
        self._input_source = isrc

        parser = Sax.CreateParser()
        parser.setContentHandler(self)
        for featurename, value in features:
            parser.setFeature(featurename, value)

        # Always set whitespace rules property
        parser.setProperty(Sax.PROPERTY_WHITESPACE_RULES,
                           STYLESHEET_WHITESPACE_RULES)
        for propertyname, value in properties:
            parser.setProperty(propertyname, value)

        try:
            parser.parse(isrc)
        except SAXParseException, e:
            e = e.getException() or e
            if isinstance(e, XsltException):
                raise e
            raise XsltException(Error.STYLESHEET_PARSE_ERROR, isrc.uri, e)
        
        self._input_source = None
        
        root = self._state_stack[0].node
        if root is self._ownerDoc:
            # the top-most stylesheet
            root.stylesheet.setup()

        return root.stylesheet
