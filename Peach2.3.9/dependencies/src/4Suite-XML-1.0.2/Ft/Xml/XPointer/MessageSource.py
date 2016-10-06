########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/XPointer/MessageSource.py,v 1.3 2004/01/26 07:40:21 jkloth Exp $
"""
XPointer error codes and messages

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft import TranslateMessage as _
from Ft.Xml.XPointer import XPtrException

g_errorMessages = {
    XPtrException.INTERNAL_ERROR : _('There is an internal bug in 4Suite. '
        'Please make a post to the 4Suite mailing list to report this error '
        'message to the developers. Include platform details and info about '
        'how to reproduce the error. Info about the mailing list is at '
        'http://lists.fourthought.com/mailman/listinfo/4suite. '
        'The error code to report is: %s'),
    XPtrException.SYNTAX_ERROR : _("Syntax error in XPointer expression: %s"),
    XPtrException.RESOURCE_ERROR : _("Invalid resource, or not well-formed XML: %s"),
    XPtrException.SUB_RESOURCE_ERROR : _("Expression does not locate a resource"),
    }
