import gc, weakref
from Ft.Xml import InputSource, Domlette

_refs = []

def StartNodeCounting():
    del _refs[:]

def GetNodeCount():
    return len(_refs)

class TestNode(Domlette.Node):
    def __init__(self, *args, **kwds):
        def callback(ref):
            try: _refs.remove(ref)
            except ValueError: pass
        _refs.append(weakref.ref(self, callback))

class TestDocument(Domlette.Document, TestNode):
    pass

class TestElement(Domlette.Element, TestNode):
    def setAttributeNS(self, namespaceURI, qualifiedName, value):
        attr = TestAttr(self.ownerDocument, namespaceURI, qualifiedName)
        self.setAttributeNodeNS(attr)
        attr.value = value
        return attr

class TestAttr(Domlette.Attr, TestNode):
    pass

class TestText(Domlette.Text, TestNode):
    pass

class TestProcessingInstruction(Domlette.ProcessingInstruction, TestNode):
    pass

class TestComment(Domlette.Comment, TestNode):
    pass

class TestDocumentFragment(Domlette.DocumentFragment, TestNode):
    pass

def test_empty_node(tester,domMod):
    tester.startTest("Empty Document")
    StartNodeCounting()
    doc = TestDocument()
    tester.compare(1, GetNodeCount())
    del doc
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Text")
    StartNodeCounting()
    doc = TestDocument()
    text = TestText(doc, "Foo")
    tester.compare(2, GetNodeCount())
    del text
    tester.compare(1, GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Element")
    StartNodeCounting()
    elem = TestElement(doc, None,"Foo")
    tester.compare(1, GetNodeCount())
    del elem
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Attribute")
    StartNodeCounting()
    attr = TestAttr(doc, None,"Foo")
    tester.compare(1, GetNodeCount())
    del attr
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Comment")
    StartNodeCounting()
    com = TestComment(doc, "Foo")
    tester.compare(1, GetNodeCount())
    del com
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Processing Instruction")
    StartNodeCounting()
    pi = TestProcessingInstruction(doc, "Foo", "Bar")
    tester.compare(1, GetNodeCount())
    del pi
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Document Fragment")
    StartNodeCounting()
    df = TestDocumentFragment(doc)
    tester.compare(1, GetNodeCount())
    del df
    tester.compare(0, GetNodeCount())
    tester.testDone()


def test_small_tree(tester,domMod):
    gc.collect()  #Force to clean everything up
    tester.startTest("Single Parent -> child rel")
    doc = TestDocument()
    StartNodeCounting()
    elem = TestElement(doc, None, "Foo")
    elem2 = TestElement(doc, None, "Foo2")
    elem.appendChild(elem2)
    tester.compare(2, GetNodeCount())
    del elem
    del elem2
    gc.collect() #Force collection
    tester.compare(0, GetNodeCount())
    del doc
    tester.testDone()

    tester.startTest("Document -> elem rel")
    StartNodeCounting()
    doc = TestDocument()
    elem = TestElement(doc, None, "Foo")
    doc.appendChild(elem)
    tester.compare(2, GetNodeCount())
    del doc
    del elem
    gc.collect() #Force collection
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Document -> text rel")
    StartNodeCounting()
    doc = TestDocument()
    text = TestText(doc, "Foo")
    doc.appendChild(text)
    tester.compare(2, GetNodeCount())
    del doc
    del text
    gc.collect() #Force collection
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Document -> pi rel")
    StartNodeCounting()
    doc = TestDocument()
    pi = TestProcessingInstruction(doc, "Foo", "Bar")
    doc.appendChild(pi)
    tester.compare(2, GetNodeCount())
    del doc
    del pi
    gc.collect() #Force collection
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Document -> comment rel")
    StartNodeCounting()
    doc = TestDocument()
    com = TestComment(doc, "Foo")
    doc.appendChild(com)
    tester.compare(2, GetNodeCount())
    del doc
    del com
    gc.collect() #Force collection
    tester.compare(0, GetNodeCount())
    tester.testDone()

def test_df_tree(tester,domMod):
    gc.collect()  #Force to clean everything up
    tester.startTest("Document Fragment Tree")
    doc = TestDocument()
    StartNodeCounting()
    df = TestDocumentFragment(doc)
    elem = TestElement(doc, None, "Foo")
    elem2 = TestElement(doc, None, "Foo2")
    df.appendChild(elem)
    df.appendChild(elem2)
    tester.compare(3, GetNodeCount())
    del elem
    del elem2
    del df
    gc.collect() #Force collection
    tester.compare(0, GetNodeCount())
    tester.testDone()


def test_attributes(tester,domMod):
    gc.collect()  #Force to clean everything up
    tester.startTest("Element with setAttributeNodeNS")
    doc = TestDocument()
    StartNodeCounting()
    elem = TestElement(doc, None, "Foo")
    attr = TestAttr(doc, None, "Foo")
    elem.setAttributeNodeNS(attr)
    tester.compare(2, GetNodeCount())
    del elem
    del attr
    gc.collect() #Force collection
    tester.compare(0, GetNodeCount())
    tester.testDone()

    tester.startTest("Element with setAttributeNS")
    doc = TestDocument()
    StartNodeCounting()
    elem = TestElement(doc, None, "Foo")
    elem.setAttributeNS(None, "Foo", "Bar")
    tester.compare(2, GetNodeCount())
    del elem
    gc.collect() #Force collection
    tester.compare(0, GetNodeCount())
    tester.testDone()

# -- cyclic garbage collection -----------------------------------------

def test_cycles(tester,domMod):
    tester.startGroup("Reclaiming of Cyclic Memory")
    test_empty_node(tester,domMod)
    test_small_tree(tester,domMod)
    test_df_tree(tester,domMod)
    test_attributes(tester,domMod)
    tester.groupDone()

# -- reference counts --------------------------------------------------

def TestRefCounts(tester, document):
    from sys import getrefcount
    def node_refcounts(node, expected):
        if isinstance(node, Domlette.Element):
            # test element's children
            for child in node:
                expected = node_refcounts(child, expected)
            # test element's attributes
            for attr in node.attributes.itervalues():
                expected = node_refcounts(attr, expected)
        # Reference count:
        #  +1 for getrefcount() argument
        #  +1 for node_refcounts() argument
        #  +1 for iterator binding
        #  +1 for outer binding
        #  +1 for local binding
        msg = node.__class__.__name__ + ' refcounts'
        tester.compare(5, getrefcount(node), msg)
        return expected + 1

    # Reference count:
    #  +1 for getrefcount() argument
    #  +1 for TestRefCounts() argument
    #  +1 for outer binding
    #  +1 for local binding
    expected = 4
    for node in document:
        expected = node_refcounts(node, expected)
    msg = document.__class__.__name__ + ' refcounts'
    tester.compare(expected, getrefcount(document), msg)
    return

def test_refcounts(tester,domMod):
    tester.startGroup("Low Level Ref Counts")

    tester.startTest("Empty Document")
    gc.collect()
    assert not gc.garbage, gc.garbage

    doc = TestDocument()
    TestRefCounts(tester, doc)
    del doc
    gc.collect()
    tester.compare(0, len(gc.garbage))
    tester.testDone()

    # Ensure that all local bindings are deleted except for 'doc', obviously.
    tester.startTest("Constructor Created Document")
    gc.collect()
    assert not gc.garbage

    doc = TestDocument()
    elem = TestElement(doc, 'http://foo.com', 'foo:root')
    doc.appendChild(elem)
    text = TestText(doc, "Data1")
    elem.appendChild(text)
    del text
    pi = TestProcessingInstruction(doc, "tar", "Data3")
    doc.insertBefore(pi, elem)
    del pi
    comment = TestComment(doc, "Data2")
    doc.appendChild(comment)
    del comment
    elem2 = TestElement(doc, 'http://foo2.com', 'foo2:child')
    elem2.setAttributeNS('http://foo2.com', 'foo2:attr', 'value')
    elem.appendChild(elem2)
    del elem2
    del elem
    TestRefCounts(tester, doc)
    del doc
    gc.collect()
    tester.compare(0, len(gc.garbage))
    tester.testDone()

    # Ensure that all local bindings are deleted except for 'doc', obviously.
    tester.startTest("DOM Created Document")
    gc.collect()
    assert not gc.garbage
    doc = domMod.implementation.createDocument(None, None, None)
    elem = doc.createElementNS('http://foo.com', 'foo:root')
    doc.appendChild(elem)
    text = doc.createTextNode("Data1")
    elem.appendChild(text)
    del text
    pi = doc.createProcessingInstruction("tar", "Data3")
    doc.insertBefore(pi, elem)
    del pi
    comment = doc.createComment("Data2")
    doc.appendChild(comment)
    del comment
    elem2 = doc.createElementNS('http://foo2.com', 'foo2:child')
    elem2.setAttributeNS('http://foo2.com', 'foo2:attr', 'value')
    elem.appendChild(elem2)
    del elem2
    del elem
    TestRefCounts(tester, doc)
    del doc
    gc.collect()
    tester.compare(0, len(gc.garbage))
    tester.testDone()

    from test_domlette_readers import SMALL_XML, LARGE_XML

    tester.startTest("Small parsed XML")
    isrc = InputSource.DefaultFactory.fromString(SMALL_XML, 'mem')
    gc.collect()
    assert not gc.garbage
    doc = domMod.NonvalParse(isrc)
    TestRefCounts(tester, doc)
    del doc
    gc.collect()
    tester.compare(0, len(gc.garbage))
    tester.testDone()

    tester.startTest("Large parsed XML")
    isrc = InputSource.DefaultFactory.fromString(LARGE_XML, 'mem')
    gc.collect()
    assert not gc.garbage
    doc = domMod.NonvalParse(isrc)
    TestRefCounts(tester, doc)
    del doc
    gc.collect()
    tester.compare(0, len(gc.garbage))
    tester.testDone()

    tester.startTest("Small parsed XML w/ mod")
    isrc = InputSource.DefaultFactory.fromString(SMALL_XML, 'mem')
    gc.collect()
    assert not gc.garbage
    doc = domMod.NonvalParse(isrc)
    for ctr in xrange(1000):
        doc.documentElement.setAttributeNS('http://foo.com', 'bar', 'baz')
    gc.collect()
    TestRefCounts(tester, doc)
    del doc
    gc.collect()
    tester.compare(0, len(gc.garbage))
    tester.testDone()

    tester.groupDone()
    return

# -- testing entry function --------------------------------------------

def test_memory(tester, domMod):
    tester.startGroup("Memory")
    flags = gc.get_debug()
    try:
        gc.set_debug(0)
        test_cycles(tester, domMod)
        test_refcounts(tester, domMod)
    finally:
        gc.set_debug(flags)
    tester.groupDone()
    return

