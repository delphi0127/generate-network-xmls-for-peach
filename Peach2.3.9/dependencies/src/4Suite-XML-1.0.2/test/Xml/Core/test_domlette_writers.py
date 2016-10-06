import cStringIO
from Ft.Xml import EMPTY_NAMESPACE
from Ft.Xml.Domlette import Print, PrettyPrint

doctype_expected_1 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo PUBLIC "myPub" "mySys">
<foo/>"""

JABBERWOCKY = """One, two! One, two! And through and through
  The vorpal blade went snicker-snack!
He left it dead, and with its head
  He went galumphing back."""

# as XML, with Print
xhtml_expected_1 = """<?xml version="1.0" encoding="UTF-8"?>\n<html><head><title>test</title></head><body><h1>xhtml test</h1><hr noshade="noshade"/><pre>%s</pre></body></html>""" % JABBERWOCKY

# as HTML, with Print
xhtml_expected_2 = """<html><head><title>test</title></head><body><h1>xhtml test</h1><hr noshade><pre>%s</pre></body></html>""" % JABBERWOCKY

# as XML, with PrettyPrint
xhtml_expected_3 = """<?xml version="1.0" encoding="UTF-8"?>
<html>
  <head>
    <title>test</title>
  </head>
  <body>
    <h1>xhtml test</h1>
    <hr noshade="noshade"/>
    <pre>%s</pre>
  </body>
</html>
""" % JABBERWOCKY

# as HTML, with PrettyPrint
xhtml_expected_4 = """<html>
  <head>
    <title>test</title>
  </head>
  <body>
    <h1>xhtml test</h1>
    <hr noshade>
    <pre>%s</pre>
  </body>
</html>
""" % JABBERWOCKY


def test_writer(tester, domMod):
    tester.startGroup('Domlette serialization')

    tester.startTest('minimal document with DOCTYPE')
    doc = domMod.implementation.createDocument(EMPTY_NAMESPACE, u'foo', None)
    doc.publicId = u'myPub'
    doc.systemId = u'mySys'
    buf = cStringIO.StringIO()
    Print(doc, buf)
    result = buf.getvalue()
    tester.compare(doctype_expected_1, result)
    tester.testDone()

    tester.startGroup('namespace-free XHTML')
    tester.startTest('create document')
    doc = domMod.implementation.createDocument(EMPTY_NAMESPACE, None, None)
    html = doc.createElementNS(EMPTY_NAMESPACE, u'html')
    head = doc.createElementNS(EMPTY_NAMESPACE, u'head')
    title = doc.createElementNS(EMPTY_NAMESPACE, u'title')
    titletext = doc.createTextNode(u'test')
    body = doc.createElementNS(EMPTY_NAMESPACE, u'body')
    h1 = doc.createElementNS(EMPTY_NAMESPACE, u'h1')
    h1text = doc.createTextNode(u'xhtml test')
    hr = doc.createElementNS(EMPTY_NAMESPACE, u'hr')
    hr.setAttributeNS(EMPTY_NAMESPACE, u'noshade', u'noshade')
    pre = doc.createElementNS(EMPTY_NAMESPACE, u'pre')
    pretext= doc.createTextNode(JABBERWOCKY)
    pre.appendChild(pretext)
    h1.appendChild(h1text)
    body.appendChild(h1)
    body.appendChild(hr)
    body.appendChild(pre)
    title.appendChild(titletext)
    head.appendChild(title)
    html.appendChild(head)
    html.appendChild(body)
    doc.appendChild(html)
    tester.testDone()

    tester.startTest('as XML with Print')
    buf = cStringIO.StringIO()
    Print(doc, buf)
    result = buf.getvalue()
    tester.compare(xhtml_expected_1, result)
    tester.testDone()

    tester.startTest('as HTML with Print')
    buf = cStringIO.StringIO()
    Print(doc, buf, asHtml=1)
    result = buf.getvalue()
    tester.compare(xhtml_expected_2, result)
    tester.testDone()

    tester.startTest('as XML with PrettyPrint')
    buf = cStringIO.StringIO()
    PrettyPrint(doc, buf)
    result = buf.getvalue()
    tester.compare(xhtml_expected_3, result)
    tester.testDone()

    tester.startTest('as HTML with PrettyPrint')
    buf = cStringIO.StringIO()
    PrettyPrint(doc, buf, asHtml=1)
    result = buf.getvalue()
    tester.compare(xhtml_expected_4, result)
    tester.testDone()

    tester.groupDone()

    tester.groupDone()
    return
