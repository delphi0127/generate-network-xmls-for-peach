########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/test_harness.py,v 1.29 2006/02/16 20:49:31 jkloth Exp $
"""
Common functions and classes for XSLT test suites

Copyright 2003 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

import os
import cStringIO
from Ft.Lib import Uri, Uuid
from Ft.Xml import READ_EXTERNAL_DTD
from Ft.Xml import InputSource, Domlette
from Ft.Xml.Lib import TreeCompare
from Ft.Xml.XPath import XPathException
from Ft.Xml.Xslt import Processor, XsltException, Error


from Ft.Xml.Xslt import XsltFunctions
g_idmap = {}
def GenerateId(context, nodeSet=None):
    """
    Replacement for XSLT's generate-id(). Generates IDs that are
    unique, but not random, for comparisons in the test suites.
    """
    gen_id = XsltFunctions.GenerateId(context, nodeSet)
    if gen_id:
        id = g_idmap.setdefault(gen_id, len(g_idmap)+1)
        gen_id = u'id%d' % id
    return gen_id

ExtFunctions = {(None, 'generate-id') : GenerateId}


class MappingResolver(Uri.FtUriResolver):
    def __init__(self, uriMapping):
        Uri.FtUriResolver.__init__(self)
        self._uriMapping = uriMapping
        return

    def normalize(self, uriRef, baseUri):
        if uriRef in self._uriMapping:
            return uriRef
        return Uri.FtUriResolver.normalize(self, uriRef, baseUri)

    def resolve(self, uri, baseUri=None):
        if uri in self._uriMapping:
            return cStringIO.StringIO(self._uriMapping[uri])
        return Uri.FtUriResolver.resolve(self, uri, baseUri)

def GetMappingFactory(uriMapping):
    return InputSource.InputSourceFactory(resolver=MappingResolver(uriMapping))

class FileInfo:
    """
    Encapsulates a file given as a string or URI, so that it can be
    referenced in various ways. Used by XsltTest().
    """
    def __init__(self, uri=None, string=None, baseUri='', validate=False,
                 **kwords):
        self.uri = uri
        self.string = string
        self.baseUri = baseUri
        self.validate = validate
        self.args = kwords

        # Same logic that exists in _4xslt.py
        # The processor only deals with URIs, not file paths
        if uri and os.path.isfile(uri):
            self.uri = Uri.OsPathToUri(os.path.abspath(uri))
        if not (uri or string):
            raise ValueError('Either string or uri are required')

        if string and not baseUri:
            base = os.path.join(os.path.abspath(os.getcwd()),
                                Uuid.UuidAsString(Uuid.GenerateUuid()))
            self.baseUri = Uri.OsPathToUri(base)
        return

    def toInputSource(self, factory):
        if self.uri:
            source = factory.fromUri(self.uri, **self.args)
        else:
            source = factory.fromString(self.string, self.baseUri, **self.args)
        return source


def XsltTest(tester, sourceXml, stylesheets, expected, compareFunc=None,
             ignorePis=1, topLevelParams=None, extensionModules=None,
             exceptionClass=XsltException, exceptionCode=None,
             stylesheetInputFactory=None, documentInputFactory=None,
             stylesheetAltUris=None, title='', funcArgs=None):
    """
    Common function to perform an XSLT transformation and compare the
    results through the tester.

    title is a short name that describes the test.

    tester is an Ft.Lib.TestSuite.Tester instance.

    sourceXml is a FileInfo instance for the source document.

    stylesheets is a list of FileInfo instances for the stylesheet(s).

    expected is a string to compare the actual transformation result to.

    compareFunc is a cmp()-like function to use to do the comparison.
    It defaults to whatever the tester's default is; usually cmp().
    funcArgs is a dictionary of keyword arguments to pass to the
    comparison function, if it accepts keyword arguments.

    ignorePis, topLevelParams, extensionModules, stylesheetAltUris are
    as documented in Ft.Xml.Xslt.Processor.Processor.

    exceptionCode is the expected exception code, if the test is
    intended to generate an exception.

    documentInputFactory, stylesheetInputFactory are InputSource
    factories to use when resolving references to external URIs from
    within the source document or stylesheet(s), respectively. Defaults
    for both are Ft.Xml.InputSource.DefaultFactory.
    """
    # reset the counter for generate-id
    g_idmap.clear()

    if not title:
        title = 'Source %(source)s' % (tester.test_data)
    tester.startTest(title)

    # Create the processor
    processor = Processor.Processor(stylesheetAltUris=stylesheetAltUris)
    processor.registerExtensionModules([__name__])
    if extensionModules:
        processor.registerExtensionModules(extensionModules)

    # Setup document input for the processor
    factory = documentInputFactory or InputSource.DefaultFactory
    reader = Domlette._Reader(tester.test_data['module'].NonvalParse,
                              kwargs={'readExtDtd': READ_EXTERNAL_DTD})
    reader.inputSourceFactory = factory
    processor.setDocumentReader(reader)

    # Do the transformation
    try:
        # Add the stylesheets to the processor
        factory = stylesheetInputFactory or InputSource.DefaultFactory
        for stylesheet in stylesheets:
            processor.appendStylesheet(stylesheet.toInputSource(factory))

        result = processor.run(sourceXml.toInputSource(factory),
                               ignorePis=ignorePis,
                               topLevelParams=topLevelParams)
    except exceptionClass, exception:
        if exceptionCode is None:
            # No exception was expected
            estr = _PrettifyException(exceptionClass, exception.errorCode)
            tester.exception('Unexpected exception ' + estr)
        else:
            # Compare the exception result
            expected = _PrettifyException(exceptionClass, exceptionCode)
            compared = _PrettifyException(exceptionClass, exception.errorCode)
            tester.compare(expected, compared, stackLevel=2)
    else:
        if expected is None and exceptionCode is not None:
            # An exception was expected
            estr = _PrettifyException(exceptionClass, exceptionCode)
            tester.error(estr + ' not raised', stackLevel=2)
        else:
            # Compare the processor result
            outputParams = processor.outputParams
            if compareFunc is not None:
                name = compareFunc.__module__ + '.' + compareFunc.__name__
                tester.warning("Overridden compareFunc (%s)" % name)
                
            if outputParams.method == (None, 'text'):
                compareFunc = cmp
            elif outputParams.method == (None, 'html'):
                compareFunc = TreeCompare.HtmlTreeCompare
            elif outputParams.method == (None, 'xml'):
                compareFunc = TreeCompare.XmlTreeCompare

            tester.compare(expected, result, diff=1, func=compareFunc,
                           stackLevel=2, funcArgs=funcArgs or {})

    tester.testDone()
    return

def _PrettifyException(etype, errorCode):
    if issubclass(etype, XsltException):
        # error code is defined by Ft.Xml.Xslt.Error
        for k, v in vars(Error).items():
            if v == errorCode:
                errorCode = "Error." + k
                break
    elif issubclass(etype, XPathException):
        # error code is defined by the exception class
        for k, v in vars(etype).items():
            if v == errorCode:
                errorCode = etype.__name__ + '.' + k
                break
    return '%s(%s)' % (etype.__name__, errorCode)
