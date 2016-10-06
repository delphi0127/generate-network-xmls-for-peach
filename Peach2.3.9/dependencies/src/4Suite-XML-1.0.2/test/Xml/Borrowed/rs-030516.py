import cStringIO
from Ft.Xml.Domlette import Print, PrettyPrint, NonvalidatingReader


SRC1 = """\
<S:foo xmlns:S="http://example.com/1">
  <bar>test</bar>
  <bar xmlns="http://example.com/2">test2</bar>
  <S:bar xmlns:S="http://example.com/2">test2</S:bar>
</S:foo>
"""

EXPECTED1_PRINTED = """\
<?xml version="1.0" encoding="UTF-8"?>
<S:foo xmlns:S="http://example.com/1">
  <bar>test</bar>
  <bar xmlns="http://example.com/2">test2</bar>
  <S:bar xmlns:S="http://example.com/2">test2</S:bar>
</S:foo>"""

EXPECTED1_PRETTY = """\
<?xml version="1.0" encoding="UTF-8"?>
<S:foo xmlns:S="http://example.com/1">
  <bar>test</bar>
  <bar xmlns="http://example.com/2">test2</bar>
  <S:bar xmlns:S="http://example.com/2">test2</S:bar>
</S:foo>
"""


def Test(tester):
    tester.startGroup('Rich Salz reports default namespace munging')
    doc = NonvalidatingReader.parseString(SRC1, __name__)
    tester.startTest('Ft.Xml.Domlette.Print')
    stream = cStringIO.StringIO()
    Print(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED1_PRINTED, result)
    tester.testDone()
    tester.startTest('Ft.Xml.Domlette.PrettyPrint')
    stream = cStringIO.StringIO()
    PrettyPrint(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED1_PRETTY, result)
    tester.testDone()
    tester.groupDone()
    return

