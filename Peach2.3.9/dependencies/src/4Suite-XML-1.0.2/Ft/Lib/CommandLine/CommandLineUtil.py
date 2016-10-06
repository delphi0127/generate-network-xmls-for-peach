########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/CommandLine/CommandLineUtil.py,v 1.12 2004/09/07 20:05:27 mbrown Exp $
"""
Utility functions used by command-line scripts

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os, sys

from Ft.Lib import Uri, Wrap

__all__ = ['ArgumentError', 'GetoptError',
           'wrap_text',
           'SourceArgToUri', 'SourceArgToInputSource']


class ArgumentError(Exception):
    pass


class GetoptError(Exception):
    pass


def wrap_text(text, width):
    """
    Split 'text' into multiple lines of no more than 'width' characters
    each, and return the result as a list of strings.

    This function differs from distutils.fancy_getopt.wrap_text() in
    that the distutils version collapses blank lines; this one doesn't.

    See also: Ft.Lib.Wrap()
    """
    return Wrap(text, width).split('\n')


def SourceArgToUri(arg, resolver=Uri.BASIC_RESOLVER):
    """
    Some command-line scripts take an argument that is supposed to be
    either "-" (denoting standard input) or a URI reference that can be
    resolved against the URI equivalent of the current working
    directory. This function processes such an argument, given as a
    string, and returns an appropriate URI.

    Since users tend to expect local OS paths to work as URIs, this
    function will accept and use an OS path argument if does appear to
    point to an existing local file, even though this could interfere
    with catalog-based resolution.

    Raises a ValueError if arg is neither a local file nor a valid URI
    reference nor "-".

    The resolver object must support a normalize() method that
    can resolve a URI reference against a base URI, returning a URI.
    """
    if not isinstance(resolver, Uri.UriResolverBase):
        msg = 'It appears there is a bug in this command-line' \
              ' script. A %s was passed as URI resolver to a function that' \
              ' requires an instance of Ft.Lib.Uri.UriResolverBase (or' \
              ' a subclass thereof).'
        raise TypeError(msg % type(resolver))
    if not isinstance(arg, str) and not isinstance(arg, unicode):
        msg = 'It appears there is a bug in this command-line' \
              ' script. A %s was passed as an argument needing to be' \
              ' converted to a URI. A string must be provided instead.'
        raise TypeError(msg % type(arg))

    if arg == '-':
        return Uri.OsPathToUri('unknown-STDIN', attemptAbsolute=True)
    elif arg:
        if os.path.isfile(arg):
            return Uri.OsPathToUri(arg, attemptAbsolute=True)
        elif not Uri.MatchesUriRefSyntax(arg):
            raise ValueError("'%s' is not a valid URI reference." % arg)
        elif Uri.IsAbsolute(arg):
            return arg

    base = Uri.OsPathToUri(os.getcwd(), attemptAbsolute=True)
    if base[-1] != '/':
        base += '/'
    return resolver.normalize(arg, base)


def SourceArgToInputSource(arg, factory, *v_args, **kw_args):
    """
    Some command-line scripts take an argument that is supposed to be
    either "-" (denoting standard input) or a URI reference that can be
    resolved against the URI equivalent of the current working
    directory. This function processes such an argument, given as a
    string, and returns an appropriate InputSource object.

    Since users tend to expect local OS paths to work as URIs, this
    function will accept and use an OS path argument if does appear to
    point to an existing local file, even though this could interfere
    with catalog-based resolution.

    Raises a ValueError if arg is neither a local file nor a valid URI
    reference nor "-". Raises a UriException if a stream for the
    InputSource could not be opened (e.g., when the URI refers to a
    directory or unreadable file).

    Extra arguments given to this function are passed to the
    InputSourceFactory method that creates the InputSource instance.
    The factory must support the methods fromStream() and fromUri(),
    as defined in Ft.Xml.InputSource.InputSourceFactory. The factory
    must also provide a resolver object with a normalize() method that
    can resolve a URI reference against a base URI, returning a URI.
    """
    # It is important to require the caller to supply the factory,
    # as we are in Ft.Lib, not Ft.Xml, so it is not safe to import
    # Ft.Xml.InputSourceFactory. Also, we want to leave open the
    # possibility that other factories can be used, perhaps to
    # generate an InputSource that is not XML oriented or that is
    # a subclass of Ft.Xml.InputSource.
    if factory is None:
        msg = 'It appears there is a bug in this command-line' \
              ' script. Python\'s "None" type was passed to a' \
              ' function that requires an instance of' \
              ' Ft.Xml.InputSource.InputSourceFactory.'
        raise TypeError(msg)

    sourceUri = SourceArgToUri(arg, factory.resolver)

    if arg == '-':
        v_args = (sys.stdin,) + v_args
        kw_args['uri'] = sourceUri
        isrc = factory.fromStream(*v_args, **kw_args)
    else:
        v_args = (sourceUri,) + v_args
        isrc = factory.fromUri(*v_args, **kw_args)
    return isrc

