########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/__init__.py,v 1.39.2.1 2006-08-23 14:41:32 uogbuji Exp $
"""
4XSLT initialization and XSLT pattern tools

These are the most common steps for using this XSLT engine:

  1. Create an Ft.Xml.Xslt.Processor.Processor instance:

     from Ft.Xml.Xslt import Processor
     processor = Processor.Processor()

  2. Prepare Ft.Xml.InputSource instances (via their factory)
     for the source XML and for the stylesheet.

  3. Call the Processor's appendStylesheet() method, passing it
     the stylesheet's InputSource.

  4. Call the Processor's run() method, passing it the source
     document's InputSource.

You can call run() multiple times on different InputSources. When you're
done, the processor's reset() method can be used to restore a clean slate
(at which point you would have to append stylesheets to the processor
again), but in most circumstances it is actually less expensive to just
create a new Processor instance.

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

# the order of imports here is very important

XSL_NAMESPACE = u'http://www.w3.org/1999/XSL/Transform'

import MessageSource
Error = MessageSource.Error

# -- XSLT exceptions -------------------------------------------------

from Ft import FtException
class XsltException(FtException):
    def __init__(self, errorCode, *args):
        FtException.__init__(self, errorCode,
                             MessageSource.g_errorMessages, args)
        return

class XsltParserException(XsltException):
    """
    The exception raised when an error is encountered during the parsing
    of a stylesheet.  This eliminates the need for location information
    within each error message.
    """
    def __init__(self, code, locator, *args):
        XsltException.__init__(self, code, *args)

        # Add location information to the message
        msg = MessageSource.POSITION_INFO % (locator.getSystemId(),
                                             locator.getLineNumber(),
                                             locator.getColumnNumber(),
                                             self.message)
        self.message = msg
        return

class XsltRuntimeException(XsltException):
    def __init__(self, code, xsltelement, *args):
        XsltException.__init__(self, code, *args)

        # Add location information to the message
        baseUri = xsltelement.baseUri or '?'
        line = xsltelement.lineNumber or '?'
        col = xsltelement.columnNumber or '?'
        msg = MessageSource.POSITION_INFO % (baseUri, line, col, self.message)
        self.message = msg
        return


# -- element classifications -----------------------------------------

class CategoryTypes:
    """Collection of constants making up the categories of XSLT element"""
    INSTRUCTION = 0
    TOP_LEVEL_ELEMENT = 1
    RESULT_ELEMENT = 2

import XPatternParserc as XPatternParser
parser = XPatternParser

# -- XPattern API ----------------------------------------------------

from xml.dom import Node
class PatternList:
    """
    PatternList is a class that is useful for people writing code to
    process XSLT patterns, especially in groups.
    """
    PARSER = parser.new()
    def __init__(self, patterns, namespaces=None):
        """
        patterns - A list of strings that make up either compiled pattern
                   objects or valid XSLT patterns in string form.
                   It must be either all of one form or all of another
        namespaces - A namespace dictionary - { prefix: uri, ... } -
                     to be used for setting up expressions in the pattern
        """
        self.namespaces = namespaces or {}
        if hasattr(patterns[0], "match"):
            self._patterns = patterns
        else:
            self._patterns = [ self.PARSER.parse(p) for p in patterns ]
        self._shortcuts = [ p.getShortcuts(self.namespaces) for p in self._patterns ]
        self._lookup_table = {}
        self._patternMapping = {}
        i = 0
        for shortcut_list in self._shortcuts:
            for ((subpattern, axis_type), (node_type, expanded_name)) in shortcut_list:
                self._patternMapping[subpattern] = self._patterns[i]
                if node_type == Node.ELEMENT_NODE:
                    if not self._lookup_table.has_key(node_type):
                        self._lookup_table[node_type] = {}
                    if not self._lookup_table[node_type].has_key(expanded_name):
                        self._lookup_table[node_type][expanded_name] = []
                    self._lookup_table[node_type][expanded_name].append((subpattern, axis_type, self._patterns[i]))
                else:
                    if not self._lookup_table.has_key(node_type):
                        self._lookup_table[node_type] = []
                    self._lookup_table[node_type].append((subpattern, axis_type, self._patterns[i]))
            i = i + 1
        self.length = len(self._patterns)
        return

    #def matchAll(nodes):
    #    """Returns the subset of given nodes that match all patterns"""
    #    return [ n for n in nodes if [ ]
    #        ]

    def lookup(self, node, context=None):
        """Return the patterns that match the node (as a list)"""
        if node.nodeType == Node.ELEMENT_NODE:
            #lookup result is a dict for elements
            narrowed_namecheck = self._lookup_table.get(Node.ELEMENT_NODE, {})
            narrowed = narrowed_namecheck.get((node.namespaceURI, node.localName), [])
            #lookup of (ns,local) None is for the element wildcard case '*'
            narrowed.extend(narrowed_namecheck.get(None, []))
        else:
            #lookup result is a list  for non-elements
            narrowed = self._lookup_table.get(node.nodeType, [])
        if node.nodeType not in [ Node.DOCUMENT_NODE, Node.ATTRIBUTE_NODE ]:
            #lookup of nodeType None is for the wildcard case 'node()'
            narrowed.extend(self._lookup_table.get(None, []))
        if not narrowed: return []
        if not context:
            from Ft.Xml.XPath.Context import Context
            context = Context(node.ownerDocument, 1, 1, processorNss=self.namespaces)
        return [ p[2] for p in narrowed if p[0].match(context, node, p[1]) ]

    def lookupAsSet(self, node, context=None):
        """Returns the patterns that match the node (as a set [dictionary])"""
        if node.nodeType == Node.ELEMENT_NODE:
            #lookup result is a dict for elements
            narrowed_namecheck = self._lookup_table.get(Node.ELEMENT_NODE, {})
            narrowed = narrowed_namecheck.get((node.namespaceURI, node.localName), [])
            #lookup of (ns,local) None is for the element wildcard case '*'
            narrowed.extend(narrowed_namecheck.get(None, []))
        else:
            #lookup result is a list  for non-elements
            narrowed = self._lookup_table.get(node.nodeType, [])
        if node.nodeType not in [ Node.DOCUMENT_NODE, Node.ATTRIBUTE_NODE ]:
            #lookup of nodeType None is for the wildcard case 'node()'
            narrowed.extend(self._lookup_table.get(None, []))
        if not narrowed: return {}
        matched_patterns = {}
        if not context: context = Context(node.ownerDocument, 1, 1)
        for p in narrowed:
            if p[0].match(context, node, p[1]):
                matched_patterns[p[2]] = None
        return matched_patterns

    def xsltKeyPrep(self, context, node):
        """
        A special utility used for XSLT key preparation.
        A list of lists is returned.  The outer list corresponds
        to the patterns.  Each inner list is either [node] or []
        depending on whether or not the node matched the corresponding
        pattern.
        """
        matching_patterns = self.lookupAsSet(node, context)
        return [ [node]*matching_patterns.has_key(p) for p in self._patterns ]
        #return [ [node]*(s[1][0] == node.nodeType and (s[1][0] != Node.ELEMENT_NODE or s[1][1] == (node.namespaceURI, node.localName)) and s[0][0].match(context, node)) for s in self._shortcuts ]

# -- Convenience API ----------------------------------------------------

import os

def _AttachStylesheetToProcessor(stylesheet, processor):
    from Ft.Lib import Uri, Uuid
    from Ft.Xml import InputSource
    from Ft.Xml.Catalog import IsXml
    if isinstance(stylesheet, InputSource.InputSource):
        processor.appendStylesheet(stylesheet)
    #elif stylesheet.find(XSL_NAMESPACE) > 0 and IsXml(stylesheet):
        #Note: this would break in pathological cases such as a user
        #passing in a stylesheet string with only an XInclude to the actual XSLT
    elif IsXml(stylesheet):
        #Create dummy Uri to use as base
        dummy_uri = 'urn:uuid:'+Uuid.UuidAsString(Uuid.GenerateUuid())
        processor.appendStylesheet(
            InputSource.DefaultFactory.fromString(stylesheet, dummy_uri)
            )
    elif hasattr(stylesheet, 'read'):
        #Create dummy Uri to use as base
        dummy_uri = 'urn:uuid:'+Uuid.UuidAsString(Uuid.GenerateUuid())
        processor.appendStylesheet(
            InputSource.DefaultFactory.fromStream(stylesheet, dummy_uri)
            )
    elif Uri.IsAbsolute(stylesheet): # or not os.path.isfile(stylesheet):
        processor.appendStylesheet(
            InputSource.DefaultFactory.fromUri(stylesheet)
            )
    else:
        processor.appendStylesheet(
            InputSource.DefaultFactory.fromUri(Uri.OsPathToUri(stylesheet))
            )
    return

def Transform(source, stylesheet, params=None, output=None):
    """
    Convenience function for applying an XSLT transform.  Returns
    a string.

    source - XML source document in the form of a a string (not Unicode
             object), file-like object (stream), file path, URI or
             Ft.Xml.InputSource.InputSource instance.  If string or stream
             it must be self-contained  XML (i.e. not requiring access to
             any other resource such as external entities or includes)
    stylesheet - XSLT document in the form of a string, stream, URL,
                 file path or Ft.Xml.InputSource.InputSource instance
    params - optional dictionary of stylesheet parameters, the keys of
             which may be given as unicode objects if they have no namespace,
             or as (uri, localname) tuples if they do.
    output - optional file-like object to which output is written (incrementally, as processed)
    """
    #do the imports within the function: a tad bit less efficient, but
    #avoid circular crap
    from Ft.Xml.Xslt import Processor
    from Ft.Xml import InputSource
    from Ft.Lib import Uri, Uuid
    from Ft.Xml.Lib.XmlString import IsXml

    params = params or {}
    processor = Processor.Processor()
    _AttachStylesheetToProcessor(stylesheet, processor)
    if isinstance(source, InputSource.InputSource):
        pass
    elif hasattr(source, 'read'):
        #Create dummy Uri to use as base
        dummy_uri = 'urn:uuid:'+Uuid.UuidAsString(Uuid.GenerateUuid())
        source = InputSource.DefaultFactory.fromStream(source, dummy_uri)
    elif IsXml(source):
        dummy_uri = 'urn:uuid:'+Uuid.UuidAsString(Uuid.GenerateUuid())
        source = InputSource.DefaultFactory.fromString(source, dummy_uri)
    elif Uri.IsAbsolute(source): # or not os.path.isfile(source):
        source = InputSource.DefaultFactory.fromUri(source)
    else:
        source = InputSource.DefaultFactory.fromUri(Uri.OsPathToUri(source))
    return processor.run(source, topLevelParams=params, outputStream=output)


def TransformPath(source, stylesheet):
    import warnings
    warnings.warn("You are using the deprecated Ft.Xml.Xslt.TransformPath function, Please use Ft.Xml.Xslt.Transform instead", DeprecationWarning, 2)

    return Transform(source, stylesheet)


# this import must come after all the above
from StylesheetTree import XsltElement

