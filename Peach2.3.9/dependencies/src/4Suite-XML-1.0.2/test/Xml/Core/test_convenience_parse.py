from Ft.Xml import Parse
from Ft.Lib import Uri, Uuid
from xml.dom import Node
import os

#More in-depth testing of DOM structure building is done in other tests.
#Just checking the API for now

TEST_STRING = "<test/>"
TEST_FILE = "Xml/Core/disclaimer.xml"
TEST_URL = "http://cvs.4suite.org/viewcvs/*checkout*/4Suite/test/Xml/Core/disclaimer.xml"


def Test(tester):
    tester.startGroup("Convenience parse functions, part 1")

    tester.startTest("Parse with string")
    doc = Parse(TEST_STRING)
    #Minimal node testing
    tester.compare(len(doc.childNodes), 1)
    tester.compare(doc.childNodes[0].nodeType, Node.ELEMENT_NODE)
    tester.compare(doc.childNodes[0].nodeName, 'test')
    tester.compare(doc.childNodes[0].namespaceURI, None)
    tester.compare(doc.childNodes[0].prefix, None,)
    tester.testDone()

    tester.startTest("Parse with stream")
    
    stream = open(TEST_FILE)
    doc = Parse(stream)
    #Minimal node testing
    tester.compare(len(doc.childNodes), 1)
    tester.compare(doc.childNodes[0].nodeType, Node.ELEMENT_NODE)
    tester.compare(doc.childNodes[0].nodeName, 'disclaimer')
    tester.compare(doc.childNodes[0].namespaceURI, None)
    tester.compare(doc.childNodes[0].prefix, None,)
    tester.testDone()

    tester.startTest("Parse with file path")
    doc = Parse(TEST_FILE)
    #Minimal node testing
    tester.compare(len(doc.childNodes), 1)
    tester.compare(doc.childNodes[0].nodeType, Node.ELEMENT_NODE)
    tester.compare(doc.childNodes[0].nodeName, 'disclaimer')
    tester.compare(doc.childNodes[0].namespaceURI, None)
    tester.compare(doc.childNodes[0].prefix, None,)
    tester.testDone()
    tester.groupDone()

    if tester.offline:
        return

    # These tests require an active network connection.
    tester.startGroup("Convenience parse functions, part 2 (may be slow; requires Internet connection)")

    tester.startTest("Parse with URL")
    doc = Parse(TEST_URL)
    #Minimal node testing
    tester.compare(len(doc.childNodes), 1)
    tester.compare(doc.childNodes[0].nodeType, Node.ELEMENT_NODE)
    tester.compare(doc.childNodes[0].nodeName, 'disclaimer')
    tester.compare(doc.childNodes[0].namespaceURI, None)
    tester.compare(doc.childNodes[0].prefix, None,)
    tester.testDone()

    tester.groupDone()
    return
