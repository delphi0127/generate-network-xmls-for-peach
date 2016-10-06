########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/BuiltInExtFunctions.py,v 1.30 2005/03/18 23:47:19 jkloth Exp $
"""
4XSLT specific extension functions (i.e. ones that create a node set)

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""
# Use this module only for functions that generate new node sets
# or for whatever reason need a processor object (e.g. FtKey needs
# a processor to read the key defs). Place others in
# Ft.Xml.XPath.BuiltInExtFunctions.py

import re

from Ft.Xml.Lib.XmlString import SplitQName
from Ft.Xml.XPath import FT_EXT_NAMESPACE
from Ft.Xml.XPath import Conversions
from Ft.Xml.Xslt import XsltRuntimeException, Error
from Ft.Xml.Xslt.XsltFunctions import Key

__all__ = ['ExtNamespaces', 'ExtFunctions',
           'FtKey',
           'Lookup',
           'Map',
           'DocAsString',
           'SearchRe',
           'SerializeXml',
           'Split',]


def FtKey(context, qname, keyList, realContextNode=None):
    """
    Query an XSLT key, but allow the user to override the context node for
    purposes of determining which source document to check.
    realContextNode is a node set from which the first node is extracted
    And used as the context node
    """
    if realContextNode:
        orig_node = context.node
        context.node = realContextNode[0]
        result = Key(context, qname, keyList)
        context.node = orig_node
    else:
        result = Key(context, qname, keyList)
    return result


def SearchRe(context, pattern, arg=None):
    """Do a regular expression search against the argument (i.e. get all matches)"""
    if not arg:
        arg = context.node
    arg = Conversions.StringValue(arg)
    matches_nodeset = []
    compiled = re.compile(pattern)

    processor = context.processor
    processor.pushResultTree(context.currentInstruction.baseUri)
    try:
        match = compiled.search(arg)
        while match:
            processor.writers[-1].startElement('Match')
            # .groups() return empty tuple when the pattern did not do grouping
            groups = match.groups() or (match.group(),)
            for group in groups:
                processor.writers[-1].startElement('Group')
                group and processor.writers[-1].text(group)
                processor.writers[-1].endElement('Group')
            processor.writers[-1].endElement('Match')
            match = compiled.search(arg, match.end())
    finally:
        rtf = processor.popResult()
    return rtf.childNodes


def Map(context, funcname, *nodesets):
    """
    Apply the function serially over the given node sets.
    In iteration i, the function is passed N parameters
    where N is the number of argument node sets.  Each
    parameter is a node set of size 1, whose node is
    the ith node of the corresponding argument node set.
    The return value is a node set consisting of a series
    of result-tree nodes, each of which is a text node
    whose value is the string value of the result of the
    ith function invocation.
    Warning: this function uses the implied ordering of the node set
    Based on its implementation as a Python list.  But in reality
    There is no reliable ordering of XPath node sets.
    Therefore this function is not recommended for use with
    more than one node set parameter.
    """
    (prefix, local) = SplitQName(funcname)
    uri = context.processorNss.get(prefix)
    if prefix and not uri:
        raise XsltRuntimeException(Error.UNDEFINED_PREFIX,
                                   context.currentInstruction, prefix)
    expanded = (prefix and uri or '', local)
    func = context.functions.get(expanded)
    if not func:
        raise Exception('Dynamically invoked function %s not found.'%funcname)

    flist = [func]*len(nodesets)
    lf = lambda x, f, *args: apply(f, args)
    retlist = apply(map, (lf, flist) + nodesets)

    processor = context.processor
    processor.pushResultTree(context.currentInstruction.baseUri)
    try:
        for ret in retlist:
            processor.writers[-1].text(Conversions.StringValue(ret))
    finally:
        rtf = processor.popResult()
    return rtf.childNodes


def Lookup(context, name, key):
    """
    f:lookup() queries an index as defined by f:create-index.
    """
    name = Conversions.StringValue(name)
    key = Conversions.StringValue(key)
    processor = context.processor
    indices = processor.extensionParams.get((FT_EXT_NAMESPACE, 'indices'), {})
    index = indices.get(name, {})
    value = index.get(key, [])
    return value


def DocAsString(context, obj, encoding='UTF-8'):
    """
    Retrieves a document, similar to the document() function, but
    returns the document as an XPath string object rather than as a
    node-set.

    Security note: if the associated URI resolver allows file: URLs,
    this extension could be used to read arbitrary system files
    """
    sheet = context.processor.stylesheet
    baseUri = context.currentInstruction.baseUri

    if isinstance(obj, list):
        result = u''
        for node in obj:
            result += DocAsString(context,
                                  Conversions.StringValue(node),
                                  encoding)
    else:
        if hasattr(context, 'processor'):
            #In Xslt, use the ISF on the processor to resolve the URI
            isrc = context.processor.inputSourceFactory.fromUri(baseUri)
            isrc = isrc.resolve(Conversions.StringValue(obj),
                                hint="XSLT DOCUMENT FUNCTION")
            data = isrc.read()
            isrc.close()
            return data
        else:
            # the current instruction's base URI should suffice
            uri = Uri.BASIC_RESOLVER.normalize(
                Conversions.StringValue(obj),
                baseUri)
        if obj == u'' and baseUri in sheet.root.sources:
            result = sheet.root.sources[baseUri]
        else:
            resultfile = codecs.open(uri, 'rb', encoding)
            result = resultfile.read()
            resultfile.close()

    return result


def SerializeXml(context, nodeset, method=None,
                 omitxmldecl=1):
    """
    f:serialize-xml() takes a node set and turns it into a string
    representing the serialization of the node set, obtained
    by concatenating the serialization of each node in the
    node set in document order.

    See also: XPath (not XSLT) extension function f:parse-xml()
    """
    from Exslt.Common import NodeSet as _NodeSet
    import cStringIO
    from Ft.Xml import EMPTY_NAMESPACE
    from Ft.Xml.Xslt.CopyOfElement import CopyNode
    nodeset = _NodeSet(context, nodeset)
    result = cStringIO.StringIO()
    processor = context.processor
    op = processor.outputParams.clone()
    method = method or (EMPTY_NAMESPACE, 'xml')
    op.method = method
    op.omitXmlDeclaration = omitxmldecl and "yes" or "no"
    processor.addHandler(op, result)

    for node in nodeset:
        CopyNode(processor, node)
    processor.removeHandler()
    return unicode(result.getvalue(), op.encoding)


def Split(context, arg, delim=u' '):
    """
    DEPRECATED.
    Equivalent to EXSLT's str:split().
    Splits a string according to a sub-string and return a node set
    of elements nodes, each of which is named "Split" and contains the
    split text
    For example f:split('A,B,C,') returns a node set of "Split" nodes
    having text nodes with values "A", "B" and "C"
    arg - converted to a string, is the string to split up
    delim - the delimiter upon which to split, defaults to " "
    """
    arg = Conversions.StringValue(arg)
    delim = Conversions.StringValue(delim)
    context.processor.pushResultTree(context.currentInstruction.baseUri)
    try:
        for text in arg.split(delim):
            context.processor.writers[-1].startElement('Split')
            context.processor.writers[-1].text(text)
            context.processor.writers[-1].endElement('Split')
    finally:
        rtf = context.processor.popResult()
    return rtf.childNodes



ExtNamespaces = {
    FT_EXT_NAMESPACE : 'f',
    }

ExtFunctions = {
    (FT_EXT_NAMESPACE, 'key') : FtKey,
    (FT_EXT_NAMESPACE, 'lookup') : Lookup,
    (FT_EXT_NAMESPACE, 'search-re') : SearchRe,
    (FT_EXT_NAMESPACE, 'map') : Map,
    (FT_EXT_NAMESPACE, 'doc-as-string'): DocAsString,
    (FT_EXT_NAMESPACE, 'serialize-xml') : SerializeXml,
    (FT_EXT_NAMESPACE, 'split'): Split,
    }

