########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Lib/Iri.py,v 1.4.4.1 2006/08/23 06:46:34 jkloth Exp $
"""
Classes and functions related to IRI processing

Copyright 2004 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import sys

def IriToUri(iri, convertHost=False):
    r"""
    Converts an IRI or IRI reference to a URI or URI reference,
    implementing sec. 3.1 of draft-duerst-iri-10.

    The convertHost flag indicates whether to perform conversion of
    the ireg-name (host) component of the IRI to an RFC 2396-compatible
    URI reg-name (IDNA encoded), e.g.
    IriToUri(u'http://r\xe9sum\xe9.example.org/', convertHost=False)
    => u'http://r%C3%A9sum%C3%A9.example.org/'
    IriToUri(u'http://r\xe9sum\xe9.example.org/', convertHost=True)
    => u'http://xn--rsum-bpad.example.org/'

    Ordinarily, the IRI should be given as a unicode string. If the IRI
    is instead given as a byte string, then it will be assumed to be
    UTF-8 encoded, will be decoded accordingly, and as per the
    requirements of the conversion algorithm, will NOT be normalized.
    """
    if not isinstance(iri, str):
        iri = NfcNormalize(iri)

    if convertHost and sys.version_info[0:2] >= (2,3):
        # first we have to get the host
        from Ft.Lib.Uri import SplitUriRef, UnsplitUriRef
        (scheme, auth, path, query, frag) = SplitUriRef(iri)
        if auth and auth.find('@') > -1:
            userinfo, hostport = auth.split('@')
        else:
            userinfo = None
            hostport = auth
        if hostport and hostport.find(':') > -1:
            host, port = hostport.split(':')
        else:
            host = hostport
            port = None
        if host:
            host = ConvertIregName(host)
            auth = ''
            if userinfo:
                auth += userinfo + '@'
            auth += host
            if port:
                auth += ':' + port
        iri = UnsplitUriRef((scheme, auth, path, query, frag))

    res = u''
    pos = 0
    surrogate = None
    for c in iri:
        cp = ord(c)
        if cp > 128:
            if cp < 160:
                # FIXME: i18n
                raise ValueError("Illegal character at position %d (0-based) of IRI %r" % (pos, iri))
            # 'for c in iri' may give us surrogate pairs
            elif cp > 55295:
                if cp < 56320:
                    # d800-dbff
                    surrogate = c
                    continue
                elif cp < 57344:
                    # dc00-dfff
                    if surrogate is None:
                        raise ValueError("Illegal surrogate pair in %r" % iri)
                    c = surrogate + c
                else:
                    raise ValueError("Illegal surrogate pair in %r" % iri)
                surrogate = None
            for octet in c.encode('utf-8'):
                res += u'%%%02X' % ord(octet)
        else:
            res += c
        pos += 1
    return res


def NfcNormalize(iri):
    """
    On Python 2.3 and higher, normalizes the given unicode string
    according to Unicode Normalization Form C (NFC), so that it can
    be used as an IRI or IRI reference.
    """
    try:
        from unicodedata import normalize
        iri = normalize('NFC', iri)
    except ImportError:
        pass
    return iri


def ConvertIregName(iregname):
    """
    On Python 2.3 and higher, converts the given ireg-name component
    of an IRI to a string suitable for use as a URI reg-name in pre-
    rfc2396bis schemes and resolvers. Returns the ireg-name
    unmodified on Python 2.2.
    """
    try:
        # I have not yet verified that the default IDNA encoding
        # matches the algorithm required by the IRI spec, but it
        # does work on the one simple example in the spec.
        iregname = iregname.encode('idna')
    except:
        pass
    return iregname
