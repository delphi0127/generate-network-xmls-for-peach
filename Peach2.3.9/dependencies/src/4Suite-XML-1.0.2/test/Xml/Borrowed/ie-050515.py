import cStringIO
from Ft.Xml.Domlette import Print, PrettyPrint, NonvalidatingReader


SRC1 = """\
<cookie>
  <act:FlowViewLayout xmlns:act="urn:Actimize.FlowViewLayout">
  </act:FlowViewLayout>
</cookie>
"""

EXPECTED1_PRINTED = """\
<?xml version="1.0" encoding="UTF-8"?>
<cookie xmlns:act="urn:Actimize.FlowViewLayout">
  <act:FlowViewLayout>
  </act:FlowViewLayout>
</cookie>"""

#EXPECTED1_PRETTY = """\
#"""

def Test(tester):
    tester.startGroup('Idan Elfassy finds well-formedness bug in printer')
    doc = NonvalidatingReader.parseString(SRC1, __name__)
    tester.startTest('Ft.Xml.Domlette.Print')
    stream = cStringIO.StringIO()
    Print(doc, stream=stream)
    result = stream.getvalue()
    tester.compare(EXPECTED1_PRINTED, result)
    tester.testDone()
    tester.groupDone()
    return

