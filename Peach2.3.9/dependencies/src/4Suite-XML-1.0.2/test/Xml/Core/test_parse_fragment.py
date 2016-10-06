from Ft.Xml import Parse, CreateInputSource
from Ft.Xml.Domlette import Print, EntityReader, GetAllNs, ParseFragment
from Ft.Lib import Uri, Uuid
from xml.dom import Node
import cStringIO, os

SOURCE1 = "<p>hello<b>world</b>.  How ya doin'?</p>"

EXPECTED1 = '<p>hello<b>world</b>.  How ya doin\'?</p>'

EXPECTED2 = '<p xmlns="http://www.w3.org/1999/xhtml">hello<b>world</b>.  How ya doin\'?</p>'

SOURCE2 = "<p>hello<b xmlns=''>world</b>.  How ya doin'?</p>"

EXPECTED3 = '<p xmlns="http://www.w3.org/1999/xhtml">hello<b xmlns="">world</b>.  How ya doin\'?</p>'

SOURCE3 = "<h:p xmlns:h='http://www.w3.org/1999/xhtml'>hello<h:b>world</h:b>.  How ya doin'?</h:p>"

EXPECTED4 = '<h:p xmlns:h="http://www.w3.org/1999/xhtml">hello<h:b>world</h:b>.  How ya doin\'?</h:p>'


def Test(tester):
    tester.startGroup("Fragment parse")

    tester.startTest("Plain parse")
    isrc = CreateInputSource(SOURCE1)
    doc = ParseFragment(isrc)
    stream = cStringIO.StringIO()
    Print(doc, stream)
    tester.compare(EXPECTED1, stream.getvalue())
    #Minimal node testing
    tester.compare(len(doc.childNodes), 1)
    tester.compare(doc.childNodes[0].nodeType, Node.ELEMENT_NODE)
    tester.compare(doc.childNodes[0].nodeName, u'p')
    tester.compare(doc.childNodes[0].namespaceURI, None)
    tester.compare(doc.childNodes[0].prefix, None,)
    tester.testDone()

    tester.startTest("Parse with overridden default namespace")
    nss = {u'xml': u'http://www.w3.org/XML/1998/namespace',
           None: u'http://www.w3.org/1999/xhtml'}
    isrc = CreateInputSource(SOURCE1)
    doc = ParseFragment(isrc, nss)
    stream = cStringIO.StringIO()
    Print(doc, stream)
    tester.compare(EXPECTED2, stream.getvalue())
    #doc = ParseFragment(TEST_STRING)
    #Minimal node testing
    tester.compare(len(doc.childNodes), 1)
    tester.compare(doc.childNodes[0].nodeType, Node.ELEMENT_NODE)
    tester.compare(doc.childNodes[0].nodeName, u'p')
    tester.compare(doc.childNodes[0].namespaceURI, u'http://www.w3.org/1999/xhtml')
    tester.compare(doc.childNodes[0].prefix, None,)
    tester.testDone()

    tester.startTest("Parse with overridden default namespace and re-overridden child")
    nss = {u'xml': u'http://www.w3.org/XML/1998/namespace',
           None: u'http://www.w3.org/1999/xhtml'}
    isrc = CreateInputSource(SOURCE2)
    doc = ParseFragment(isrc, nss)
    stream = cStringIO.StringIO()
    Print(doc, stream)
    tester.compare(EXPECTED3, stream.getvalue())
    #Minimal node testing
    tester.compare(len(doc.childNodes), 1)
    tester.compare(doc.childNodes[0].nodeType, Node.ELEMENT_NODE)
    tester.compare(doc.childNodes[0].nodeName, u'p')
    tester.compare(doc.childNodes[0].namespaceURI, u'http://www.w3.org/1999/xhtml')
    tester.compare(doc.childNodes[0].prefix, None,)
    tester.testDone()

    tester.startTest("Parse with overridden non-default namespace")
    nss = {u'xml': u'http://www.w3.org/XML/1998/namespace',
           u'h': u'http://www.w3.org/1999/xhtml'}
    isrc = CreateInputSource(SOURCE3)
    doc = ParseFragment(isrc, nss)
    stream = cStringIO.StringIO()
    Print(doc, stream)
    tester.compare(EXPECTED4, stream.getvalue())
    #doc = ParseFragment(TEST_STRING)
    #Minimal node testing
    tester.compare(len(doc.childNodes), 1)
    tester.compare(doc.childNodes[0].nodeType, Node.ELEMENT_NODE)
    tester.compare(doc.childNodes[0].nodeName, u'h:p')
    tester.compare(doc.childNodes[0].namespaceURI, u'http://www.w3.org/1999/xhtml')
    tester.compare(doc.childNodes[0].prefix, u'h')
    tester.testDone()

    tester.groupDone()
    return

