########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/Regex.py,v 1.1 2005/01/27 04:47:36 uogbuji Exp $
"""
Tools to manage the many different flavors of regex

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import re

#e.g. u"(foo){5,}" -> u"(foo){5}(foo)*"
MIN_LENGTH_SEQ_PAT = re.compile(u"(\\(.+\\))\\{([0-9]+),\\}")


def W3cRegexToPyRegex(w3cregex):
    """
    Convert W3C regex to Python regex
    e.g.:
    >>> from Ft.Lib.Regex import W3cRegexToPyRegex
    >>> print repr(W3cRegexToPyRegex(u"(foo){5,}"))
    u'((foo)){5}(foo)*'
    """
    #Input format: W3C regex ( http://www.w3.org/TR/xmlschema-2/#dt-regex )
    #Output format: Python regex ( http://docs.python.org/lib/re-syntax.html )
    regex = MIN_LENGTH_SEQ_PAT.subn(lambda m: u"("+m.group(1)+u")"+u"{"+m.group(2)+u"}"+m.group(1)+u"*", w3cregex)[0]
    #FIXME: A lot more work on character classes and the like
    return regex

