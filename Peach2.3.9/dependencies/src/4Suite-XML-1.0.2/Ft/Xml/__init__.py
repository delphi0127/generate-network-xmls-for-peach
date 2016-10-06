########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/__init__.py,v 1.49.4.3 2006/09/18 13:49:48 uogbuji Exp $
"""
Module providing utilities for processing XML files

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__all__ = [# constants
           'EMPTY_NAMESPACE',
           'EMPTY_PREFIX',
           'XML_NAMESPACE',
           'XMLNS_NAMESPACE',
           'XHTML_NAMESPACE',
           'READ_EXTERNAL_DTD',
           'HAS_PYEXPAT',
           # classes
           'ReaderException', 'XIncludeException',
           # functions
           'SplitQName', 'ApplyXUpdate',
           # modules
           'MarkupWriter',
           'Parse',
           'ParsePath',
           ]


EMPTY_NAMESPACE = None
EMPTY_PREFIX = None
XML_NAMESPACE = u"http://www.w3.org/XML/1998/namespace"
XMLNS_NAMESPACE = u"http://www.w3.org/2000/xmlns/"
XHTML_NAMESPACE = u"http://www.w3.org/1999/xhtml"

# Defined here to ensure that all readers operate the same.
READ_EXTERNAL_DTD = True

from Ft import FtException, __version__, TranslateMessage as _

class ReaderException(FtException):
    """
    Exception class for errors specific to XML reading
    (at a level above standard, non-namespace-aware parsing)
    """
    # Fatal errors
    # Note: These are actual Expat error codes redefined here to allow for
    #   translation of the error messages.
    #NO_MEMORY = 1                              # mapped to MemoryError
    SYNTAX_ERROR = 2
    NO_ELEMENTS = 3
    INVALID_TOKEN = 4
    UNCLOSED_TOKEN = 5
    PARTIAL_CHAR = 6
    TAG_MISMATCH = 7
    DUPLICATE_ATTRIBUTE = 8
    JUNK_AFTER_DOCUMENT_ELEMENT = 9
    ILLEGAL_PARAM_ENTITY_REF = 10
    UNDEFINED_ENTITY = 11
    RECURSIVE_ENTITY_REF = 12
    ASYNC_ENTITY = 13
    BAD_CHAR_REF = 14
    BINARY_ENTITY_REF = 15
    ATTRIBUTE_EXTERNAL_ENTITY_REF = 16
    MISPLACED_XML_PI = 17
    UNKNOWN_ENCODING = 18
    INCORRECT_ENCODING = 19
    UNCLOSED_CDATA_SECTION = 20
    EXTERNAL_ENTITY_HANDLING = 21
    NOT_STANDALONE = 22
    #UNEXPECTED_STATE = 23                      # mapped to SystemError
    ENTITY_DECLARED_IN_PE = 24
    #FEATURE_REQUIRES_XML_DTD = 25              # mapped to SystemError
    #CANT_CHANGE_FEATURE_ONCE_PARSING = 26      # mapped to SystemError
    UNBOUND_PREFIX = 27
    UNDECLARED_PREFIX = 28
    INCOMPLETE_PE = 29
    INVALID_XML_DECL = 30
    INVALID_TEXT_DECL = 31
    INVALID_PUBLICID = 32
    #SUSPENDED = 33                             # mapped to SystemError
    #NOT_SUSPENDED = 34                         # mapped to RuntimeError
    #ABORTED = 35                               # mapped to SystemError
    #FINISHED = 36                              # mapped to SystemError
    #SUSPEND_PE = 37                            # mapped to SystemError
    RESERVED_PREFIX_XML = 38
    RESERVED_PREFIX_XMLNS = 39
    RESERVED_NAMESPACE_URI = 40

    # Validity errors
    MISSING_DOCTYPE = 1000
    INVALID_ELEMENT = 1001
    ROOT_ELEMENT_MISMATCH = 1002
    UNDECLARED_ELEMENT = 1003
    INCOMPLETE_ELEMENT = 1004
    INVALID_TEXT = 1005
    UNDECLARED_ATTRIBUTE = 1006
    DUPLICATE_ID = 1007
    UNDECLARED_ENTITY = 1008
    INVALID_ENTITY = 1009
    UNDECLARED_NOTATION = 1010
    MISSING_ATTRIBUTE = 1011
    UNDEFINED_ID = 1012                         # FIXME: implement
    DUPLICATE_ELEMENT_DECL = 1013
    DUPLICATE_ID_DECL = 1014
    ID_ATTRIBUTE_DEFAULT = 1015
    XML_SPACE_DECL = 1016
    XML_SPACE_VALUES = 1017
    INVALID_NAME_VALUE = 1018
    INVALID_NAME_SEQ_VALUE = 1019
    INVALID_NMTOKEN_VALUE = 1020
    INVALID_NMTOKEN_SEQ_VALUE = 1021
    INVALID_ENUM_VALUE = 1022
    ATTRIBUTE_UNDECLARED_NOTATION = 1023
    ENTITY_UNDECLARED_NOTATION = 1024           # FIXME: implement

    # Warnings
    ATTRIBUTES_WITHOUT_ELEMENT = 2000
    ATTRIBUTE_DECLARED = 2001
    ENTITY_DECLARED = 2002

    XML_PARSE_ERROR = 100
    RECURSIVE_PARSE_ERROR = 101

    def __init__(self, errorCode, systemId, lineNumber, columnNumber,
                 **kwords):
        FtException.__init__(self, errorCode, MessageSource.READER, **kwords)
        self.systemId = systemId
        self.lineNumber = lineNumber
        self.columnNumber = columnNumber
        return

    def __str__(self):
        systemId = self.systemId
        if isinstance(systemId, unicode):
            systemId = systemId.encode('unicode_escape')
        return _("In %s, line %s, column %s: %s") % (systemId,
                                                     self.lineNumber,
                                                     self.columnNumber,
                                                     self.message)

class XIncludeException(FtException):
    """
    Exception class for errors specific to XInclude processing
    """
    MISSING_HREF = 10
    INVALID_PARSE_ATTR = 11
    TEXT_XPOINTER = 12
    FRAGMENT_IDENTIFIER = 13
    UNSUPPORTED_XPOINTER = 14
    INCLUDE_IN_INCLUDE = 15
    FALLBACK_NOT_IN_INCLUDE = 16
    MULTIPLE_FALLBACKS = 17

    def __init__(self, errorCode, *args):
        FtException.__init__(self, errorCode, MessageSource.XINCLUDE, args)

import MessageSource

from Ft.Xml.Lib.XmlString import SplitQName


#Wrap this so that we can import it later
def ApplyXUpdate(*args, **kw_args):
    import Ft.Xml.XUpdate
    return XUpdate.ApplyXUpdate(*args, **kw_args)

#Good ol' backward compatibility for creative spellings
def ApplyXupdate(*args, **kw_args):
    import Ft.Xml.XUpdate
    return XUpdate.ApplyXupdate(*args, **kw_args)


from distutils import version
pyxml_required = version.StrictVersion('0.8.0')
def CheckVersion(feature=None):
    """
    PyXML is required by some features of 4Suite (e.g., validating parsing,
    and 4XSLT's SaxWriter). This is a common function to test whether a
    correct version of PyXML is installed. It raises a SystemExit if the
    test result is negative, and returns None otherwise.

    The feature argument is a string indicating which feature in 4Suite
    requires PyXML. It is output as part of the SystemExit message.
    """
    try:
        import _xmlplus
        xml_version = version.StrictVersion(_xmlplus.__version__)
    except:
        xml_version = version.StrictVersion('0.0.0')

    if xml_version < pyxml_required:
        import sys
        if not feature:
            feature = "this feature"
        print """
        PyXML v%s is required for %s in 4Suite.
        It is available at http://sourceforge.net/projects/pyxml.
        """ % (str(pyxml_required), feature)
        sys.exit(1)

HAS_PYEXPAT = True
try:
    from xml.parsers import expat
    expat.ParserCreate
    del expat
except (ImportError, AttributeError):
    HAS_PYEXPAT = False

from MarkupWriter import MarkupWriter

# Convenience functions for parsing, etc.
import os

def CreateInputSource(obj, uri=None):
    """
    Convenience function for creating an InputSource.
    obj - a string, Unicode object (only if you really know what you're doing),
          file-like object (stream), file path or URI.  You can also pass an
          InputSource object, in which case the return value is just the same
          object, possibly with the URI modified
    uri - optional override URI.  The base URI for the IS will be set to this
          value

    Returns an InputSource which can be passed to 4Suite APIs.
    """
    #do the imports within the function: a tad bit less efficient, but
    #avoid circular crap
    from Ft.Xml import InputSource
    factory = InputSource.DefaultFactory
    from Ft.Lib import Uri, Uuid
    from Ft.Xml.Lib.XmlString import IsXml

    if isinstance(obj, InputSource.InputSource):
        isrc = obj
    elif hasattr(obj, 'read'):
        #Create dummy Uri to use as base
        dummy_uri = 'urn:uuid:'+Uuid.UuidAsString(Uuid.GenerateUuid())
        isrc = factory.fromStream(obj, dummy_uri)
    elif IsXml(obj):
        dummy_uri = 'urn:uuid:'+Uuid.UuidAsString(Uuid.GenerateUuid())
        isrc = factory.fromString(obj, dummy_uri)
    elif Uri.IsAbsolute(obj): #or not os.path.isfile(obj):
        isrc =  factory.fromUri(obj)
    else:
        isrc = factory.fromUri(Uri.OsPathToUri(obj))
    if uri: isrc.uri = uri
    return isrc


def Parse(source):
    """
    Convenience function for parsing XML.  Use this function with a single
    argument, which must either be a string (not Unicode object), file-like
    object (stream), file path or URI.

    Returns a Domlette node.

    Only pass strings or streams to this function if the XML is self-contained
    XML (i.e. not requiring access to any other resource such as external
    entities or includes).  If you get URI resolution errors, do not use this
    function: use the lower-level APIs instead.  As an example, if you want
    such resolution to use the current working directory as a base, parse
    as follows for strings:

    from Ft.Xml.Domlette import NonvalidatingReader
    from Ft.Lib import Uri

    XML = "<!DOCTYPE a [ <!ENTITY b "b.xml"> ]><a>&b;</a>"

    base = Uri.OsPathToUri('')  #Turn CWD into a file: URL
    doc = NonvalidatingReader.parseString(XML, base)
    # during parsing, the replacement text for &b;
    # will be obtained from b.xml in the CWD

    For streams, use "parseStream" rather than "parseString" in the above.
    """
    #do the imports within the function: a tad bit less efficient, but
    #avoid circular crap
    from Ft.Xml.Domlette import NonvalidatingReader
    from Ft.Lib import Uri, Uuid
    from Ft.Xml.Lib.XmlString import IsXml

    if hasattr(source, 'read'):
        #Create dummy Uri to use as base
        dummy_uri = 'urn:uuid:'+Uuid.UuidAsString(Uuid.GenerateUuid())
        return NonvalidatingReader.parseStream(source, dummy_uri)
    elif IsXml(source):
        dummy_uri = 'urn:uuid:'+Uuid.UuidAsString(Uuid.GenerateUuid())
        return NonvalidatingReader.parseString(source, dummy_uri)
    elif Uri.IsAbsolute(source): #or not os.path.isfile(source):
        return NonvalidatingReader.parseUri(source)
    else:
        return NonvalidatingReader.parseUri(Uri.OsPathToUri(source))


def ParsePath(source):
    import warnings
    warnings.warn("You are using the deprecated Ft.Xml.ParsePath function, Please use Ft.Xml.Parse instead", DeprecationWarning, 2)

    return Parse(source)


