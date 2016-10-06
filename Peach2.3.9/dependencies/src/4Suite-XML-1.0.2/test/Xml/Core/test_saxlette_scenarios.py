from Ft.Xml import InputSource
from Ft.Xml import Domlette
from Ft.Xml import Sax

class element_counter:
    def startDocument(self):
        self.ecount = 0

    def startElementNS(self, name, qname, attribs):
        self.ecount += 1


DOC1 = """
<top>
  <x><leaf/></x>
  <y><leaf/></y>
  <z><leaf/></z>
</top>
"""


def test_basics(tester):
    tester.startGroup("Saxlette basics")

    tester.startTest("element counter demo handler")
    parser = Sax.CreateParser()
    handler = element_counter()
    parser.setContentHandler(handler)
    isrc = InputSource.DefaultFactory.fromString(DOC1, 'urn:bogus:x')
    parser.parse(isrc)
    tester.compare(handler.ecount, 7)
    tester.testDone()

    tester.groupDone()
    return


class container_state:
    def __init__(self, parser):
        self.parser = parser
        return
    
    def startDocument(self):
        self.current = None
        return

    def startElementNS(self, name, qname, attribs):
        if qname != u'leaf':
            self.current = qname
        return

    def endElementNS(self, name, qname):
        if qname == u'leaf':
            self.parser.setProperty(Sax.PROPERTY_YIELD_RESULT, self.current)
        return


def test_synchronicity(tester):
    tester.startGroup("Saxlette generator feature")

    tester.startTest("check generator synchronicity")
    parser = Sax.CreateParser()
    parser.setFeature(Sax.FEATURE_GENERATOR, True)
    handler = container_state(parser)
    parser.setContentHandler(handler)
    isrc = InputSource.DefaultFactory.fromString(DOC1, 'urn:bogus:x')
    generator = parser.parse(isrc)
    for item in generator:
        tester.compare(item, handler.current)
    tester.testDone()

    tester.groupDone()
    return


def Test(tester):
    test_basics(tester)
    test_synchronicity(tester)
    return


