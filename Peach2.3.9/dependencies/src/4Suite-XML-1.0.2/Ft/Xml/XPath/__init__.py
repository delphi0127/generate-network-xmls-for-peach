########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/__init__.py,v 1.29 2005/04/03 04:14:15 jkloth Exp $
"""
4XPath initialization and principal functions

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

# From DOM Level 3 XPath
XPATH_NAMESPACE_NODE = NAMESPACE_NODE = 13

FT_EXT_NAMESPACE = 'http://xmlns.4suite.org/ext'

__all__ = [# global constants:
           'XPATH_NAMESPACE_NODE', 'NAMESPACE_NODE', 'FT_EXT_NAMESPACE',
           # exception classes:
           'XPathException', 'CompiletimeException', 'RuntimeException',
           # XPath expression parser:
           'g_parser', 'parser',
           # XPath context API:
           'Context', #the module; is this necessary to expose?
           # XPath expression processing:
           'Compile', 'Evaluate', 'SimpleEvaluate',
           # DOM preparation for XPath processing:
           'NormalizeNode',
           ]


# -- XPath exceptions --------------------------------------------------------

from Ft import FtException

class XPathException(FtException):
    """
    Base class for exceptions specific to XPath processing
    """
    def __init__(self, errorCode, messages, args):
        FtException.__init__(self, errorCode, messages, args)


class CompiletimeException(XPathException):
    """
    The exception raised when an error is encountered during the
    parsing or compilation of an XPath expression.
    """
    #errorCodes:
    # internal/unexpected errors
    INTERNAL = 1
    # other expression compile-time errors
    SYNTAX = 2

    def __init__(self, errorCode, *args):
        # import here to avoid circularity
        import MessageSource
        XPathException.__init__(self, errorCode,
                                MessageSource.ERROR_COMPILETIME, args)
        return


class RuntimeException(XPathException):
    """
    The exception raised when an error is encountered during the
    parsing or evaluation of an XPath expression.
    """
    #errorCodes:
    # internal/unexpected errors
    INTERNAL = 1
    # other expression evaluation (run-time) errors
    NO_CONTEXT         = 10
    UNDEFINED_VARIABLE = 100
    UNDEFINED_PREFIX   = 101
    UNDEFINED_FUNCTION = 102
    WRONG_ARGUMENTS    = 200
    ARGCOUNT_NONE      = 201
    ARGCOUNT_ATLEAST   = 202
    ARGCOUNT_EXACT     = 203
    ARGCOUNT_ATMOST    = 204

    def __init__(self, errorCode, *args):
        # import here to avoid circularity
        import MessageSource
        XPathException.__init__(self, errorCode,
                                MessageSource.ERROR_RUNTIME, args)
        return


# -- Additional setup --------------------------------------------------------

# This occurs near the end because we want to avoid circular import
# problems when the parser imports the expression token classes.
import XPathParserc as XPathParser
parser = XPathParser

# 2004-09-07 - uogbuji:
#   Name module global properly. Leave "parser" alone for now for
#   backwards-compat. Name "parser" is deprecated.
# 2004-10-15 - jkloth:
#   "parser" is not really a global variable, it is a module alias.  The
#   aliasing appears here instead of in XPathParser.py as that file takes a
#   long time to import and allows the ability of testing both versions by
#   importing each separately.
#   The name was chosen as lowercase to aid in merging with the PyXML codebase.
#   However, the XPath codebase has diverged greatly (Domlette/minidom
#   differences) so a new name is acceptible/appropriate, keeping in mind that
#   this name refers to a module.  I suggest simply "Parser".
g_parser = parser


# -- Core XPath API ----------------------------------------------------------

import Context

from Util import Evaluate, SimpleEvaluate, Compile

#Allow access to the NormalizeNode function
from Util import NormalizeNode

Util.XPathParser = g_parser
Util.Context = Context
