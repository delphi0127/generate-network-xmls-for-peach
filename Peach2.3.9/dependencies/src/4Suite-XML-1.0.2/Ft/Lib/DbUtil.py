########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/DbUtil.py,v 1.5 2005/10/16 20:50:51 jkloth Exp $
"""
Utilities for database connections

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

__all__ = ['EscapeQuotes']

try:
    from EscapeQuotesc import escape as EscapeQuotes
except ImportError:
    def EscapeQuotes(qstr):
        """
        Postgres uses single quotes for string marker, so put a
        backslash before single quotes for insertion into a database.
        Also escape backslashes.
        pre: qstr = string to be escaped
        post: return the string with all single quotes escaped
        """
        if qstr is None:
            return u''
        tmp = qstr.replace("\\","\\\\")
        tmp = tmp.replace("'", "\\'")
        return unicode(tmp)
