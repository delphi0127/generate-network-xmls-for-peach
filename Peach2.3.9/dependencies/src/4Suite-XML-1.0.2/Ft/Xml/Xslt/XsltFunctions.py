########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/XsltFunctions.py,v 1.46 2005/08/02 22:43:01 mbrown Exp $
"""
Standard XSLT functions

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os, cStringIO, traceback
from Ft.Lib import boolean, UriException
from Ft.Lib.Uri import IsAbsolute
from Ft.Xml import __version__, EMPTY_NAMESPACE
from Ft.Xml.Lib import routines
from Ft.Xml.XPath import Conversions, FT_EXT_NAMESPACE
from Ft.Xml.XPath.XPathTypes import NodesetType
from Ft.Xml.Xslt import XsltRuntimeException, Error, XSL_NAMESPACE

# is there no better list of implemented core XSLT elements?
from Ft.Xml.Xslt.StylesheetHandler import _ELEMENT_MAPPING

def Document(context, object, nodeSet=None):
    """
    Implementation of document().

    The XSLT 1.0 document function returns the root node of a single
    XML document or of the union of multiple XML documents. The
    arguments are reduced to a set of URIs that indicate the documents
    to parse.

    The first argument is required and provides a set of URI
    references, each of which may be absolute or relative. If it
    is a node-set, then the URI references are the string-values of
    each node in the set. If the argument is any other kind of
    object, the URI reference is the string-value of object.

    The second argument is optional. If given, it provides a base URI
    for normalizing relative URI references, it must be a node-set,
    and only its first node (in document order) is used. The base URI
    for all relative references is the URI of the entity from which
    the node originated. If the node-set is empty, an exception is
    raised (see XSLT 1.0 erratum E14).

    If the second argument is not given, then the base URI depends on
    whether the first argument is a node-set. If the first argument is
    a node-set, then the base URI for each node in the set is the
    entity from which that node originated. Otherwise, the base URI is
    the URI of the entity containing the node with the document() call
    (this URI is usually that of the stylesheet itself, but could be
    an imported stylesheet or even a parsed general entity).

    Thus,

    document('') typically refers to the stylesheet itself, prior to
    whitespace stripping;

    document('http://somehost/foo.xml') refers to the document at
    that absolute URI;

    document('foo.xml') typically refers to the foo.xml document
    relative to the stylesheet;

    document('http://somehost/foo.xml', $ns) where $ns is a non-empty
    node-set refers to the document at that absolute URI ($ns is
    ignored);

    document('foo.xml', $ns) where $ns is a non-empty node-set refers
    to the foo.xml document relative to the URI of the entity from
    which $ns[1] originated;

    document($ns) where $ns is a non-empty node-set is treated as if
    it were
    document(string($ns[1]),$ns[1])|document(string($ns[2]),$ns[2])
    and so on; and

    document($ns, $ns2) where $ns is a node-set and $ns2 is a
    non-empty node-set is treated as if it were
    document(string($ns[1]),$ns2[1])|document(string($ns[2]),$ns2[1])
    and so on.
    """
    result = []
    sheet = context.processor.stylesheet
    uris = {}

    if nodeSet:
        if not isinstance(nodeSet, NodesetType):
            raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                       context.currentInstruction)
        # error condition if 2nd argument is an empty node-set
        if not nodeSet:
            raise XsltRuntimeException(Error.DOC_FUNC_EMPTY_NODESET,
                           context.currentInstruction)
        try:
            base = getattr(nodeSet[0], 'baseURI')
        except AttributeError:
            raise XsltRuntimeException(
                Error.UNKNOWN_NODE_BASE_URI, context.currentInstruction,
                'first node in second argument to document()')
    else:
        base = context.currentInstruction.baseUri

    # arg1 is not a node-set
    if not isinstance(object, NodesetType):
        ref = Conversions.StringValue(object)
        # check base URI coming from arg 2 only when it's needed
        if IsAbsolute(ref):
            base = ref
        else:
            if not nodeSet:
                base = context.currentInstruction.baseUri
                if not base:
                    raise XsltRuntimeException(Error.UNKNOWN_NODE_BASE_URI,
                                   context.currentInstruction,
                                   'node containing document() call')
        # use resolver's normalize() to make it absolute
        # we need to do this even if the ref is already absolute
        # because we have to verify scheme and accept bases that start with '/'
        uris[context.processor.inputSourceFactory.resolver.normalize(ref, base)] = 1
    # arg1 is a node-set
    else:
        for node in object:
            ref = Conversions.StringValue(node)
            if IsAbsolute(ref):
                base=ref
            else:
                # check base URI coming from arg 2 only when it's needed
                if nodeSet:
                    if not base:
                        raise XsltRuntimeException(Error.UNKNOWN_NODE_BASE_URI,
                                       context.currentInstruction,
                                       'first node in second argument to document()')
                else:
                    base = getattr(node, 'baseURI', None)
                    if not base:
                        raise XsltRuntimeException(Error.UNKNOWN_NODE_BASE_URI,
                                       context.currentInstruction,
                                       'first node in first argument to document()')
            # use resolver's normalize() to make it absolute.
            # we need to do this even if the ref is already absolute
            # because we have to verify scheme and accept bases that start with '/'
            uris[context.processor.inputSourceFactory.resolver.normalize(ref, base)] = 1

    for uri in uris:
        # try to get cached DOM
        if uri in context.documents:
            result += [context.documents[uri]]
        else:
            try:
                # or try to get cached string
                if uri in sheet.root.sources:
                    # Create an input source with the same properties
                    # as the document input source.
                    stream = cStringIO.StringIO(sheet.root.sources[uri])
                    isrc = context.processor._documentInputSource.clone(
                        stream, uri, "XSLT DOCUMENT FUNCTION")
                # otherwise, create a new input source
                else:
                    isrc = context.processor._documentInputSource.resolve(
                        uri, hint="XSLT DOCUMENT FUNCTION")
                doc = context.processor._docReader.parse(isrc)
                context.addDocument(doc, uri)
                result += [doc]
            except UriException:
                tb = cStringIO.StringIO()
                tb.write("Lower-level traceback:\n")
                traceback.print_exc(1000, tb)
                msg = 'Unable to retrieve document: %s\n%s' % (uri, tb.getvalue())
                context.processor.warning(msg)
    return result


def Key(context, qname, keyList):
    """
    Implementation of key().

    The first argument specifies the name of the key. When the second
    argument to the key function is of type node-set, then the result
    is the union of the result of applying the key function to the
    string value of each of the nodes in the argument node-set.
    When the second argument to key is of any other type, the argument
    is converted to a string as if by a call to the string function; it
    returns a node-set containing the nodes in the same document as the
    context node that have a value for the named key equal to this string.
    """
    qname = Conversions.StringValue(qname)
    if not qname:
        raise XsltRuntimeException(Error.INVALID_QNAME_ARGUMENT,
                                   context.currentInstruction, qname)
    split_name = context.expandQName(Conversions.StringValue(qname))
    doc = context.node.rootNode
    try:
        keys_for_context_doc = context.processor.keys[doc]
        requested_key = keys_for_context_doc[split_name]
    except KeyError:
        sheet = context.processor.stylesheet
        sheet.updateKey(doc, split_name, context.processor)
        keys_for_context_doc = context.processor.keys[doc]
        requested_key = keys_for_context_doc[split_name]

    result = []
    if not isinstance(keyList, NodesetType):
        keyList = [keyList]
    for key in keyList:
        key = Conversions.StringValue(key)
        result.extend(requested_key.get(key, []))
    return result


def Current(context):
    """
    Implementation of current().

    Returns a node-set that has the current node as its only member.
    """
    return [context.currentNode]


def UnparsedEntityUri(context, name):
    """
    Implementation of unparsed-entity-uri().

    Returns the URI of the unparsed entity with the specified name in
    the same document as the context node. It returns the empty string
    if there is no such entity.
    """
    name = Conversions.StringValue(name)
    unparsedEntities = getattr(context.node.rootNode, 'unparsedEntities', {})
    return unparsedEntities.get(name, u'')


def GenerateId(context, nodeSet=None):
    """
    Implementation of generate-id().

    Returns a string that uniquely identifies the node in the argument
    node-set that is first in document order. If the argument node-set
    is empty, the empty string is returned. If the argument is omitted,
    it defaults to the context node.
    """
    if nodeSet is not None and type(nodeSet) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    if nodeSet is None:
        # If no argument is given, use the context node
        return u'id%r' % id(context.node)
    elif nodeSet:
        # first node in nodeset in document order
        nodeSet.sort()
        return u'id%r' % id(nodeSet[0])
    else:
        # When the nodeset is empty, return an empty string
        return u''


def SystemProperty(context, qname):
    """
    Implementation of system-property().

    Returns an object representing the value of the system property
    identified by the given QName. If there is no such system property,
    the empty string is returned. Supports the required properties in
    the XSLT namespace: xsl:version, xsl:vendor, and xsl:vendor-url;
    plus the following 4Suite-specific properties:

    FOO in namespace http://xmlns.4suite.org/xslt/env-system-property,
    where FOO is an environment variable; and version, tempdir,
    and platform in the %s namespace.
    """ % FT_EXT_NAMESPACE
    qname = Conversions.StringValue(qname)
    #FIXME: actual test should ensure split_name is a QName
    if not qname:
        raise XsltRuntimeException(Error.INVALID_QNAME_ARGUMENT,
                                   context.currentInstruction, qname)
    (uri, local) = context.expandQName(qname)
    if uri == XSL_NAMESPACE:
        if local == 'version':
            return 1.0
        if local == 'vendor':
            return u"Fourthought Inc."
        if local == 'vendor-url':
            return u"http://4Suite.org"
    elif uri == 'http://xmlns.4suite.org/xslt/env-system-property':
        return unicode(os.environ.get(local, ''))
    elif uri == FT_EXT_NAMESPACE:
        if local == 'version':
            return __version__
        if local == 'tempdir':
            #Returns the directory used by the OS for temporary files
            import tempfile
            return unicode(tempfile.gettempdir())
        if local == 'platform':
            return unicode(sys.platform)
    return u''


def FunctionAvailable(context, qname):
    """
    Implementation of function-available().

    Returns true if and only if the expanded-name represented by the
    given QName is the name of a function in the function library.
    If the expanded-name has a non-null namespace URI, then it refers
    to an extension function; otherwise, it refers to a function
    defined by XPath or XSLT.
    """
    qname = Conversions.StringValue(qname)
    #FIXME: actual test should ensure split_name is a QName
    if not qname:
        return boolean.false
    split_name = context.expandQName(qname)
    if split_name in context.functions:
        return boolean.true
    else:
        return boolean.false


def ElementAvailable(context, qname):
    """
    Implementation of element-available().

    Returns true if and only if the expanded-name represented by the
    given QName is the name of an instruction. If the expanded-name has
    a namespace URI equal to the XSLT namespace URI, then it refers to
    an element defined by XSLT. Otherwise, it refers to an extension
    element. If the expanded-name has a null namespace URI, the
    element-available function will return false.
    """
    qname = Conversions.StringValue(qname)
    #FIXME: actual test should ensure split_name is a QName
    if not qname:
        return boolean.false
    namespaceURI, localName = expandedName = context.expandQName(qname)

    if namespaceURI == XSL_NAMESPACE:
        available = localName in _ELEMENT_MAPPING
    elif namespaceURI == EMPTY_NAMESPACE:
        available = False
    else:
        available = expandedName in context.processor.extElements

    return available and boolean.true or boolean.false


def FormatNumber(context, number, formatString, decimalFormatName=None):
    """
    Implementation of format-number().

    Converts its first argument to a string using the format pattern
    string specified by the second argument and the decimal-format
    named by the third argument (see the xsl:decimal-format element),
    or the default decimal-format, if there is no third argument.

    The format pattern string is in the syntax specified by the JDK 1.1
    DecimalFormat class. The decimal-format name must be a QName. It is
    an error if the stylesheet does not contain a declaration of the
    decimal-format with the specified expanded-name.
    """
    num = Conversions.NumberValue(number)

    format_string = Conversions.StringValue(formatString)

    if decimalFormatName is not None:
        format_name = context.expandQName(decimalFormatName)
    else:
        format_name = None
    try:
        decimal_format = context.stylesheet.decimalFormats[format_name]
    except KeyError:
        raise XsltRuntimeException(Error.UNDEFINED_DECIMAL_FORMAT,
                                   decimalFormatName)

    return routines.FormatNumber(num, format_string, decimal_format)


CoreFunctions = {
    (EMPTY_NAMESPACE, 'document'): Document,
    (EMPTY_NAMESPACE, 'key'): Key,
    (EMPTY_NAMESPACE, 'current'): Current,
    (EMPTY_NAMESPACE, 'generate-id'): GenerateId,
    (EMPTY_NAMESPACE, 'system-property'): SystemProperty,
    (EMPTY_NAMESPACE, 'function-available'): FunctionAvailable,
    (EMPTY_NAMESPACE, 'element-available'): ElementAvailable,
    (EMPTY_NAMESPACE, 'format-number'): FormatNumber,
    (EMPTY_NAMESPACE, 'unparsed-entity-uri'): UnparsedEntityUri,
    }
