########################################################################
# $Source: /var/local/cvsroot/4Suite/Ft/Xml/Catalog.py,v $ $Revision: 1.38 $ $Date: 2006/08/12 15:56:22 $
"""
Classes and functions that help implement OASIS XML and TR9401 Catalogs.
Resolution with Catalogs is handled via the Ft.Xml.InputSource module.

Based on a contribution to PyXML from Tarn Weisner Burton
<twburton@users.sf.net>. See
http://sourceforge.net/tracker/index.php?func=detail&aid=490069&group_id=6473&atid=306473

Copyright 2005 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os, re, sys, warnings, cStringIO
from xml.sax import xmlreader

from Ft import FtWarning, GetConfigVar
from Ft.Lib import Uri, UriException, ImportUtil
from Ft.Xml import XML_NAMESPACE
from Ft.Xml.Lib.XmlString import IsXml

__all__ = ['Catalog', 'GetDefaultCatalog']

TR9401 = re.compile(r'^\s*(BASE|CATALOG|DELEGATE|PUBLIC|SYSTEM|OVERRIDE\s+YES|OVERRIDE\s+NO)\s+"((?:[^"\\]|\\.)*)"(?:\s+"((?:[^"\\]|\\.)*)")?', re.M | re.I)


_urn_hex_re = re.compile('%(..)')
_urn_trans_re = re.compile('[+:;]')
_urn_trans_map = {'+' : ' ',
                  ';' : '//',
                  ':' : '::',
                  }

def UnwrapUrn(urn):
    unwrapped = False
    if urn:
        # normalize URN
        if urn.lower()[:4] == 'urn:':
            # make the first 2 components lowercase
            parts = urn.split(':', 2)
            parts[:2] = [ x.lower() for x in parts[:2] ]
            urn = ':'.join(parts)
            # make hex codes uppercase
            urn = _urn_hex_re.sub(lambda m: '%' + m.group(1).upper(), urn)

        # "unwrap" publicid URN
        if urn[:13] == 'urn:publicid:':
            urn = urn[13:]
            urn = _urn_trans_re.sub(lambda m: _urn_trans_map[m.group()], urn)
            urn = _urn_hex_re.sub(lambda m: chr(int(m.group(1), 16)), urn)
            unwrapped = True

    return (unwrapped, urn)


class Catalog:
    """
    Reads and provides access to a catalog, providing mappings of public
    and system IDs to URIs, etc.

    It is implemented as a SAX ContentHandler and is able to read
    OASIS TR 9401 Catalogs <http://www.oasis-open.org/specs/a401.htm>
    and OASIS XML Catalogs <http://www.oasis-open.org/committees/entity/spec.html>
    """
    def __init__(self, uri, quiet=True):
        self.systemIds = {}
        self.publicIds = {}
        self.uris = {}
        self.publicDelegates = []
        self.systemDelegates = []
        self.uriDelegates = []
        self.systemRewrites = []
        self.uriRewrites = []
        self.catalogs = []
        self.uri = uri
        self.quiet = quiet

        if not Uri.IsAbsolute(uri):
            # Using a relative URI here makes it hard to reliably
            # locate the catalog. Also, if the catalog doesn't set
            # its own base URI with xml:base, then we won't be able
            # to resolve relative URI references within the catalog.
            # So we should warn that this situation is undesirable.
            warnings.warn("Catalog URI '%s' is not absolute.",
                          FtWarning, 2)

        stream = Uri.BASIC_RESOLVER.resolve(uri)
        data = stream.read()
        stream.close()

        if IsXml(data):
            # cannot be a TR 9401 document, assume an XML Catalog
            self._parseXmlCat(data)
        else:
            # cannot be an XML Catalog, assume a TR 9401 file
            self._parseTr9401(data)

        # longest match first
        self.publicDelegates.sort()
        self.publicDelegates.reverse()
        self.systemDelegates.sort()
        self.systemDelegates.reverse()
        self.uriDelegates.sort()
        self.uriDelegates.reverse()
        self.systemRewrites.sort()
        self.systemRewrites.reverse()
        self.uriRewrites.sort()
        self.uriRewrites.reverse()

        if not quiet:
            sys.stderr.write('Catalog contents:\n')
            for key in self.__dict__.keys():
                sys.stderr.write('  %s = %r\n' % (key, self.__dict__[key]))
            sys.stderr.flush()
        return

    def resolveEntity(self, publicId, systemId):
        """
        Return the applicable URI.

        If an external identifier (PUBLIC or SYSTEM) entry exists in the
        Catalog for the identifier(s) specified, return the mapped value.

        External identifiers identify the external subset, entities, and
        notations of an XML document.
        """
        unwrapped, publicId = UnwrapUrn(publicId)
        unwrapped, systemId = UnwrapUrn(systemId)
        # If the system identifier is a URN in the publicid namespace, it is
        # converted into a public identifier by "unwrapping" the URN.
        if unwrapped:
            # 1. No public identifier was provided. Resolution continues as if
            # the public identifier constructed by unwrapping the URN was
            # supplied as the original public identifier and no system
            # identifier was provided.
            if not publicId:
                publicId = systemId
                systemId = None
            # 2. The normalized public identifier provided is lexically
            # identical to the public identifier constructed by unwrapping
            # the URN. Resolution continues as if the system identifier had
            # not been supplied.
            elif publicId == systemId:
                systemId = None
            # 3. The normalized public identifier provided is different from
            # the public identifier constructed by unwrapping the URN. This
            # is an error. Applications may recover from this error by
            # discarding the system identifier and proceeding with the
            # original public identifier.
            else:
                warnings.warn("publicId %r does not match the unwrapped "
                              "systemId %r" % (publicId, systemId),
                              FtWarning, 2)
                systemId = None

        # Resolution follows the steps listed below, proceeding to each
        # subsequent step if and only if no other action is indicated.
        #
        # 1. Resolution begins in the first catalog entry file in the
        # current catalog entry file list.

        if systemId is not None:
            # 2. If a system identifier is provided, and at least one matching
            # system entry exists, the (absolutized) value of the uri
            # attribute of the first matching system entry is returned.
            if systemId in self.systemIds:
                return self.systemIds[systemId]

            # 3. If a system identifier is provided, and at least one matching
            # rewriteSystem entry exists, rewriting is performed.
            #
            # Rewriting removes the matching prefix and replaces it with the
            # rewrite prefix identified by the matching rewriteSystem entry.
            # The rewritten string is returned.
            for length, start, rewrite in self.systemRewrites:
                if start == systemId[:length]:
                    return rewrite + systemId[length:]

            # 4. If a system identifier is provided, and one or more
            # delegateSystem entries match, delegation is performed.
            #
            # If delegation is to be performed, a new catalog entry file list
            # is generated from the set of all matching delegateSystem
            # entries. The (absolutized) value of the catalog attribute of
            # each matching delegateSystem entry is inserted into the new
            # catalog entry file list such that the delegate entry with the
            # longest matching systemIdStartString is first on the list, the
            # entry with the second longest match is second, etc.
            #
            # These are the only catalog entry files on the list, the current
            # list is not considered for the purpose of delegation. If
            # delegation fails to find a match, resolution for this entity
            # does not resume with the current list. (A subsequent resolution
            # attempt for a different entity begins with the original list; in
            # other words the catalog entry file list used for delegation is
            # distinct and unrelated to the "normal" catalog entry file list.)
            #
            # Catalog resolution restarts using exclusively the catalog entry
            # files in this new list and the given system identifier; any
            # originally given public identifier is ignored during the
            # remainder of the resolution of this external identifier: return
            # to step 1.
            attempted = False
            for length, start, catalog in self.systemDelegates:
                if start == systemId[:length]:
                    attempted = True
                    result = catalog.resolveEntity(publicId, systemId)
                    if result:
                        return result
            if attempted:
                # delegation attempted but failed, resolution aborted
                return

        if publicId is not None:
            # 5. If a public identifier is provided, and at least one matching
            # public entry exists, the (absolutized) value of the uri
            # attribute of the first matching public entry is returned. If a
            # system identifier is also provided as part of the input to this
            # catalog lookup, only public entries that occur where the prefer
            # setting is public are considered for matching.
            if publicId in self.publicIds:
                uri, prefer = self.publicIds[publicId]
                if systemId is None or prefer:
                    return uri

            # 6. If a public identifier is provided, and one or more
            # delegatePublic entries match, delegation is performed. If a
            # system identifier is also provided as part of the input to this
            # catalog lookup, only delegatePublic entries that occur where
            # the prefer setting is public are considered for matching.
            #
            # See #4 above for details on delegation.
            attempted = False
            for length, start, catalog, prefer in self.publicDelegates:
                if (systemId is None or prefer) and start == publicId[:length]:
                    attempted = True
                    result = catalog.resolveEntity(publicId, systemId)
                    if result:
                        return result
            if attempted:
                # delegation attempted but failed, resolution aborted
                return

        # 7. If the current catalog entry file contains one or more
        # nextCatalog entries, the catalog entry files referenced by each
        # nextCatalog entry's "catalog" attribute are inserted, in the order
        # that they appear in this catalog entry file, onto the current
        # catalog entry file list, immediately after the current catalog
        # entry file.
        #
        # 8. If there are one or more catalog entry files remaining on the
        # current catalog entry file list, load the next catalog entry file
        # and continue resolution efforts: return to step 2.
        for catalog in self.catalogs:
            result = catalog.resolveEntity(publicId, systemId)
            if result:
                return result

        # 9. Indicate to the calling application that no match was found.
        return


    def resolveURI(self, uri):
        """
        Return the applicable URI.

        If a URI entry exists in the Catalog for the URI specified, return
        the mapped value.

        URI references, for example namespace names, stylesheets, included
        files, graphics, and hypertext references, simply identify other
        resources.
        """
        # If the URI reference is a URN in the publicid namespace
        # ([RFC 3151]), it is converted into a public identifier by
        # "unwrapping" the URN (Section 6.4). Resolution continues by
        # following the semantics of external identifier resolution
        # (Section 7.1) as if the public identifier constructed by
        # unwrapping the URN had been provided and no system identifier had
        # been provided.
        unwrapped, publicId = UnwrapUrn(uri)
        if unwrapped:
            return self.resolveEntity(publicId, None)

        # Resolution of a generic URI reference follows the steps listed
        # below, proceeding to each subsequent step if and only if no other
        # action is indicated.

        # 1. Resolution begins in the first catalog entry file in the
        # current catalog list.

        # 2. If at least one matching uri entry exists, the (absolutized)
        # value of the uri attribute of the first matching uri entry is
        # returned.
        if uri in self.uris:
            return self.uris[uri]

        # 3. If at least one matching rewriteURI entry exists, rewriting is
        # performed.
        #
        # Rewriting removes the matching prefix and replaces it with the
        # rewrite prefix identified by the matching rewriteURI entry. The
        # rewritten string is returned.
        for length, start, rewrite in self.uriRewrites:
            if start == uri[:length]:
                return rewrite + uri[length:]

        # 4. If one or more delegateURI entries match, delegation is performed.
        #
        # If delegation is to be performed, a new catalog entry file list is
        # generated from the set of all matching delegateURI entries. The
        # (absolutized) value of the catalog attribute of each matching
        # delegateURI entry is inserted into the new catalog entry file list
        # such that the delegate entry with the longest matching
        # uriStartString is first on the list, the entry with the second
        # longest match is second, etc.
        #
        # These are the only catalog entry files on the list, the current list
        # is not considered for the purpose of delegation. If delegation fails
        # to find a match, resolution for this entity does not resume with the
        # current list. (A subsequent resolution attempt for a different
        # entity begins with the original list; in other words the catalog
        # entry file list used for delegation is distinct and unrelated to the
        # "normal" catalog entry file list.)
        #
        # Catalog resolution restarts using exclusively the catalog entry
        # files in this new list and the given URI reference: return to step 1.
        attempted = False
        for length, start, catalog in self.uriDelegates:
            if start == uri[:length]:
                attempted = True
                result = catalog.resolveURI(uri)
                if result:
                    return result
        if attempted:
            # delegation attempted but failed, resolution aborted
            return

        # 5. If the current catalog entry file contains one or more
        # nextCatalog entries, the catalog entry files referenced by each
        # nextCatalog entry's "catalog" attribute are inserted, in the order
        # that they appear in this catalog entry file, onto the current
        # catalog entry file list, immediately after the current catalog
        # entry file.
        #
        # 6. If there are one or more catalog entry files remaining on the
        # current catalog entry file list, load the next catalog entry file
        # and continue resolution efforts: return to step 2.
        for catalog in self.catalogs:
            result = catalog.resolveURI(uri)
            if result:
                return result

        # 7. Indicate to the calling application that no match was found.
        return

    def _parseXmlCat(self, data):
        """
        Parse an XML Catalog, as specified in
        http://www.oasis-open.org/committees/entity/spec-2001-08-06.html.
        Partially implemented.
        """
        self.prefer_public = [True]
        self.base = [self.uri]

        # Since we have the catalog data already, parse it.
        source = xmlreader.InputSource(self.uri)
        source.setByteStream(cStringIO.StringIO(data))

        from Ft.Xml.Sax import CreateParser
        p = CreateParser()
        p.setFeature(
          'http://xml.org/sax/features/external-parameter-entities', False)
        p.setContentHandler(self)
        p.parse(source)

        # are these explicit dels needed?
        del self.prefer_public
        del self.base
        return

    def _parseTr9401(self, data):
        """
        Parse a TR9401 Catalog, as specified in
        <http://www.oasis-open.org/specs/a401.htm>.
        Partially implemented.
        """
        prefer_public = True
        base = self.uri
        for cmd in TR9401.findall(data):
            token = cmd[0].upper()
            if token == 'PUBLIC':
                if len(cmd) == 3:
                    self.publicIds[cmd[1]] = (Uri.Absolutize(cmd[2], base), prefer_public)
            elif token == 'SYSTEM':
                if len(cmd) == 3:
                    self.systemIds[cmd[1]] = Uri.Absolutize(cmd[2], base)
            elif token == 'BASE':
                base = cmd[1]
            elif token[:8] == 'OVERRIDE':
                prefer_public = token[8:].strip() == 'YES'
            elif token == 'DELEGATE':
                if len(cmd) == 3:
                    self.publicDelegates[cmd[1]] = Uri.Absolutize(cmd[2], base)
            elif token == 'CATALOG':
                if len(cmd) == 2:
                    catalog = Catalog(Uri.Absolutize(cmd[1], base), self.quiet)
                    self.catalogs.append(catalog)
        return

    # methods used by the XML parser

    def startElementNS(self, (namespace, name), qualifiedName, attrs):
        """
        Handle an element start event for the XML parser.
        This is a SAX ContentHandler method.
        """
        # update current base URI
        base = self.base[-1]
        if name not in ('rewriteSystem', 'rewriteURI'):
            base = attrs.get((XML_NAMESPACE, 'base'), base)
        self.base.append(base)

        if name == 'public':
            # a publicId lookup
            if self.__ensure_attrs(name, attrs, 'publicId', 'uri'):
                # save the state of prefer_public also
                publicId = attrs[(None, 'publicId')]
                uri = Uri.Absolutize(attrs[(None, 'uri')], base)
                self.publicIds[publicId] = (uri, self.prefer_public[-1])
        elif name == 'system':
            # a systemId lookup
            if self.__ensure_attrs(name, attrs, 'systemId', 'uri'):
                systemId = attrs[(None, 'systemId')]
                uri = Uri.Absolutize(attrs[(None, 'uri')], base)
                self.systemIds[systemId] = uri
        elif name == 'uri':
            # a URI lookup
            if self.__ensure_attrs(name, attrs, 'name', 'uri'):
                name = attrs[(None, 'name')]
                uri = Uri.Absolutize(attrs[(None, 'uri')], base)
                self.uris[name] = uri
        elif name == 'rewriteURI':
            # a URI rewrite
            if self.__ensure_attrs(name, attrs, 'uriStartString', 'rewritePrefix'):
                startString = attrs[(None, 'uriStartString')]
                rewritePrefix = Uri.Absolutize(attrs[(None, 'rewritePrefix')],
                                               base)
                rewriteRule = (len(startString), startString, rewritePrefix)
                self.uriRewrites.append(rewriteRule)
        elif name == 'rewriteSystem':
            # a systemId rewrite
            if self.__ensure_attrs(name, attrs, 'systemIdStartString', 'rewritePrefix'):
                startString = attrs[(None, 'systemIdStartString')]
                rewritePrefix = Uri.Absolutize(attrs[(None, 'rewritePrefix')],
                                               base)
                rewriteRule = (len(startString), startString, rewritePrefix)
                self.systemRewrites.append(rewriteRule)
        elif name == 'delegateSystem':
            # delegate systemId to specific catalog
            if self.__ensure_attrs(name, attrs, 'systemIdStartString', 'catalog '):
                startString = attrs[(None, 'systemIdStartString')]
                catalog = Uri.Absolutize(attrs[(None, 'catalog')], base)
                delegate = Catalog(catalog, self.quiet)
                delegateRule = (len(startString), startString, delegate)
                self.systemDelegates.append(delegateRule)

        elif name == 'delegatePublic':
            # delegate publicId to specific catalog
            if self.__ensure_attrs(name, attrs, 'publicIdStartString', 'catalog '):
                # save the state of prefer_public also
                startString = attrs[(None, 'publicIdStartString')]
                catalog = Uri.Absolutize(attrs[(None, 'catalog')], base)
                delegate = Catalog(catalog, self.quiet)
                delegateRule = (len(startString), startString, delegate,
                                self.prefer_public[-1])
                self.publicDelegates.append(delegateRule)
        elif name == 'delegateURI':
            # delegate URI to specific catalog
            if self.__ensure_attrs(name, attrs, 'uriStartString', 'catalog '):
                startString = attrs[(None, 'uriStartString')]
                catalog = Uri.Absolutize(attrs[(None, 'catalog')], base)
                delegate = Catalog(catalog, self.quiet)
                delegateRule = (len(startString), startString, delegate)
                self.uriDelegates.append(delegateRule)
        elif name == 'nextCatalog':
            # the next catalog in a chain
            if self.__ensure_attrs(name, attrs, 'catalog'):
                catalog = Uri.Absolutize(attrs[(None, 'catalog')], base)
                self.catalogs.append(Catalog(catalog, self.quiet))
        elif name in ('catalog', 'group'):
            # look for prefer attribute and update the stack
            prefer = self.prefer_public[-1] and 'public' or 'system'
            prefer = attrs.get((None, 'prefer'), prefer) == 'public'
            self.prefer_public.append(prefer)
        return

    def __ensure_attrs(self, name, attrs, *attr_names):
        """
        Ensure that the right attributes exist just in case the parser
        is a non-validating one.
        """
        for attr_name in attr_names:
            #if not attr_name in attrs:
            if not attrs.has_key((None, attr_name)):
                if not self.quiet:
                    print '%s: Malformed %s element, missing %s attribute' % (self.uri, name, attr_name)
                return False
        return True


    def endElementNS(self, (namespace, name), qualifiedName):
        """
        Handle an element end event for the XML parser.
        This is a SAX ContentHandler method.
        """
        self.base.pop()
        if name in ('catalog', 'group'):
            # pop the stack
            self.prefer_public.pop()
        return


def GetDefaultCatalog(basename='default.cat'):
    """
    Load the default catalog file(s).
    """
    quiet = 'XML_DEBUG_CATALOG' not in os.environ

    uris = []
    # original 4Suite XML Catalog support
    if 'XML_CATALOGS' in os.environ:
        # os.pathsep seperated list of pathnames
        for path in os.environ['XML_CATALOGS'].split(os.pathsep):
            uris.append(Uri.OsPathToUri(path))

    # libxml2 XML Catalog support
    if 'XML_CATALOG_FILES' in os.environ:
        # whitespace-separated list of pathnames or URLs (ick!)
        for path in os.environ['XML_CATALOG_FILES'].split():
            # if its already not already an URL, make it one
            if not Uri.IsAbsolute(path):
                uris.append(Uri.OsPathToUri(path))
            else:
                uris.append(path)

    # add the default 4Suite catalog
    pathname = os.path.join(GetConfigVar('DATADIR'), basename)
    if GetConfigVar('RESOURCEBUNDLE'):
        resource = ImportUtil.OsPathToResource(pathname)
        uri = Uri.ResourceToUri('Ft.Xml', resource)
    else:
        uri = Uri.OsPathToUri(pathname)
    uris.append(uri)

    if not quiet:
        prefix = "Catalog URIs:"
        for uri in uris:
            sys.stderr.write('%s %s\n' % (prefix, uri))
            prefix = " "*len(prefix)

    catalog = None
    for uri in uris:
        if not quiet:
            sys.stderr.write('Reading %s\n' % uri)
            sys.stderr.flush()
        try:
            # FIXME: Use dict merging rather than this inefficient cascading
            if catalog is None:
                if not quiet:
                    sys.stderr.write('Creating catalog from %s\n' % uri)
                    sys.stderr.flush()
                catalog = Catalog(uri, quiet)
            else:
                if not quiet:
                    sys.stderr.write('Appending %s\n' % uri)
                    sys.stderr.flush()
                catalog.catalogs.append(Catalog(uri, quiet))
        except UriException, e:
            #warnings.warn("Catalog resource (%s) disabled: %s" % (uri,
            #                                                      e.message),
            #              FtWarning)
            pass

    if not quiet:
        sys.stderr.write('Done. Result is %r\n' % catalog)
        sys.stderr.flush()

    return catalog
