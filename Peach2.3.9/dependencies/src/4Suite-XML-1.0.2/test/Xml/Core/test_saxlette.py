import os
from xml.sax import make_parser, SAXException, SAXParseException
from xml.sax.handler import property_lexical_handler
from xml.sax.handler import property_declaration_handler
from xml.sax.xmlreader import XMLReader
from xml.sax.saxutils import prepare_input_source

from Ft.Lib import Uri
from Ft.Xml.Domlette import NonvalParse, Print
from Ft.Xml.InputSource import DefaultFactory
from Ft.Xml.Sax import CreateParser, DomBuilder
from Ft.Xml.Lib import TreeCompare

### Parser Creation ####################################################

def test_make_parser(tester):
    tester.startTest("Ft.Xml.Sax.CreateParser")
    try:
        parser = CreateParser()
    except:
        tester.error("parser not available")
    tester.testDone()

    tester.startTest("xml.sax.make_parser")
    try:
        parser = make_parser(['Ft.Xml.Sax'])
    except:
        tester.error("parser not available")
    tester.compare("Ft.Xml.cDomlette", parser.__class__.__module__,
                   "wrong module")
    tester.compare("Parser", parser.__class__.__name__,
                   "wrong class")
    tester.testDone()
    return

### DomBuilder #########################################################

def compare_builder(expected, builder):
    isrc = DefaultFactory.fromString(expected, "urn:test:expected")
    expected = NonvalParse(isrc)
    return not TreeCompare.NodeCompare(expected, builder.getDocument())

def test_builder_basic(tester):
    tester.startTest("Element")
    builder = DomBuilder()
    builder.startDocument()
    builder.startElementNS((None, u'doc'), u'doc', {})
    builder.endElementNS((None, u'doc'), u'doc')
    builder.endDocument()
    tester.compare("<doc/>", builder, func=compare_builder)
    tester.testDone()
    return

def test_builder_content(tester):
    tester.startTest("Element with content")
    builder = DomBuilder()
    builder.startDocument()
    builder.startElementNS((None, u'doc'), u'doc', {})
    builder.characters(u'huhei')
    builder.endElementNS((None, u'doc'), u'doc')
    builder.endDocument()
    tester.compare("<doc>huhei</doc>", builder, func=compare_builder)
    tester.testDone()
    return

TEST_NAMESPACE = u'http://4suite.org/sax/test'

def test_builder_ns(tester):
    tester.startTest("Namespaces")
    builder = DomBuilder()
    builder.startDocument()
    builder.startPrefixMapping(u'ns1', TEST_NAMESPACE)
    builder.startElementNS((TEST_NAMESPACE, u'doc'), u'ns1:doc', {})
    builder.startElementNS((None, u'udoc'), u'udoc', {})
    builder.endElementNS((None, u'udoc'), u'udoc')
    builder.endElementNS((TEST_NAMESPACE, u'doc'), u'ns1:doc')
    builder.endPrefixMapping(u'ns1')
    builder.endDocument()
    source = "<ns1:doc xmlns:ns1='%s'><udoc/></ns1:doc>" % str(TEST_NAMESPACE)
    tester.compare(source, builder, func=compare_builder)
    tester.testDone()
    return

def test_dom_builder(tester):
    tester.startGroup("DomBuilder")
    test_builder_basic(tester)
    test_builder_content(tester)
    test_builder_ns(tester)
    tester.groupDone()
    return

### XMLReader Interface ################################################

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_PATH = os.path.join(BASE_PATH, 'data.xml')
CONTENT_URI = Uri.OsPathToUri(CONTENT_PATH)

f = open(CONTENT_PATH)
try:
    XMLREADER_CONTENT = f.read()
finally:
    f.close()
    del f

def test_xmlreader_sax(tester):
    tester.startTest("SAX InputSource")
    parser = CreateParser()
    builder = DomBuilder()
    parser.setContentHandler(builder)
    parser.parse(prepare_input_source(CONTENT_PATH))
    tester.compare(XMLREADER_CONTENT, builder, func=compare_builder)
    tester.testDone()
    return

def test_xmlreader_sysid(tester):
    tester.startTest("System ID")
    parser = CreateParser()
    builder = DomBuilder()
    parser.setContentHandler(builder)
    parser.parse(CONTENT_URI)
    tester.compare(XMLREADER_CONTENT, builder, func=compare_builder)
    tester.testDone()
    return

def test_xmlreader_ft(tester):
    tester.startTest("4Suite InputSource")
    parser = CreateParser()
    builder = DomBuilder()
    parser.setContentHandler(builder)
    parser.parse(DefaultFactory.fromUri(CONTENT_URI))
    tester.compare(XMLREADER_CONTENT, builder, func=compare_builder)
    tester.testDone()
    return

def test_xmlreader_file(tester):
    tester.startTest("file-like object")
    parser = CreateParser()
    builder = DomBuilder()
    parser.setContentHandler(builder)
    parser.parse(open(CONTENT_PATH))
    tester.compare(XMLREADER_CONTENT, builder, func=compare_builder)
    tester.testDone()
    return

def test_xmlreader(tester):
    tester.startGroup("XMLReader")
    test_xmlreader_sax(tester)
    test_xmlreader_sysid(tester)
    test_xmlreader_ft(tester)
    test_xmlreader_file(tester)
    tester.groupDone()
    return

### DTDHandler Interface ###############################################

DTD_CONTENT = """<!DOCTYPE doc [
<!-- DTDHandler -->
<!NOTATION GIF PUBLIC
  "-//CompuServe//NOTATION Graphics Interchange Format 89a//EN">
<!ENTITY img SYSTEM "expat.gif" NDATA GIF>
<!-- DeclHandler -->
<!ELEMENT doc (#PCDATA | e)*>
<!ELEMENT e EMPTY>
<!ATTLIST e
  id   ID     #REQUIRED
  a1   CDATA  #IMPLIED
  enum ( v1 | v2 ) "v1"
>
<!ENTITY e1 "e1">
<!ENTITY % e2 "e2">
<!ENTITY e3 SYSTEM "entity.ent">
]>
<doc><!--LexicalHandler--><![CDATA[cdata]]></doc>
"""

class LexicalHandler:

    def __init__(self):
        self.events = []
        self.comments = []

    def startDTD(self, name, publicId, systemId):
        self.events.append(('startDTD', (name, publicId, systemId)))

    def endDTD(self):
        self.events.append(('endDTD', ()))

    def startCDATA(self):
        self.events.append(('startCDATA', ()))

    def endCDATA(self):
        self.events.append(('endCDATA', ()))

    def comment(self, data):
        self.comments.append(data)

class DTDHandler:

    def __init__(self):
        self.notations = []
        self.entities = []

    def notationDecl(self, name, publicId, systemId):
        self.notations.append((name, publicId, systemId))

    def unparsedEntityDecl(self, name, publicId, systemId, notationName):
        self.entities.append((name, publicId, systemId, notationName))

class DeclHandler:

    def __init__(self):
        self.elements = []
        self.attributes = []
        self.entities = []

    def elementDecl(self, name, model):
        self.elements.append((name, model))

    def attributeDecl(self, eName, aName, type, decl, value):
        self.attributes.append((eName, aName, type, decl, value))

    def internalEntityDecl(self, name, value):
        self.entities.append((name, value))

    def externalEntityDecl(self, name, publicId, systemId):
        self.entities.append((name, publicId, systemId))

def test_lexical_handler(tester):
    tester.startTest("LexicalHandler")
    parser = CreateParser()
    handler = LexicalHandler()
    parser.setProperty(property_lexical_handler, handler)

    parser.parse(DefaultFactory.fromString(DTD_CONTENT, "file:source"))
    
    events = [('startDTD', (u'doc', None, None)),
              ('endDTD', ()),
              ('startCDATA', ()),
              ('endCDATA', ()),
              ]
    comments = [u'LexicalHandler']
    tester.compare(events, handler.events, "events")
    tester.compare(comments, handler.comments, "comments")
    tester.testDone()

def test_dtd_handler(tester):
    tester.startTest("DTDHandler")
    parser = CreateParser()
    dtdhandler = DTDHandler()
    parser.setDTDHandler(dtdhandler)

    parser.parse(DefaultFactory.fromString(DTD_CONTENT, "file:source"))
    
    notations = [
        (u'GIF',
         u'-//CompuServe//NOTATION Graphics Interchange Format 89a//EN',
         None),
        ]
    entities = [
        (u'img', None, u'file:expat.gif', u'GIF'),
        ]
    tester.compare(notations, dtdhandler.notations, "notations")
    tester.compare(entities, dtdhandler.entities, "unparsed entities")
    tester.testDone()

def test_decl_handler(tester):
    tester.startTest("DTDHandler")
    parser = CreateParser()
    handler = DeclHandler()
    parser.setProperty(property_declaration_handler, handler)

    parser.parse(DefaultFactory.fromString(DTD_CONTENT, "file:source"))
    
    elements = [
        (u'doc', u'(#PCDATA|e)*'),
        (u'e', u'EMPTY'),
        ]
    attributes = [
        (u'e', u'id', u'ID', u'#REQUIRED', None),
        (u'e', u'a1', u'CDATA', u'#IMPLIED', None),
        (u'e', u'enum', u'(v1|v2)', None, u'v1'),
        ]
    entities = [
        (u'e1', u'e1'),
        (u'%e2', u'e2'),
        (u'e3', None, u'file:entity.ent'),
        ]
    tester.compare(elements, handler.elements, "element decls")
    tester.compare(attributes, handler.attributes, "attribute decls")
    tester.compare(entities, handler.entities, "entity decls")
    tester.testDone()

def test_dtd(tester):
    tester.startGroup("DTD Declarations")
    test_lexical_handler(tester)
    test_dtd_handler(tester)
    test_decl_handler(tester)
    tester.groupDone()
    return

### Attributes Interface ###############################################

class AttributesGatherer:

    _attrs = None
    
    def startElementNS(self, eName, qName, attrs):
        self._attrs = attrs
        return

def test_attrs_empty(tester):
    tester.startTest("Empty")
    parser = CreateParser()
    gatherer = AttributesGatherer()
    parser.setContentHandler(gatherer)

    content = "<doc/>"
    
    parser.parse(DefaultFactory.fromString(content, "urn:test:source"))
    attrs = gatherer._attrs
    name = (TEST_NAMESPACE, "attr")
    try:
        attrs.getValue(name)
    except KeyError:
        pass
    else:
        tester.error("getValue")
    try:
        attrs[name]
    except KeyError:
        pass
    else:
        tester.error("__getitem__")
    try:
        attrs.getQNameByName(name)
    except KeyError:
        pass
    else:
        tester.error("getQNameByName")
    tester.compare(0, len(attrs), "__len__")
    tester.compare(False, name in attrs, "__contains__")
    tester.compare(False, attrs.has_key(name), "has_key")
    tester.compare(None, attrs.get(name), "get")
    tester.compare(25, attrs.get(name, 25), "get")
    tester.compare([], attrs.keys(), "keys")
    tester.compare([], attrs.items(), "items")
    tester.compare([], attrs.values(), "values")
    tester.testDone()
    return

def test_attrs_specified(tester):
    tester.startTest("Specified")
    parser = CreateParser()
    gatherer = AttributesGatherer()
    parser.setContentHandler(gatherer)

    content = "<doc xmlns:ns='%s' ns:attr='val'/>" % str(TEST_NAMESPACE)
    
    parser.parse(DefaultFactory.fromString(content, "urn:test:source"))
    attrs = gatherer._attrs
    name = (TEST_NAMESPACE, "attr")
    tester.compare(u"val", attrs.getValue(name), "getValue")
    tester.compare(u"val", attrs[name], "__getitem__")
    tester.compare(u"ns:attr", attrs.getQNameByName(name), "getQNameByName")
    tester.compare(1, len(attrs), "__len__")
    tester.compare(True, name in attrs, "__contains__")
    tester.compare(True, attrs.has_key(name), "has_key")
    tester.compare(u"val", attrs.get(name), "get")
    tester.compare(u"val", attrs.get(name, 25), "get")
    tester.compare([name], attrs.keys(), "keys")
    tester.compare([(name, u"val")], attrs.items(), "items")
    tester.compare([u"val"], attrs.values(), "values")
    tester.testDone()
    return

def test_attributes(tester):
    tester.startGroup("Attributes")
    test_attrs_empty(tester)
    test_attrs_specified(tester)
    tester.groupDone()
    return

### Locator Interface ##################################################

class LocatorTester:

    def __init__(self, tester, sysid=CONTENT_URI):
        self._tester = tester
        self._sysid = sysid

    def setDocumentLocator(self, locator):
        self._locator = locator
        return

    def endDocument(self):
        tester = self._tester
        locator = self._locator
        tester.compare(self._sysid, locator.getSystemId(), "getSystemId")
        tester.compare(4, locator.getLineNumber(), "getLineNumber")
        tester.compare(7, locator.getColumnNumber(), "getColumnNumber")
        return

def verify_finished_locator(tester, locator):
    tester.compare(None, locator.getSystemId(), "getSystemId")
    tester.compare(-1, locator.getLineNumber(), "getLineNumber")
    tester.compare(-1, locator.getColumnNumber(), "getColumnNumber")
    return
    
def test_locator_sax(tester):
    tester.startTest("SAX InputSource")
    parser = CreateParser()
    parser.setContentHandler(LocatorTester(tester, CONTENT_PATH))
    parser.parse(prepare_input_source(CONTENT_PATH))
    verify_finished_locator(tester, parser)
    tester.testDone()
    return

def test_locator_sysid(tester):
    tester.startTest("System ID")
    parser = CreateParser()
    parser.setContentHandler(LocatorTester(tester))
    parser.parse(CONTENT_URI)
    verify_finished_locator(tester, parser)
    tester.testDone()
    return

def test_locator_ft(tester):
    tester.startTest("4Suite InputSource")
    parser = CreateParser()
    parser.setContentHandler(LocatorTester(tester))
    parser.parse(DefaultFactory.fromUri(CONTENT_URI))
    verify_finished_locator(tester, parser)
    tester.testDone()
    return

def test_locator(tester):
    tester.startGroup("Locator")
    test_locator_sax(tester)
    test_locator_sysid(tester)
    test_locator_ft(tester)
    tester.groupDone()
    return

### Error Reporting ####################################################

def test_errors_incomplete(tester):
    tester.startTest("Incomplete Parsing")
    parser = CreateParser()
    content = "<foo>"
    uri = "urn:test:source"
    try:
        parser.parse(DefaultFactory.fromString(content, uri))
    except SAXParseException, e:
        pass
    else:
        tester.error("SAXParseException not raised")
    tester.testDone()
    return
    
def test_errors_location(tester):
    tester.startTest("Location")
    parser = CreateParser()
    content = "<foo bar foorbar>"
    uri = "urn:test:source"
    try:
        parser.parse(DefaultFactory.fromString(content, uri))
    except SAXParseException, e:
        tester.compare(uri, e.getSystemId())
    else:
        tester.error("SAXParseException not raised")
    tester.testDone()
    return
    
def test_errors(tester):
    tester.startGroup("Errors")
    test_errors_incomplete(tester)
    #test_errors_location(tester)
    tester.groupDone()
    return


### Main ###############################################################

def Test(tester):
    test_make_parser(tester)
    test_dom_builder(tester)
    test_xmlreader(tester)
    test_dtd(tester)
    test_attributes(tester)
    test_locator(tester)
    test_errors(tester)
    return
