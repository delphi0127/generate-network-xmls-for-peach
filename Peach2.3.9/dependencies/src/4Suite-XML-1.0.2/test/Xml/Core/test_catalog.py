import os, cStringIO

from Ft.Lib import Uri
from Ft.Xml import Domlette
from Ft.Xml.Catalog import Catalog
from Ft.Xml.InputSource import InputSourceFactory
from Ft.Xml.InputSource import DefaultFactory, NoCatalogFactory
from Ft.Xml.Lib.TreeCompare import TreeCompare

#def TestCatalog(tester, domMod):
#    tester.startGroup("Catalog test")
#    cat = Catalog(Uri.OsPathToUri('Xml/Core/xcatalog.xml', attemptAbsolute=1))
#    tester.startTest("XSA example")
#    isrc = cat.fromUri(Uri.OsPathToUri('Xml/Core/4suite.xsa', attemptAbsolute=1))
#    doc = domMod.ValParse(isrc)
#    stream = cStringIO.StringIO()
#    Domlette.Print(doc, stream)
#    #tester.compare(expected_1, stream.getvalue(), func=TreeCompare.TreeCompare)
#    #print stream.getvalue()
#    tester.testDone()
#    tester.groupDone()

XML_1 = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE foo [
  <!ENTITY sys SYSTEM "include1.xml">
  <!ENTITY pub PUBLIC "-//BOGUS//Include 1//EN//XML" "include1.xml">
  <!ENTITY badsys PUBLIC "-//BOGUS//Include 1//EN//XML" "DOES_NOT_EXIST.xml">
  <!ENTITY badpub PUBLIC "-//BOGUS//Include 99//EN//XML" "include1.xml">
]><test><sys>&sys;</sys><pub>&pub;</pub><badsys>&badsys;</badsys><badpub>&badpub;</badpub></test>"""

XML_EXPECTED_1 = """<?xml version="1.0" encoding="utf-8"?><test><sys>\n<foo/></sys><pub>\n<foo/></pub><badsys>\n<foo/></badsys><badpub>\n<foo/></badpub></test>"""


def Test(tester):
    tester.startGroup('XML and TR9401 Catalogs')
    tester.startTest('Parse an XML Catalog supplied via a URI')
    cat_path = os.path.join('Xml','Core','xcatalog.xml')
    cat_uri = Uri.OsPathToUri(cat_path, attemptAbsolute=1)
    cat = Catalog(cat_uri)
    tester.testDone()
    tf_path = os.path.join('Xml','Core','include1.xml')
    try:
        fd = open(tf_path)
        orig = fd.read()
        fd.close()
    except:
        fd.close()
        tester.warning('Could not read test file; skipping resolution tests.')
        return

    tester.startTest('Parse an XML Catalog supplied via an InputSource')
    fd = open(cat_path, 'rb')
    cat_data = fd.read()
    fd.close()
    isrc = NoCatalogFactory.fromString(cat_data, cat_uri)
    cat = Catalog()
    cat.isrc = isrc
    cat.parse()
    tester.testDone()

    # The catalog object should map 'urn:bogus:include1.xml' to
    # 'include1.xml' relative to the catalog's base URI.
    tester.startTest('Resolve a relative URI reference in the catalog (1)')
    expected = Uri.Absolutize('include1.xml', cat_uri)
    tester.compare(expected, cat.uris['urn:bogus:include1.xml'])
    tester.testDone()

    # The catalog object should map 'urn:bogus:include1-from-parent.xml'
    # to 'Core/include1.xml' relative to the catalog's base URI.
    tester.startTest('Resolve a relative URI reference in the catalog (2)')
    expected = Uri.Absolutize('Core/include1.xml', cat_uri)
    tester.compare(expected, cat.uris['urn:bogus:include1-from-parent.xml'])
    tester.testDone()

    # Same as above but we'll change the base URI of the catalog and
    # see if the results are still correct
    tester.startTest('Resolve a relative URI reference in the catalog (3)')
    alt_cat_path = os.path.join('Xml','xcatalog.xml')
    alt_cat_uri = Uri.OsPathToUri(alt_cat_path, attemptAbsolute=1)
    alt_cat_isrc = NoCatalogFactory.fromString(cat_data, alt_cat_uri)
    alt_cat = Catalog()
    alt_cat.isrc = alt_cat_isrc
    alt_cat.uri = alt_cat_uri
    alt_cat.parse()
    expected = Uri.Absolutize('Core/include1.xml', alt_cat_uri)
    tester.compare(expected, alt_cat.uris['urn:bogus:include1-from-parent.xml'])
    tester.testDone()

    # Make sure the default catalog exists and isn't empty
    tester.startTest('4Suite default catalog exists')
    from Ft.Xml.Catalog import FT_CATALOG
    entries = FT_CATALOG.publicIds or FT_CATALOG.uris
    tester.compare(True, len(entries) > 0)
    tester.testDone()

    # A test of catalog support in Ft.Xml.InputSource
    # (actually try to resolve a document URI with a catalog)
    tester.startTest('Resolve doc via InputSource w/Catalog containing rel. URI (1)')
    factory = InputSourceFactory(catalog=cat)
    isrc = factory.fromUri('urn:bogus:include1.xml')
    data = isrc.read()
    isrc.close()
    tester.compare(orig, data)
    tester.testDone()

    # A test of catalog support in Ft.Xml.InputSource
    # (same as previous, just with the different catalog base URI)
    tester.startTest('Resolve doc via InputSource w/Catalog containing rel. URI (2)')
    factory = InputSourceFactory(catalog=alt_cat)
    isrc = factory.fromUri('urn:bogus:include1-from-parent.xml')
    data = isrc.read()
    isrc.close()
    tester.compare(orig, data)
    tester.testDone()

    # A test of catalog support in Ft.Xml.InputSource
    # and resolving all combinations of Public and System IDs
    tester.startTest('Resolve ext. entities w/Catalog')
    xml_uri = Uri.Absolutize('test_catalog_INTERNAL.xml', cat_uri)
    factory = InputSourceFactory(catalog=cat)
    isrc = factory.fromString(XML_1, xml_uri)
    doc = Domlette.NonvalidatingReader.parse(isrc)
    st = cStringIO.StringIO()
    Domlette.Print(doc, stream=st)
    tester.compare(XML_EXPECTED_1, st.getvalue(), func=TreeCompare)
    tester.testDone()

    tester.groupDone()
    return
