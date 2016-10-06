import os, cStringIO

from xml.dom import Node
from Ft.Lib import Uri
from Ft.Xml import ReaderException, Domlette, InputSource
from Ft.Xml.Lib import TreeCompare

# Py 2.2 doesn't have UnicodeEncodeError
try:
    UnicodeEncodeError
except NameError:
    UnicodeEncodeError = None

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
BASE_PATH = Uri.OsPathToUri(BASE_PATH, attemptAbsolute=True) + '/'

def CompareXml(expected, compared):
    try:
        rv = TreeCompare.TreeCompare(expected, compared, baseUri=BASE_PATH)
        return rv
    except Exception, e:
        import traceback
        traceback.print_exc()
        return 1

def CompareXmlNode(expected, compared, ignoreComments=0):
    try:
        return TreeCompare.NodeCompare(expected, compared,
                                       ignoreComments=ignoreComments)
    except Exception, e:
        import traceback
        traceback.print_exc()
        return 1

def test_reader(tester,domMod):
    tester.startGroup("DOM Readers")
    test_validating_reader(tester, domMod)
    test_nonvalidating_reader(tester, domMod)
    test_xml_base(tester, domMod)
    test_extent_xinclude(tester, domMod)
    test_strip_elements(tester, domMod)
    test_namespaces(tester, domMod)
    test_read_utf16(tester, domMod)
    test_unknown_encoding(tester, domMod)
    test_encoding_override(tester, domMod)
    test_read_exceptions(tester, domMod.NonvalParse)
    test_various_docs(tester, domMod)
    tester.groupDone()
    return

def test_oasis_suite(tester, domMod):
    test_suite_root_var = 'W3C_XMLTS_ROOT'
    tester.startGroup("W3C XML Conformance Test Suites (XML TS)")
    if not os.environ.has_key(test_suite_root_var):
        tester.warning('Not tested; set %s to point to the'
                       ' xmlconf directory.' % test_suite_root_var)
        tester.groupDone()
        return
    else:
        XMLTS_BASE = os.environ[test_suite_root_var]

    if not os.path.isfile(os.path.join(XMLTS_BASE, 'xmlconf.xml')):
        tester.warning('Not tested; directory %s does not seem to'
                       ' contain the W3C XML Conformance Test Suite'
                       ' XML TS files.' % test_suite_root_var)
        tester.groupDone()
        return

    tester.startGroup("James Clark's XML Test Cases (1998-11-18)")
    # (casedir, casename, use validating parser?, expect exception?)
    JCLARK_CASES = [ ('not-wf', 'Not well-formed', 0, 1),
                     ('valid', 'Valid', 1, 0),
                     ('invalid', 'Invalid', 1, 1),
                   ]
    JCLARK_SUBCASES = [ ('sa', 'Standalone; no ext. general entity refs'),
                        ('ext-sa', 'Standalone; w/ ext. general entity refs'),
                        ('not-sa', 'Not standalone'),
                      ]
    TESTS_TO_SKIP = {
                      ('valid', 'sa', '012.xml'): 'only OK in non-namespace-aware system',
                    }

    # not-wf/not-sa/005.xml, although documented as testing a VC, should
    #  actually first fail on an obscure WFC. However, exactly what the
    #  expected error is seems to be something known only to a non-public
    #  W3C group. See the discussion at
    # http://lists.w3.org/Archives/Public/public-xml-testsuite/2002Jun/0018.html
    # http://lists.w3.org/Archives/Public/public-xml-testsuite/2002Jun/0022.html
    # http://lists.w3.org/Archives/Public/public-xml-testsuite/2004Sep/0002.html
    # http://lists.w3.org/Archives/Public/public-xml-testsuite/2005Mar/0002.html
    #
    # not-wf/not-sa/010.xml and not-wf/not-sa/011.xml
    # are supposed to fail "WFC: PE Between Declarations"
    # according to this message:
    # http://lists.w3.org/Archives/Public/public-xml-testsuite/2002Jun/0018.html
    #
    for casedir, casename, validating, exc_expected in JCLARK_CASES:
        for subcasedir, subcasename in JCLARK_SUBCASES:
            DIR = os.path.join(XMLTS_BASE, 'xmltest', casedir, subcasedir)
            if not os.path.isdir(DIR):
                continue

            tester.startGroup('%s; %s' % (casename, subcasename))
            XML_FILENAMES = [ f for f in os.listdir(DIR)
                              if f.endswith('.xml') ]
            XML_FILENAMES.sort()
            for filename in XML_FILENAMES:
                tester.startTest(filename)
                skipkey = (casedir, subcasedir, filename)
                if TESTS_TO_SKIP.has_key(skipkey):
                    tester.warning('Not tested; %s' % TESTS_TO_SKIP[skipkey])
                else:
                    XML_FILEPATH = os.path.join(DIR, filename)
                    uri = Uri.OsPathToUri(XML_FILEPATH)
                    isrc = InputSource.DefaultFactory.fromUri(uri)
                    if exc_expected:
                        if validating:
                            parse = domMod.ValParse
                        else:
                            parse = domMod.NonvalParse
                        tester.testException(parse, (isrc,), ReaderException)
                    elif validating:
                        try:
                            dom = domMod.ValParse(isrc)
                        except ReaderException:
                            tester.exception('The validating reader raised'
                                             ' an unexpected exception.')
                        else:
                            # The document parsed without exceptions, so
                            # now let's check the parsed document against the
                            # parsed Canonical XML equivalent, if available
                            try:
                                CXML_FILEPATH = os.path.join(DIR, 'out', filename)
                            except:
                                print "os.path.join(%r,'out',%r)" % (DIR,
                                                                     filename)
                                raise
                            if os.path.isfile(CXML_FILEPATH):
                                uri = Uri.OsPathToUri(CXML_FILEPATH)
                                isrc = InputSource.DefaultFactory.fromUri(uri)
                                try:
                                    cdom = domMod.NonvalParse(isrc)
                                except ReaderException:
                                    tester.exception('The nonvalidating reader'
                                                     ' raised an unexpected'
                                                     ' exception.')
                                else:
                                    if not CompareXmlNode(cdom, dom,
                                                          ignoreComments=1):
                                        tester.error('The validating reader'
                                                     ' parsed the document'
                                                     ' incorrectly.')

                    else:
                        try:
                            dom = domMod.NonvalParse(isrc)
                        except ReaderException:
                            tester.exception('The nonvalidating reader raised'
                                             ' an unexpected exception.')

                tester.testDone()
            tester.groupDone()

    tester.groupDone() # James Clark's XML Test Cases

    tester.startGroup("SUN Microsystems XML test cases")
    tester.warning("Not tested.")
    tester.groupDone() # SUN

    tester.startGroup("OASIS XML test cases")
    tester.warning("Not tested.")
    tester.groupDone() # OASIS

    tester.startGroup("Fuji Xerox XML test cases")
    tester.warning("Not tested.")
    tester.groupDone() # Fuji Xerox

    tester.groupDone() # OASIS XML Test Suite

def test_read_utf16(tester,domMod):
    tester.startGroup("Read UTF-16")

    tester.startTest("Good XML: UTF-16LE, LE BOM, utf-16 encoding declaration")
    isrc = InputSource.DefaultFactory.fromUri(BASE_PATH + 'goodXml_16LE_LEBOM_16Decl.xml')
    dom = domMod.NonvalParse(isrc)
    tester.testDone()

    tester.startTest("Good XML: UTF-16BE, BE BOM, utf-16 encoding declaration")
    isrc = InputSource.DefaultFactory.fromUri(BASE_PATH + 'goodXml_16BE_BEBOM_16Decl.xml')
    dom = domMod.NonvalParse(isrc)
    tester.testDone()

    tester.startTest("Good XML: UTF-16LE, LE BOM, no encoding declaration")
    isrc = InputSource.DefaultFactory.fromUri(BASE_PATH + 'goodXml_16LE_LEBOM_noDecl.xml')
    dom = domMod.NonvalParse(isrc)
    tester.testDone()

    tester.startTest("Good XML: UTF-16BE, BE BOM, no encoding declaration")
    isrc = InputSource.DefaultFactory.fromUri(BASE_PATH + 'goodXml_16BE_BEBOM_noDecl.xml')
    dom = domMod.NonvalParse(isrc)
    tester.testDone()

    tester.startTest("Bad XML: UTF-16LE, BE BOM, utf-16 encoding declaration")
    # A big-endian BOM will result in little-endian prolog being interpreted as
    # Chinese characters, resulting in a well-formedness error because there
    # is no document element
    isrc = InputSource.DefaultFactory.fromUri(BASE_PATH + 'badXml_16LE_BEBOM_16Decl.xml')
    tester.testException(domMod.NonvalParse, (isrc,), ReaderException)
    tester.testDone()

    tester.startTest("Bad XML: UTF-16LE, LE BOM, utf-16le encoding declaration")
    # by definition, utf-16le and utf-16be do not have a BOM. if a little-endian
    # BOM is encountered, it is interpreted as a zero-width no-break space, which
    # is not allowed at the beginning of an XML document entity.
    isrc = InputSource.DefaultFactory.fromUri(BASE_PATH + 'badXml_16LE_LEBOM_16LEDecl.xml')
    tester.warning("Skipping; most parsers, including Expat, do not treat this as an error") # why not?
    # Oracle XML Parser: "Illegal change of encoding: from UTF-16 to utf-16le"
    # Aelfred (in Saxon 6.5.3): ZWNBS ignored
    # Xerces 2.0.0: ZWNBS ignored
    # MSXML: ZWNBS ignored
    # xmllib: ZWNBS ignored
    # Firefox: ZWNBS ignored
    # Expat (all versions): ZWNBS ignored
    tester.testDone()

    tester.startTest("Bad XML: UTF-16LE, no BOM, utf-16 encoding declaration")
    # if the encoding declaration is "utf-16", a BOM is required. without a BOM,
    # UTF-8 will be assumed initially, so each 0x00 byte will be interpreted as
    # U+0000, which is not allowed in an XML document
    isrc = InputSource.DefaultFactory.fromUri(BASE_PATH + 'badXml_16LE_noBOM_16Decl.xml')
    tester.warning("Skipping; some parsers, including Expat, do not treat this as an error") # why not?
    # Oracle XML Parser (on x86): treats as UTF-16LE
    # Aelfred (in Saxon 6.5.3): "no byte-order mark for UCS-2 entity"
    # Xerces 2.0.0: treats as UTF-16LE
    # MSXML: "A name was started with an invalid character."
    # xmllib: "invalid element name"
    # Firefox: treats as UTF-16LE
    # Expat (all versions): treats as UTF-16LE
    tester.testDone()

    tester.startTest("Bad XML: UTF-8, no BOM, utf-16 encoding declaration")
    # if the encoding declaration is "utf-16", a BOM is required. without a BOM,
    # UTF-8 will be assumed initially, so the xml declaration is readable, but
    # when the "utf-16" is encountered, a fatal error must occur because there
    # is no BOM. if the parser doesn't catch this error, it should then have a
    # well-formedness error because there is no document element, only a string
    # of non-Latin characters
    isrc = InputSource.DefaultFactory.fromUri(BASE_PATH + 'badXml_utf8_noBOM_16Decl.xml')
    tester.testException(domMod.NonvalParse, (isrc,), ReaderException)
    tester.testDone()

    tester.groupDone()
    return


def test_unknown_encoding(tester, domMod):
    tester.startGroup("Unknown encoding support")
    encodings = [('iso-8859-2', '\xA1', u'\u0104'),
                 ('iso-8859-3', '\xA1', u'\u0126'),
                 ('iso-8859-4', '\xA1', u'\u0104'),
                 ('iso-8859-5', '\xA1', u'\u0401'),
                 ('iso-8859-6', '\xAC', u'\u060C'),
                 ('iso-8859-7', '\xA1', u'\u2018'),
                 ('iso-8859-8', '\xAA', u'\u00D7'),
                 ('iso-8859-9', '\xD0', u'\u011E'),
                 ('iso-8859-10', '\xA1', u'\u0104'),
                 ('iso-8859-13', '\xA1', u'\u201D'),
                 ('iso-8859-14', '\xA1', u'\u1E02'),
                 ('iso-8859-15', '\xA4', u'\u20AC'),
                 ('koi8-r', '\x80', u'\u2500'),
                 ]
    # add some multi-byte encodings
    try:
        '\xA1\xA1'.decode('euc-jp')
    except LookupError:
        pass
    else:
        encodings.append(('euc-jp', '\xA1\xA1', u'\u3000'))
    try:
        '\x8F\x40'.decode('shift-jis')
    except LookupError:
        pass
    else:
        encodings.append(('shift-jis', '\x8F\x40', u'\u5B97'))

    for encoding, byte, char in encodings:
        tester.startTest(encoding)
        src = "<?xml version='1.0' encoding='%s'?><char>%s</char>" % (encoding,
                                                                      byte)
        isrc = InputSource.DefaultFactory.fromString(src, 'file:'+encoding)
        doc = domMod.NonvalParse(isrc)
        tester.compare(char, doc.documentElement.firstChild.data)
        tester.testDone()
    tester.groupDone()
    return


def test_encoding_override(tester, domMod):
    tester.startGroup("External encoding declaration")
    for actual_enc in ('utf-8', 'iso-8859-1', 'us-ascii', 'utf-16'):
        for declared_enc in ('utf-8', 'iso-8859-1', 'us-ascii', 'utf-16', 'x-klingon'):
            tester.startTest('declared internally: %s; externally/actual: %s' % (declared_enc, actual_enc))
            src = JGREETING_UNICODE % declared_enc
            try:
                src = src.encode(actual_enc)
            except (UnicodeError, UnicodeEncodeError):
                src = JGREETING_ESCAPED % declared_enc
                src = src.encode(actual_enc)

            isrc = InputSource.DefaultFactory.fromString(src, 'http://4suite.org/jgreeting.xml', encoding=actual_enc)
            doc = domMod.NonvalParse(isrc)
            chars = doc.documentElement.firstChild.data
            tester.compare(u'\u4eca\u65e5\u306f', chars)
            tester.testDone()
    tester.groupDone()


def test_strip_elements(tester,domMod):
    tester.startGroup("Strip Elements")

    tester.startTest("Strip Elements")
    src = "<ft:foo xmlns:ft='http://fourthought.com' xmlns:ft2='http://foo.com'><ft:bar>  </ft:bar><ft:bar> F </ft:bar><ft:baz>  Bar1  </ft:baz><ft2:bar>  </ft2:bar><ft2:baz> Bar2 </ft2:baz><bar>  </bar><baz>  Bar3  </baz></ft:foo>"

    stripElements = [(None,'bar',1),
                     ('http://fourthought.com','bar',1),
                     ('http://foo.com','*',1)]

    isrc = InputSource.DefaultFactory.fromString(src, BASE_PATH,
                                                 stripElements=stripElements)
    dom = domMod.NonvalParse(isrc)

    tester.compare(None,dom.documentElement.childNodes[0].firstChild)
    tester.compare(" F ",dom.documentElement.childNodes[1].firstChild.data)
    tester.compare("  Bar1  ",dom.documentElement.childNodes[2].firstChild.data)
    tester.compare(None,dom.documentElement.childNodes[3].firstChild)
    tester.compare(" Bar2 ",dom.documentElement.childNodes[4].firstChild.data)
    tester.compare(None,dom.documentElement.childNodes[5].firstChild)
    tester.compare("  Bar3  ",dom.documentElement.childNodes[6].firstChild.data)
    tester.testDone()

    tester.startTest("Strip Elements with xml:space")
    src = """\
<svg xml:space="preserve" width="1000" height="1000"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <desc>Salary Chart</desc>
  <g style='stroke:#000000;stroke-width:1;font-family:Arial;font-size:16'>
    <xsl:for-each select="ROWSET/ROW">
      <xsl:call-template name="drawBar" xml:space="default">
        <xsl:with-param name="rowIndex" select="position()"/>
        <xsl:with-param name="ename" select="ENAME"/>
        <xsl:with-param name="sal" select="number(SAL)"/>
      </xsl:call-template>
    </xsl:for-each>
  </g>
</svg>"""

    expected = """<?xml version="1.0" encoding="UTF-8"?>
<svg xml:space="preserve" width="1000" height="1000"
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
 <desc>Salary Chart</desc>
  <g style='stroke:#000000;stroke-width:1;font-family:Arial;font-size:16'>
    <xsl:for-each select="ROWSET/ROW">
      <xsl:call-template name="drawBar" xml:space="default"><xsl:with-param name="rowIndex" select="position()"/><xsl:with-param name="ename" select="ENAME"/><xsl:with-param name="sal" select="number(SAL)"/></xsl:call-template>
    </xsl:for-each>
  </g>
</svg>"""

    src = """<?xml version="1.0" encoding="UTF-8"?>
<element xml:space="preserve">
  <element>
    <!-- surrounding WS should be preserved -->
  </element>
</element>"""

    stripElements = [(None, '*', True)]

    isrc = InputSource.DefaultFactory.fromString(src, BASE_PATH,
                                                 stripElements=stripElements)
    dom = domMod.NonvalParse(isrc)
    sio = cStringIO.StringIO()
    Domlette.Print(dom, sio)
    actual = sio.getvalue()
    tester.compare(src, actual, func=TreeCompare.TreeCompare)
    tester.testDone()

    tester.groupDone()
    return


def test_xml_base(tester, domMod):
    tester.startGroup("XML Base")

    tester.startTest("xml-base")
    src = BASE_TEST

    #strip all ws, set document base URI
    isrc = InputSource.DefaultFactory.fromString(src,"http://rdfInference.org",stripElements=[(None, '*', 1)])
    dom = domMod.NonvalParse(isrc)

    tester.compare("http://rdfInference.org", dom.baseURI)
    spam = dom.documentElement
    tester.compare("http://rdfInference.org", spam.baseURI)
    eggs = spam.firstChild
    tester.compare("http://fourthought.com", eggs.baseURI)
    monty = eggs.firstChild
    tester.compare("http://fourthought.com", monty.baseURI)
    knight = monty.firstChild
    tester.compare("http://fourthought.com", knight.baseURI)
    foo = eggs.childNodes[1]
    tester.compare("http://4suite.org", foo.baseURI)
    foobar = foo.firstChild
    tester.compare("http://4suite.org", foobar.baseURI)
    all = foo.childNodes[1]
    tester.compare("http://4suite.org/your-base", all.baseURI)
    are_what = all.firstChild
    tester.compare("http://4suite.org/your-base", are_what.baseURI)

    tester.testDone()

    tester.groupDone()
    return


def test_validating_reader(tester,domMod):
    tester.startGroup("Validating Reader")

    for title, source, rootName in (('ADDRBOOK', ADDRBOOK, 'ADDRBOOK'),
                                    ('xml:space', XML_SPACE_VALID, 'doc'),
                                    ):
        tester.startTest("Read Valid Document: %s" % title)
        isrc = InputSource.DefaultFactory.fromString(source, BASE_PATH)
        dom = domMod.ValParse(isrc)
        if dom.documentElement:
            tester.compare(rootName, dom.documentElement.localName)
        else:
            tester.error("Validating parser returned an empty document")
        tester.testDone()

    for title, source in (('ADDRBOOK', ADDRBOOK_INVALID),
                          ('empty element', INVALID_EMPTY),
                          ('xml:space type', XML_SPACE_DECL),
                          ('xml:space values', XML_SPACE_VALUES),
                          ):
        tester.startTest("Read Invalid Document: %s" % title)
        isrc = InputSource.DefaultFactory.fromString(source, BASE_PATH)
        tester.testException(domMod.ValParse, (isrc,), ReaderException)
        tester.testDone()

    tester.groupDone()
    return


def test_nonvalidating_reader(tester,domMod):
    tester.startGroup("non-Validating Reader")


    tester.startTest("Simple XML")
    src = InputSource.DefaultFactory.fromString(SMALL_XML, BASE_PATH)
    doc = domMod.NonvalParse(src)

    #Test a few of the nodes
    tester.compare(2,len(doc.childNodes))
    tester.compare(Node.PROCESSING_INSTRUCTION_NODE,doc.childNodes[0].nodeType)
    tester.compare("xml-stylesheet",doc.childNodes[0].target)
    tester.compare('href="addr_book1.xsl" type="text/xml"',doc.childNodes[0].data)

    tester.compare(Node.ELEMENT_NODE,doc.childNodes[1].nodeType)
    tester.compare('docelem',doc.childNodes[1].nodeName)
    tester.compare(None,doc.childNodes[1].namespaceURI)
    tester.compare(None,doc.childNodes[1].prefix)
    tester.compare(doc.childNodes[1],doc.documentElement)
    tester.compare(9,len(doc.documentElement.childNodes))

    tester.compare(1,len(doc.documentElement.attributes.keys()))
    tester.compare(('http://www.w3.org/2000/xmlns/', 'ft'),doc.documentElement.attributes.keys()[0])
    tester.compare('http://fourthought.com',doc.documentElement.attributes.values()[0].value)

    tester.compare(1,len(doc.documentElement.childNodes[1].attributes.keys()))
    tester.compare((None,'foo'),doc.documentElement.childNodes[1].attributes.keys()[0])
    tester.compare('bar',doc.documentElement.childNodes[1].attributes.values()[0].value)
    tester.compare('Some Text',doc.documentElement.childNodes[1].childNodes[0].data)


    tester.compare('http://fourthought.com',doc.documentElement.childNodes[5].namespaceURI)
    tester.compare('ft',doc.documentElement.childNodes[5].prefix)
    tester.compare(1,len(doc.documentElement.childNodes[5].attributes.keys()))
    tester.compare(('http://fourthought.com','foo'),doc.documentElement.childNodes[5].attributes.keys()[0])
    tester.compare('nsbar',doc.documentElement.childNodes[5].attributes.values()[0].value)
    tester.testDone()

    tester.startTest("Parse nasty XML")
    src = InputSource.DefaultFactory.fromString(LARGE_XML, BASE_PATH)
    doc = domMod.NonvalParse(src)
    tester.testDone()

    tester.startTest("Document with general entity defined in external subset (parse method 1)")
    source_1 = GREETING
    isrc = InputSource.DefaultFactory.fromString(source_1, BASE_PATH)
    dom = domMod.NonvalParse(isrc, readExtDtd=1)
    stream = cStringIO.StringIO()
    Domlette.Print(dom, stream)
    expected_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<greeting>hello world</greeting>
"""
    tester.compare(expected_1, stream.getvalue(), func=CompareXml)
    tester.testDone()

    # same as previous test but going through Ft.Xml.Domlette
    tester.startTest("Document with general entity defined in external subset (parse method 2)")
    source_1 = GREETING
    isrc = InputSource.DefaultFactory.fromString(source_1, BASE_PATH)
    from Ft.Xml.Domlette import NonvalidatingReaderBase
    reader = NonvalidatingReaderBase()
    reader.kwargs['readExtDtd'] = 1
    dom = reader.parse(isrc)
    stream = cStringIO.StringIO()
    Domlette.Print(dom, stream)
    expected_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<greeting>hello world</greeting>
"""
    tester.compare(expected_1, stream.getvalue(), func=CompareXml)
    tester.testDone()
    tester.groupDone()


def test_read_exceptions(tester,parseMethod):
    tester.startGroup("Reader exceptions")

    for title, source in (('Syntax Error', "<>"),
                          ('No Elements', "<?xml version='1.0'?>"),
                          ('Tag Mismatch', "<foo></bar>"),
                          ):
        tester.startTest("Basic Parse Exceptions: %s" % title)
        isrc = InputSource.DefaultFactory.fromString(source, BASE_PATH)
        tester.testException(parseMethod, (isrc,), ReaderException)
        tester.testDone()

    tester.startTest("XML 1.0 containing namespace prefix undeclaration")
    src = InputSource.DefaultFactory.fromString(XML10_PREFIX_UNDECL, BASE_PATH)
    tester.testException(parseMethod, (src,), ReaderException)
    tester.testDone()

    tester.groupDone()


def test_namespaces(tester,domMod):
    expected = [(None,'xmlns','http://www.w3.org/2000/xmlns/'),
                ('xmlns','are','http://www.w3.org/2000/xmlns/'),
                ('xmlns','foo','http://www.w3.org/2000/xmlns/'),
                ]

    src="""<?xml version="1.0"?>
<diamonds xmlns:are="urn:forever" xmlns:foo="urn:bar" xmlns="http://nowhere"/>"""



    tester.startGroup("Namespaces")

    tester.startTest("Simple test")
    isrc = InputSource.DefaultFactory.fromString(src, BASE_PATH)
    doc = domMod.NonvalParse(isrc)
    attrs = doc.documentElement.attributes.values()
    attrs.sort(lambda a, b: cmp(a.name, b.name))
    tester.compare(3,len(attrs))
    for attr in attrs:
        test = (attr.prefix,attr.localName,attr.namespaceURI)
        tester.compareIn(expected,test)
    tester.testDone()
    tester.groupDone()
    return

    tester.startTest("Parse XML 1.1 containing namespace prefix undeclaration (OK)")
    src = InputSource.DefaultFactory.fromString(XML_11_PREFIX_UNDECL, BASE_PATH)
    doc = domMod.NonvalParse(src)
    tester.testDone()

    tester.groupDone()



def test_extent_xinclude(tester, domMod):
    tester.startGroup("Reader + External Entities + XInclude")

    SRC_1 = """\
<?xml version='1.0'?>
<!DOCTYPE x [ <!ENTITY inc SYSTEM "include1.xml"> ]>
<x>
&inc;
</x>"""
    expected_1="""<?xml version='1.0' encoding='UTF-8'?><x>

<foo xml:base="%s"/>
</x>""" % Uri.Absolutize("include1.xml", BASE_PATH)
    tester.startTest("External entity")

    src = InputSource.DefaultFactory.fromString(SRC_1, BASE_PATH)

    doc = domMod.NonvalParse(src)
    stream = cStringIO.StringIO()
    Domlette.Print(doc, stream)
    tester.compare(expected_1, stream.getvalue(), func=TreeCompare.TreeCompare)
    tester.testDone()

    SRC_2 = """\
<?xml version='1.0'?>
<x xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include href="include1.xml"/>
</x>"""

    expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<x xmlns:xi='http://www.w3.org/2001/XInclude'>
<foo xml:base="%s"/>
</x>""" % Uri.Absolutize("include1.xml", BASE_PATH)
    tester.startTest("Basic XInclude")
    src = InputSource.DefaultFactory.fromString(SRC_2, BASE_PATH)
    doc = domMod.NonvalParse(src)
    stream = cStringIO.StringIO()
    Domlette.Print(doc, stream)
    tester.compare(expected_2, stream.getvalue(), func=TreeCompare.NoWsTreeCompare)
    tester.testDone()

    SRC_3="""\
<?xml version='1.0'?>
<x xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include href="include2.xml"/>
</x>"""
    expected_3="""<?xml version='1.0' encoding='UTF-8'?>
<x xmlns:xi='http://www.w3.org/2001/XInclude'>
<foo xml:base="%s">
  <foo xml:base="%s"/>
</foo>
</x>
""" % (Uri.Absolutize("include2.xml", BASE_PATH),
       Uri.Absolutize("include1.xml", BASE_PATH))
    tester.startTest("Recursive XInclude")
    src = InputSource.DefaultFactory.fromString(SRC_3, BASE_PATH)
    doc = domMod.NonvalParse(src)
    stream = cStringIO.StringIO()
    Domlette.Print(doc, stream)
    tester.compare(expected_3, stream.getvalue(), func=TreeCompare.NoWsTreeCompare)
    tester.testDone()

    SRC_4="""\
<?xml version='1.0'?>
<x xmlns:xi="http://www.w3.org/2001/XInclude">
<xi:include href="include2.xml" parse='text'/>
</x>"""
    from test_xinclude import LINESEP
    expected_4="""<?xml version='1.0' encoding='UTF-8'?>
<x xmlns:xi='http://www.w3.org/2001/XInclude'>
&lt;?xml version='1.0' encoding='utf-8'?>%(linesep)s&lt;foo xmlns:xi="http://www.w3.org/2001/XInclude">%(linesep)s  &lt;xi:include href="include1.xml"/>%(linesep)s&lt;/foo>
</x>
""" % {'linesep' : LINESEP}

    tester.startTest("XInclude text attribute")
    src = InputSource.DefaultFactory.fromString(SRC_4, BASE_PATH)
    doc = domMod.NonvalParse(src)
    stream = cStringIO.StringIO()
    Domlette.Print(doc, stream)
    tester.compare(expected_4, stream.getvalue(),func = TreeCompare.TreeCompare)
    tester.testDone()

    tester.groupDone()
    return

def test_various_docs(tester, domMod):

    def test_one_str(count, content, exception, tester=tester, module=domMod):
        tester.startTest("Document %d non-validating" % count)
        src = InputSource.DefaultFactory.fromString(content, BASE_PATH)
        if exception:
            tester.testException(module.NonvalParse, (src,), ReaderException)
        else:
            doc = module.NonvalParse(src)
            stream = cStringIO.StringIO()
            Domlette.Print(doc, stream)
            tester.compare(content, stream.getvalue(), func=CompareXml)
        tester.testDone()

        tester.startTest("Document %d validating" % count)
        src = InputSource.DefaultFactory.fromString(content, BASE_PATH)
        if exception:
            tester.testException(module.NonvalParse, (src,),
                                 ReaderException)
        else:
            doc = module.ValParse(src)
            stream = cStringIO.StringIO()
            Domlette.Print(doc, stream)
            tester.compare(content, stream.getvalue(), func=CompareXml)
        tester.testDone()
        return

    def test_one_uri(count, uri, exception, tester=tester, module=domMod):
        tester.startTest("Document %d non-validating" % count)
        src = InputSource.DefaultFactory.fromUri(uri, BASE_PATH)
        if exception:
            tester.testException(module.NonvalParse, (src,), ReaderException)
        else:
            doc = module.NonvalParse(src)
            stream = cStringIO.StringIO()
            Domlette.Print(doc, stream)
            src = InputSource.DefaultFactory.fromUri(uri, BASE_PATH)
            tester.compare(src.read(), stream.getvalue(), func=CompareXml)
        tester.testDone()

        tester.startTest("Document %d validating" % count)
        src = InputSource.DefaultFactory.fromUri(uri, BASE_PATH)
        if exception:
            tester.testException(module.NonvalParse, (src,),
                                 ReaderException)
        else:
            doc = module.ValParse(src)
            stream = cStringIO.StringIO()
            Domlette.Print(doc, stream)
            src = InputSource.DefaultFactory.fromUri(uri, BASE_PATH)
            tester.compare(src.read(), stream.getvalue(), func=CompareXml)
        tester.testDone()
        return

    tester.startGroup("Simple round trip of various XML (as strings)")
    count = 1
    for string in VARIOUS_STRINGS:
        test_one_str(count, string, 0)
        count += 1
    tester.groupDone()


    tester.startGroup("Simple round trip of various XML (as files)")
    count = 1
    for uri in VARIOUS_FILES:
        test_one_uri(count, uri, 0)
        count += 1
    tester.groupDone()

    tester.startGroup("Simple round trip of various bad XML (as strings)")
    count = 1
    for string in VARIOUS_STRINGS_BAD:
        test_one_str(count, string, 1)
        count += 1
    tester.groupDone()


    tester.startGroup("Simple round trip of various bad XML (as files)")
    count = 1
    for uri in VARIOUS_FILES_BAD:
        test_one_uri(count, uri, 1)
        count += 1
    tester.groupDone()
    return


XML10_PREFIX_UNDECL = """<?xml version="1.0"?>
<docelem xmlns:pfx=""/>
"""

XML11_PREFIX_UNDECL = """<?xml version="1.1"?>
<docelem xmlns:pfx=""/>
"""


SMALL_XML = """<?xml version = "1.0"?>
<?xml-stylesheet href="addr_book1.xsl" type="text/xml"?>
<docelem xmlns:ft='http://fourthought.com'>
  <child foo='bar'>Some Text</child>
  <!--A comment-->
  <ft:nschild ft:foo='nsbar'>Some More Text</ft:nschild>
  <appendChild/>
</docelem>
"""


LARGE_XML="""<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="../../style/function.use-cases.xsl"?>
<!-- <!DOCTYPE exslt:function SYSTEM 'function.dtd'> -->
<exslt:function xmlns:exslt="http://exslt.org/documentation"
                version="1" module="math" status="new">

<exslt:name>min</exslt:name>

<rdf:Description xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
                 xmlns:dc="http://purl.org/dc/elements/1.1/"
                 ID="math:min">
   <dc:subject>EXSLT</dc:subject>
   <dc:subject>math</dc:subject>
   <dc:subject>min</dc:subject>
   <dc:subject>minimum</dc:subject>
   <dc:rights>public domain</dc:rights>
   <exslt:revision>
      <rdf:Description xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
                       xmlns:dc="http://purl.org/dc/elements/1.1/"
                       ID="math:min.1">
         <exslt:version>1</exslt:version>
         <dc:creator email="mail@jenitennison.com"
                     url="http://www.jenitennison.com">Jeni Tennison</dc:creator>
         <dc:date>2001-03-28</dc:date>
         <dc:description>Returns the minimum value from a node-set.</dc:description>
      </rdf:Description>
   </exslt:revision>
</rdf:Description>

<exslt:doc xmlns="">
   <section>
      <para>
         The <function>math:min</function> function returns the minimum, for each node in the argument node-set, of the result of converting the string-values of the node to a number using the <ulink URL='http://www.w3.org/TR/xpath#function-number'> <function>number</function></ulink> function.  The numbers are compared as with the <literal>&lt;</literal> operator.  If the node set is empty, <returnvalue>NaN</returnvalue> is returned.
      </para>
      <para>
         The <literal>math:min</literal> template returns a result tree fragment whose string value is the result of turning the number returned by the function into a string.
      </para>
   </section>
</exslt:doc>

<exslt:definition>
   <exslt:return type="number" />
   <exslt:arg name="nodes" type="node-set" default="/.." />
</exslt:definition>

<exslt:implementations>
   <exslt:implementation src="math.min.function.xsl" language="exslt:exslt"
                         version="1" />
   <exslt:implementation src="math.min.template.xsl" language="exslt:xslt"
                         version="1" />
   <exslt:implementation src="math.min.js" language="javascript"
                         version="1" />
</exslt:implementations>

<exslt:use-cases>
   <exslt:use-case type="example" data="math.min.data.1.xml"
                   xslt="math.min.1.xsl" result="math.min.result.1.xml" />
   <exslt:use-case type="example" template="yes" data="math.min.data.1.xml"
                   xslt="math.min.2.xsl" result="math.min.result.1.xml" />
   <exslt:use-case type="boundary" data="math.min.data.2.xml"
                   xslt="math.min.1.xsl" result="math.min.result.2.xml" />
   <exslt:use-case type="boundary" template="yes" data="math.min.data.2.xml"
                   xslt="math.min.2.xsl" result="math.min.result.2.xml" />
   <exslt:use-case type="error" data="math.min.data.1.xml"
                   xslt="math.min.3.xsl">
      <exslt:doc xmlns="">
         <para>
            This use case shows an error when the function is passed a
            number as the value of the first argument.
         </para>
      </exslt:doc>
   </exslt:use-case>
   <exslt:use-case type="error" template="yes" data="math.min.data.1.xml"
                   xslt="math.min.4.xsl">
      <exslt:doc>
         <para>
            This use case shows an error when the function is passed a
            number as the value of the <parameter>nodes</parameter>
            parameter.
         </para>
      </exslt:doc>
   </exslt:use-case>
</exslt:use-cases>

</exslt:function>"""


GREETING = """<?xml version = "1.0"?>
<!DOCTYPE greeting SYSTEM "greeting.dtd">
<greeting>&bar;</greeting>
"""


JGREETING_UNICODE = u"""<?xml version="1.0" encoding="%s"?>
<greeting xml:lang="ja">\u4eca\u65e5\u306f</greeting>"""

JGREETING_ESCAPED = u"""<?xml version="1.0" encoding="%s"?>
<greeting lang="ja">&#20170;&#26085;&#12399;</greeting>"""


ADDRBOOK = """<?xml version = "1.0"?>
<!DOCTYPE ADDRBOOK SYSTEM "addr_book.dtd">
<ADDRBOOK>
    <ENTRY ID="pa">
        <NAME>Pieter Aaron</NAME>
        <ADDRESS>404 Error Way</ADDRESS>
        <PHONENUM DESC="Work">404-555-1234</PHONENUM>
        <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
        <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
        <EMAIL>pieter.aaron@inter.net</EMAIL>
    </ENTRY>
    <ENTRY ID="en">
        <NAME>Emeka Ndubuisi</NAME>
        <ADDRESS>42 Spam Blvd</ADDRESS>
        <PHONENUM DESC="Work">767-555-7676</PHONENUM>
        <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
        <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
        <EMAIL>endubuisi@spamtron.com</EMAIL>
    </ENTRY>
    <ENTRY ID="vz">
        <NAME>Vasia Zhugenev</NAME>
        <ADDRESS>2000 Disaster Plaza</ADDRESS>
        <PHONENUM DESC="Work">000-987-6543</PHONENUM>
        <PHONENUM DESC="Cell">000-000-0000</PHONENUM>
        <EMAIL>vxz@magog.ru</EMAIL>
    </ENTRY>
</ADDRBOOK>"""


ADDRBOOK_INVALID = """<?xml version = "1.0"?>
<!DOCTYPE ADDRBOOK SYSTEM "addr_book.dtd">
<ADDRBOOK>
    <INVALIDENTRY ID="pa">
        <NAME>Pieter Aaron</NAME>
        <ADDRESS>404 Error Way</ADDRESS>
        <PHONENUM DESC="Work">404-555-1234</PHONENUM>
        <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
        <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
        <EMAIL>pieter.aaron@inter.net</EMAIL>
    </INVALIDENTRY>
</ADDRBOOK>"""


INVALID_EMPTY = """<?xml version="1.0"?>
<!DOCTYPE doc [
<!ELEMENT doc EMPTY>
<doc> </doc>
"""

XML_SPACE_DECL = """<?xml version="1.0"?>
<!DOCTYPE doc [
<!ELEMENT doc EMPTY>
<!ATTLIST doc
  xml:space CDATA "preserve"
>
]>
<doc/>
"""

XML_SPACE_VALUES = """<?xml version="1.0"?>
<!DOCTYPE doc [
<!ELEMENT doc EMPTY>
<!ATTLIST doc
  xml:space (default|preserve|bogus) "preserve"
>
]>
<doc/>
"""

XML_SPACE_VALID = """<?xml version="1.0"?>
<!DOCTYPE doc [
<!ELEMENT doc EMPTY>
<!ATTLIST doc
  xml:space (default) "default"
>
]>
<doc/>
"""


BASE_TEST = """<?xml version = "1.0"?>
<spam>
  <eggs xml:base="http://fourthought.com">
    <monty python="nicht">knight</monty>
    <foo xml:base="http://4suite.org" bar="baz">foobar
      <all xml:base="your-base">are ... what?</all>
    </foo>
  </eggs>
</spam>
"""

VARIOUS_STRINGS = [
"""<?xml version="1.0"?>
<!DOCTYPE foo SYSTEM "various_strings_1.dtd">
<foo prefix:bar='' xmlns:prefix='http://spam.org'><prefix:bar/></foo>""",
]

VARIOUS_STRINGS_BAD = [
#XML well-formed but not XMLNS well-formed
"""<?xml version="1.0"?>
<!DOCTYPE foo SYSTEM "various_strings_1.dtd">
<foo undeclared-prefix:bar=''><undeclared-prefix:bar/></foo>""",

# Duplicate attributes
"""<?xml version="1.0" encoding="UTF-8"?>
<vote county="Palm Beach"
      count="23725"
      count="31563"
/>""",

# Duplicate prefixed attributes
"""<?xml version="1.0" encoding="UTF-8"?>
<vote county="Palm Beach"
      r:count="23725"
      d:count="31563"
      dem:count="23293"
      xmlns:dem="http://www.democrat.org/"
      xmlns:d="http://www.democrat.org/"
      xmlns:r="http://www.republican.org/"
/>""",
]

#Place stuff that cannot be in Python files as separate files listed here
VARIOUS_FILES = [
]

VARIOUS_FILES_BAD = [
]
