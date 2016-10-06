import cStringIO
from Ft.Xml.Domlette import implementation, Print, PrettyPrint

EXPECTED1_PRINTED = """\
<?xml version="1.0" encoding="UTF-8"?>
<x:foo xmlns:x="http://example.com/1"><bar/></x:foo>"""

EXPECTED1_PRETTY = """\
<?xml version="1.0" encoding="UTF-8"?>
<x:foo xmlns:x="http://example.com/1">
  <bar/>
</x:foo>
"""

EXPECTED2_PRINTED = """\
<?xml version="1.0" encoding="UTF-8"?>
<foo xmlns="http://example.com/1"><bar xmlns=""/></foo>"""

EXPECTED2_PRETTY = """\
<?xml version="1.0" encoding="UTF-8"?>
<foo xmlns="http://example.com/1">
  <bar xmlns=""/>
</foo>
"""

EXPECTED3_PRINTED = """\
<?xml version="1.0" encoding="UTF-8"?>
<foo><bar xmlns="http://example.com/1"/></foo>"""

EXPECTED3_PRETTY = """\
<?xml version="1.0" encoding="UTF-8"?>
<foo>
  <bar xmlns="http://example.com/1"/>
</foo>
"""

EXPECTED4_PRINTED = """\
<?xml version="1.0" encoding="UTF-8"?>
<foo><bar xmlns="http://example.com/1"><baz xmlns=""/></bar></foo>"""

EXPECTED4_PRETTY = """\
<?xml version="1.0" encoding="UTF-8"?>
<foo>
  <bar xmlns="http://example.com/1">
    <baz xmlns=""/>
  </bar>
</foo>
"""


def Test(tester):
    tester.startGroup('Uche finds nested default namespace munging')
    doc = implementation.createDocument(None, None, None)
    elem1 = doc.createElementNS("http://example.com/1", "x:foo")
    doc.appendChild(elem1)
    elem2 = doc.createElementNS(None, "bar")
    elem1.appendChild(elem2)
    tester.startTest('Outer with prefix.  Print')
    stream = cStringIO.StringIO()
    Print(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED1_PRINTED, result)
    tester.testDone()
    tester.startTest('Outer with prefix.  PrettyPrint')
    stream = cStringIO.StringIO()
    PrettyPrint(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED1_PRETTY, result)
    tester.testDone()

    doc = implementation.createDocument(None, None, None)
    elem1 = doc.createElementNS("http://example.com/1", "foo")
    doc.appendChild(elem1)
    elem2 = doc.createElementNS(None, "bar")
    elem1.appendChild(elem2)
    tester.startTest('Outer without prefix.  Print')
    stream = cStringIO.StringIO()
    Print(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED2_PRINTED, result)
    tester.testDone()
    tester.startTest('Outer without prefix.  PrettyPrint')
    stream = cStringIO.StringIO()
    PrettyPrint(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED2_PRETTY, result)
    tester.testDone()

    doc = implementation.createDocument(None, None, None)
    elem1 = doc.createElementNS(None, "foo")
    doc.appendChild(elem1)
    elem2 = doc.createElementNS("http://example.com/1", "bar")
    elem1.appendChild(elem2)
    tester.startTest('outer no prefix or ns, inner ns no prefix.  Print')
    stream = cStringIO.StringIO()
    Print(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED3_PRINTED, result)
    tester.testDone()
    tester.startTest('outer no prefix or ns, inner ns no prefix.  PrettyPrint')
    stream = cStringIO.StringIO()
    PrettyPrint(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED3_PRETTY, result)
    tester.testDone()

    doc = implementation.createDocument(None, None, None)
    elem1 = doc.createElementNS(None, "foo")
    doc.appendChild(elem1)
    elem2 = doc.createElementNS("http://example.com/1", "bar")
    elem1.appendChild(elem2)
    elem3 = doc.createElementNS(None, "baz")
    elem2.appendChild(elem3)
    tester.startTest('outer no prefix or ns, then ns no prefix then no prefix no ns.  Print')
    stream = cStringIO.StringIO()
    Print(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED4_PRINTED, result)
    tester.testDone()
    tester.startTest('outer no prefix or ns, then ns no prefix then no prefix no ns.  PrettyPrint')
    stream = cStringIO.StringIO()
    PrettyPrint(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED4_PRETTY, result)
    tester.testDone()
    tester.groupDone()
    return


