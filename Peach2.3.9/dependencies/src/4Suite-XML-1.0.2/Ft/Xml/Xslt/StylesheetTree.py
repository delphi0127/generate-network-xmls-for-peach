########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/StylesheetTree.py,v 1.23 2005/05/11 16:11:05 jkloth Exp $
"""
Node classes for the stylesheet tree

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""
from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Domlette import GetAllNs
from Ft.Xml.Xslt import XSL_NAMESPACE, XsltException, XsltRuntimeException, Error
from Ft.Xml.Xslt import AttributeValueTemplate
from Ft.Xml.Xslt import CategoryTypes
from Ft.Xml.Xslt import ContentInfo

from Ft.Xml.XPath import parser
_xpath_parser = parser
from Ft.Xml.Xslt import parser
_xpattern_parser = parser
del parser

class XsltNode:

    # positional information (for debugger and errors)
    # baseUri also used to set base URI of rtf nodes
    baseUri = ''
    lineNumber = '??'
    columnNumber = '??'
    importIndex = -1

    root = None
    parent = None
    expandedName = (None, None)
    nodeName = None
    children = None
    attributes = None

    # hints for performance
    doesSetup = False
    doesPrime = False
    doesIdle = False

    def isLastChild(self):
        siblings = self.parent.children
        if siblings.index(self) == len(siblings) - 1:
            return 1
        else:
            isLast = 1
            for node in siblings[siblings.index(self)+1:]:
                if not node.isPseudoNode():
                    isLast = 0
                    break
            return isLast

    def setup(self):
        return

    def prime(self, processor, context):
        return

    def idle(self, processor):
        return

    def instantiate(self, context, processor):
        return

    def isPseudoNode(self):
        return False

    def pprint(self, _indent=''):
        print _indent + str(self)
        if self.children:
            _indent += '  '
            for child in self.children:
                child.pprint(_indent)
        return


class XsltRoot(XsltNode):

    content = ContentInfo.Alt(ContentInfo.QName(XSL_NAMESPACE, 'xsl:stylesheet'),
                              ContentInfo.QName(XSL_NAMESPACE, 'xsl:transform'),
                              ContentInfo.ResultElements)

    validator = ContentInfo.Validator(content)

    nodeName = u'#document'

    def __init__(self, baseUri):
        self.root = self
        self.baseUri = baseUri
        # cache of original stylesheet source docs, keyed by URI
        self.sources = {}      # XML strings
        self.sourceNodes = {}  # Domlette documents
        # Regarding the cache:
        #
        # XSLT's document() function requires that the original stylesheet
        # documents be accessible as separate source document trees, but the
        # point of StylesheetReader is to avoid creating a Domlette document
        # for each stylesheet while building a single, compact stylesheet tree
        # (using the classes in this module) via the fastest parsing method
        # available. In order to support document(), we have to make it
        # possible to create, as needed, a Domlette document for each original
        # stylesheet, just in case somewhere in the stylesheet tree a
        # document() call or extension function makes reference to one of
        # those original documents. document('') is the most common case, but
        # not the only one.
        #
        # For now, we cache the original bytes of the document entity in the
        # stylesheet tree's XsltRoot object, and implement document() such
        # that it looks for documents in the Domlette cache in the XsltContext
        # first, then tries the cache we set up here, before falling back on
        # the normal resolver to fetch fresh content. If the doc is found in
        # our cache, then it is parsed and the Domlette is stored in the
        # XsltContext for future access. See XsltFunctions.py.
        #
        # Future optimization ideas:
        #  - After the stylesheet tree is built, look for document() calls
        #    in the XPath expressions, and if they all use single arguments
        #    that are hard-coded URI refs, resolve the refs to absolute form,
        #    and discard any cached docs that aren't in the resulting list.
        #  - Compress the cached strings, and decompress on the fly.
        #
        # FIXME: The cache does not include external entities or XIncludes;
        # they are refetched each time the cached document entity is read.
        # It is rare for a stylesheet to use ext. entities/XIncludes, though.
        self.primeInstructions = []
        self.idleInstructions = []
        self.stylesheet = None
        self.children = []
        return

    def appendChild(self, child):
        # The validator ensures that only one child will be added
        child.parent = self
        self.stylesheet = child
        self.children = [child]
        return

    def __str__(self):
        return "<XsltRoot at 0x%x>" % id(self)


# implements default behaviour for extension elements
class XsltElement(XsltNode):

    category = CategoryTypes.RESULT_ELEMENT
    content = ContentInfo.Template
    validator = ContentInfo.Validator(content)
    legalAttrs = None # this means no error checking or defaulting

    def __init__(self, root, namespaceUri, localName, baseUri):
        self.root = root
        self.baseUri = baseUri
        self.expandedName = (namespaceUri, localName)
        self.children = []
        self.attributes = {}
        self.namespaces = {}
        return

    def insertChild(self, index, child):
        """INTERNAL USE ONLY"""
        self.children.insert(index, child)
        child.parent = self
        if child.doesSetup:
            child.setup()
        return

    def appendChild(self, child):
        """INTERNAL USE ONLY"""
        self.children.append(child)
        child.parent = self
        if child.doesSetup:
            child.setup()
        return

    def parseAVT(self, avt):
        """DEPRECATED: specify an attribute in 'legalAttrs' instead."""
        if avt is None: return None
        try:
            return AttributeValueTemplate.AttributeValueTemplate(avt)
        except SyntaxError, error:
            raise XsltException(Error.INVALID_AVT, avt, self.baseUri,
                                self.lineNumber, self.columnNumber,
                                str(error))
        except XsltException, error:
            raise XsltException(Error.INVALID_AVT, avt, self.baseUri,
                                self.lineNumber, self.columnNumber,
                                error.args[0])

    def parseExpression(self, expression):
        """DEPRECATED: specify an attribute in 'legalAttrs' instead."""
        if expression is None: return None
        p = _xpath_parser.new()
        try:
            return p.parse(expression)
        except SyntaxError, error:
            raise XsltException(Error.INVALID_EXPRESSION, expression,
                                self.baseUri, self.lineNumber,
                                self.columnNumber, str(error))

    def parsePattern(self, pattern):
        """DEPRECATED: specify an attribute in 'legalAttrs' instead."""
        if pattern is None: return None
        p = _xpattern_parser.new()
        try:
            return p.parse(pattern)
        except SyntaxError, error:
            raise XsltException(Error.INVALID_PATTERN, pattern,
                                self.baseUri, self.lineNumber,
                                self.columnNumber, str(error))

    def splitQName(self, qname):
        """DEPRECATED: specify an attribute in 'legalAttrs' instead."""
        if not qname: return None
        index = qname.find(':')
        if index != -1:
            split = (qname[:index], qname[index+1:])
        else:
            split = (None, qname)
        return split

    def expandQName(self, qname, refNode=None):
        """DEPRECATED: specify an attribute in 'legalAttrs' instead."""
        if not qname: return None
        if refNode:
            namespaces = GetAllNs(refNode)
        else:
            namespaces = self.namespaces
        prefix, local = self.splitQName(qname)
        if prefix:
            try:
                expanded = (namespaces[prefix], local)
            except KeyError:
                raise XsltRuntimeException(Error.UNDEFINED_PREFIX,
                                           self, prefix)
        else:
            expanded = (EMPTY_NAMESPACE, local)
        return expanded

    def instantiate(self, context, processor):
        """
        Implements default behavior of instantiating each child in the order
        that they appear in the stylesheet.
        """
        context.processorNss = self.namespaces
        context.currentInstruction = self

        for child in self.children:
            child.instantiate(context, processor)
        return

    def processChildren(self, context, processor):
        """
        Iterates over the children, instantiating them in the order that they
        appear in the stylesheet.
        """
        context.processorNss = self.namespaces
        context.currentInstruction = self

        for child in self.children:
            child.instantiate(context, processor)
        return

    def __str__(self):
        #FIXME: Should this use self.__class__ or sth rather than hardcoding "XsltElement"?
        return ("<XsltElement at 0x%x:"
                " name %r, %d attributes, %d children, precedence %d>") % (
            id(self), self.nodeName, len(self.attributes), len(self.children),
            self.importIndex)


class XsltText(XsltNode):

    nodeName = u'#text'

    def __init__(self, root, baseUri, data):
        self.root = root
        self.baseUri = baseUri
        self.data = data
        return

    def instantiate(self, context, processor):
        processor.writers[-1].text(self.data)
        return

    def __str__(self):
        if len(self.data) > 20:
            data = self.data[:20] + '...'
        else:
            data = self.data
        return "<XsltText at 0x%x: %s>" % (id(self), repr(data))
