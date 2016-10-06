########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/MessageSource.py,v 1.14 2005/03/06 06:39:32 mbrown Exp $
"""
Messages for Ft.Lib

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft import TranslateMessage as _
from Ft.Lib import UriException

# %r preferred for reporting URIs because the URI refs can be empty
# strings or, if invalid, could contain characters unsafe for the error
# message stream.
#
URI = {
    UriException.INVALID_BASE_URI:
        _("Invalid base URI: %(base)r cannot be used to resolve reference %(ref)r"),
    UriException.RELATIVE_BASE_URI:
        _("Invalid base URI: %(base)r cannot be used to resolve reference %(ref)r;"
          " the base URI must be absolute, not relative."),
    UriException.NON_FILE_URI:
        _("Only a 'file' URI can be converted to an OS-specific path; URI given was %r"),
    UriException.UNIX_REMOTE_HOST_FILE_URI:
        _("A URI containing a remote host name cannot be converted to a path on posix;"
          " URI given was %r"),
    UriException.RESOURCE_ERROR:
        _("Error retrieving resource %(loc)r: %(msg)s"),
    UriException.UNSUPPORTED_PLATFORM:
        _("Platform %r not supported by URI function %s"),
    UriException.SCHEME_REQUIRED:
        _("Scheme-based resolution requires a URI with a scheme; "
          "neither the base URI %(base)r nor the reference %(ref)r have one."),
    UriException.INVALID_PUBLIC_ID_URN:
        _("A public ID cannot be derived from URN %(urn)r"
          " because it does not conform to RFC 3151."),
    UriException.UNSUPPORTED_SCHEME:
        _("The URI scheme %(scheme)s is not supported by resolver %(resolver)s"),
    UriException.IDNA_UNSUPPORTED:
        _("The URI ref %(uri)r cannot be made urllib-safe on this version of Python (IDNA encoding unsupported)."),
    }
