########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/__init__.py,v 1.23 2005/03/06 06:39:32 mbrown Exp $
"""
Module providing common utilities for many 4Suite components,
as well as for general use.

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os

from Ft import FtException


class UriException(FtException):
    """
    Exceptions used by the Uri module, and possibly others.
    """

    INVALID_BASE_URI = 100

    #RELATIVE_DOCUMENT_URI = 110
    RELATIVE_BASE_URI = 111
    OPAQUE_BASE_URI = 112

    NON_FILE_URI = 120
    UNIX_REMOTE_HOST_FILE_URI = 121

    RESOURCE_ERROR = 130

    SCHEME_REQUIRED = 200 # for SchemeRegistryResolver
    UNSUPPORTED_SCHEME = 201
    IDNA_UNSUPPORTED = 202

    INVALID_PUBLIC_ID_URN = 300

    UNSUPPORTED_PLATFORM = 1000

    def __init__(self, errorCode, *args, **kwargs):
        import MessageSource
        self.params = args or (kwargs,)
        self.errorCode = errorCode
        messages = MessageSource.URI
        msgargs = args or kwargs
        self.message = messages[errorCode] % msgargs
        Exception.__init__(self, self.message, args)
        return


def Truncate(text, length):
    """
    Returns text truncated to length, with "..." appended if truncation
    was necessary.
    """
    if len(text) > length:
        return text[:length] + '...'
    else:
        return text[:length]


def Wrap(text, width):
    r"""
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).

    See also: Ft.Lib.CommandLine.CommandLineUtil.wrap_text()
    """
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   ' \n'[(len(line)-line.rfind('\n')-1
                         + len(word.split('\n',1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )


def CloseStream(stream, quiet=False):
    """
    Closes a stream, ignoring errors if quiet=True. If the stream is a
    terminal (e.g. sys.stdin, stdout, stderr), does not attempt to close
    the stream.

    Closing terminal streams could interfere with subsequent read or
    write attempts. For example, after calling sys.stdout.close(),
    subsequent writes to stdout will not raise an exception, but may
    also fail to actually write anything to stdout.

    The stream argument can be any Python file-like object with a
    close() method, such as a regular file object or an instance of
    Ft.Xml.InputSource.InputSource (or subclass thereof).
    """
    # get the actual stream
    if hasattr(stream, 'stream'):
        # given stream is probably an InputSource
        raw_stream = stream.stream
    else:
        raw_stream = stream

    # determine if it is a terminal; abort if it is
    if hasattr(raw_stream, 'isatty') and raw_stream.isatty():
        return

    try:
        # if an InputSource, let the InputSource close stream for us
        # since subclasses can override the close method.
        stream.close()
    except:
        if quiet:
            pass
        else:
            raise

    return

