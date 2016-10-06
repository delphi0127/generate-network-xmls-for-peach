import cStringIO, re
from Ft.Xml.Lib.HtmlPrettyPrinter import HtmlPrettyPrinter

# illegal chars should be replaced
ILLEGAL_XML_CHAR_PATTERN = re.compile(u'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\u10000-\u10FFFF]')
ILLEGAL_HTML_CHAR_PATTERN = re.compile(u'[^\x09\x0A\x0D\x20-\x7F\xA0-\uD7FF\uE000-\uFFFD\u10000-\u10FFFF]')
REPLACEMENT_CHAR = '?'
cdata_1 = [u'safe',
           u'null: \u0000',
           u'bell: \u0007',
           u'form feed: \u000c',
           u'next line: \u0085',
           u'non-BMP: \u10000',
          ]

# text content of elements should be indented predictably
hpp_expected_0 = """<test>
  <p id="1"></p>
  <p id="2"></p>
  <p id="3">hello</p>
  <p id="4">hello\nworld</p>
  <p id="5">
</p>
</test>"""

# text() output should be the same regardless of whether
# it is called many times in succession or just once
data_lists_1 = (
    [u'one\ntwo\nthree\n\n\nsix\n'],
    [u'one\n', u'two\n', u'three\n', u'\n', u'\n', u'six\n'],
    [u'one\ntwo\nthree\n', u'\n', u'\n', u'six\n'],
    [u'one', u'\ntwo', u'\nthree\n\n\n', u's', u'i', u'x', u'\n'],
    )

# blank lines are not indented
hpp_expected_1 = """<table>
  <tr>
    <td>one\ntwo\nthree\n\n\nsix\n</td>
  </tr>
</table>"""


def Test(tester):
    tester.startGroup('XmlPrinter')
    tester.startTest('replacement of illegal character data')
    for cdata in cdata_1:
        stream = cStringIO.StringIO()
        printer = HtmlPrettyPrinter(stream, 'utf-8')
        printer.startDocument()
        printer.startElement(None, u'test', {}, {})
        printer.text(cdata)
        printer.endElement(None, u'test')
        printer.endDocument()
        result = stream.getvalue()
        cdata = re.sub(ILLEGAL_XML_CHAR_PATTERN, REPLACEMENT_CHAR, cdata)
        expected = '<test>%s</test>' % cdata.encode('utf-8')
        tester.compare(expected, result)
    tester.testDone()
    tester.groupDone()

    tester.startGroup('XmlPrettyPrinter')
    tester.warning("not tested")
    tester.groupDone()

    tester.startGroup('HtmlPrinter')
    tester.startTest('replacement of illegal character data')
    for cdata in cdata_1:
        stream = cStringIO.StringIO()
        printer = HtmlPrettyPrinter(stream, 'utf-8')
        printer.startDocument()
        printer.startElement(None, u'test', {}, {})
        printer.text(cdata)
        printer.endElement(None, u'test')
        printer.endDocument()
        result = stream.getvalue()
        cdata = re.sub(ILLEGAL_HTML_CHAR_PATTERN, REPLACEMENT_CHAR, cdata)
        expected = '<test>%s</test>' % cdata.encode('utf-8')
        tester.compare(expected, result)
    tester.testDone()
    tester.groupDone()

    tester.startGroup('HtmlPrettyPrinter')

    tester.startTest('simple tests of text in elements')
    stream = cStringIO.StringIO()
    printer = HtmlPrettyPrinter(stream, 'us-ascii')
    printer.startDocument()
    printer.startElement(None, u'test', {}, {})
    printer.startElement(None, u'p', {}, {u'id': u'1'})
    printer.endElement(None, u'p')
    printer.startElement(None, u'p', {}, {u'id': u'2'})
    printer.text(u'')
    printer.endElement(None, u'p')
    printer.startElement(None, u'p', {}, {u'id': u'3'})
    printer.text(u'hello')
    printer.endElement(None, u'p')
    printer.startElement(None, u'p', {}, {u'id': u'4'})
    printer.text(u'hello\nworld')
    printer.endElement(None, u'p')
    printer.startElement(None, u'p', {}, {u'id': u'5'})
    printer.text(u'\n')
    printer.endElement(None, u'p')
    printer.endElement(None, u'test')
    printer.endDocument()
    result = stream.getvalue()
    tester.compare(hpp_expected_0, result)
    tester.testDone()

    tester.startTest('single vs successive text() calls')
    for datalist in data_lists_1:
        stream = cStringIO.StringIO()
        printer = HtmlPrettyPrinter(stream, 'us-ascii')
        printer.startDocument()
        printer.startElement(None, u'table',{},{})
        printer.startElement(None, u'tr',{},{})
        printer.startElement(None, u'td',{},{})
        for data in datalist:
            printer.text(data)
        printer.endElement(None, u'td')
        printer.endElement(None, u'tr')
        printer.endElement(None, u'table')
        printer.endDocument()
        result = stream.getvalue()
        tester.compare(hpp_expected_1, result)
    tester.testDone()

    tester.groupDone()
    return
