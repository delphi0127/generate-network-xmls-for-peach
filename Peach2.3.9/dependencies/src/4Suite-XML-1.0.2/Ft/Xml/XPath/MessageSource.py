########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPath/MessageSource.py,v 1.7 2004/01/26 07:40:20 jkloth Exp $
"""
XPath error codes and messages

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft import TranslateMessage as _

from Ft.Xml.XPath import CompiletimeException, RuntimeException

# messages for expression compile-time errors
ERROR_COMPILETIME = {
    # internal/unexpected errors
    CompiletimeException.INTERNAL: _('There is an internal bug in 4XPath. '
        'Please make a post to the 4Suite mailing list to report this error '
        'message to the developers. Include platform details and info about '
        'how to reproduce the error. Info about the mailing list is at '
        'http://lists.fourthought.com/mailman/listinfo/4suite. '
        'The error code to report is: %s'),
    # other compile-time errors
    CompiletimeException.SYNTAX: _('XPath expression syntax error at line %d, column %d: %s'),
}


# messages for expression evaluation (run-time) errors
ERROR_RUNTIME = {
    # internal/unexpected errors
    RuntimeException.INTERNAL: _('There is an internal bug in 4XPath. '
        'Please make a post to the 4Suite mailing list to report this error '
        'message to the developers. Include platform details and info about '
        'how to reproduce the error. Info about the mailing list is at '
        'http://lists.fourthought.com/mailman/listinfo/4suite. '
        'The error code to report is: %s'),

    # other runtime errors
    RuntimeException.NO_CONTEXT: _('An XPath Context object is required in order to evaluate an expression.'),

    RuntimeException.UNDEFINED_VARIABLE: _('Variable undefined: ("%s", "%s").'),
    RuntimeException.UNDEFINED_PREFIX: _('Undefined namespace prefix: "%s".'),
    RuntimeException.UNDEFINED_FUNCTION: _('Undefined function: "%s".'),

    RuntimeException.WRONG_ARGUMENTS: _('Error in arguments to %s: %s'),
    RuntimeException.ARGCOUNT_NONE : _('%s() takes no arguments (%d given)'),
    RuntimeException.ARGCOUNT_ATLEAST : _('%s() takes at least %d arguments (%d given)'),
    RuntimeException.ARGCOUNT_EXACT : _('%s() takes exactly %d arguments (%d given)'),
    RuntimeException.ARGCOUNT_ATMOST : _('%s() takes at most %d arguments (%d given)'),
}
