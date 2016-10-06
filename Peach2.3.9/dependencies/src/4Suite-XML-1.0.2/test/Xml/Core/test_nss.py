from Ft.Xml import InputSource
from Ft.Xml import Domlette

def test_get_all_ns(tester, module):
    tester.startGroup("GetAllNs")

    src_1 = """
<foo:bar xmlns:foo='http://foo.com'><baz:bar xmlns:baz='http://baz.com'/>
</foo:bar>
"""
    isrc = InputSource.DefaultFactory.fromString(src_1, "dummy")
    doc = module.NonvalParse(isrc)

    tester.startTest("Simple")
    node = doc.documentElement
    res = module.GetAllNs(node)
    tester.compare(2,len(res.keys()))
    tester.compare(1,res.has_key('xml'))
    tester.compare(1,res.has_key('foo'))
    tester.compare('http://foo.com',res['foo'])
    tester.compare('http://www.w3.org/XML/1998/namespace',res['xml'])
    tester.testDone()


    tester.startTest("Simple One Deep")
    node = doc.documentElement.firstChild
    res = module.GetAllNs(node)
    tester.compare(3,len(res.keys()))
    tester.compare(1,res.has_key('xml'))
    tester.compare(1,res.has_key('foo'))
    tester.compare(1,res.has_key('baz'))
    tester.compare('http://foo.com',res['foo'])
    tester.compare('http://baz.com',res['baz'])
    tester.compare('http://www.w3.org/XML/1998/namespace',res['xml'])
    tester.testDone()

    src_2 = """
<foo:bar xmlns='http://default.com'
         xmlns:foo='http://foo.com'
         xmlns:baz='http://baz.com'
/>"""
    isrc = InputSource.DefaultFactory.fromString(src_2, "dummy")
    doc = module.NonvalParse(isrc)

    tester.startTest("Unused xmlns declaration")
    node = doc.documentElement
    res = module.GetAllNs(node)
    tester.compare(4,len(res.keys()))
    tester.compare(1,res.has_key('xml'))
    tester.compare(1,res.has_key('foo'))
    tester.compare(1,res.has_key('baz'))
    tester.compare(1,res.has_key(None))
    tester.compare('http://foo.com',res['foo'])
    tester.compare('http://baz.com',res['baz'])
    tester.compare('http://default.com',res[None])
    tester.compare('http://www.w3.org/XML/1998/namespace',res['xml'])
    tester.testDone()

    src_3 = """
<data xmlns="http://default.com">
  <group xmlns=""><e/></group>
  <group><e/></group>
</data>
"""
    isrc = InputSource.DefaultFactory.fromString(src_3, "dummy")
    doc = module.NonvalParse(isrc)

    tester.startTest("Default xmlns declaration")
    node1 = doc.documentElement.childNodes[1].firstChild
    node2 = doc.documentElement.childNodes[3].firstChild
    nss1 = module.GetAllNs(node1)
    tester.compare(1, len(nss1))
    tester.compare(True, 'xml' in nss1)
    tester.compare('http://www.w3.org/XML/1998/namespace', nss1['xml'])
    tester.compare(False, None in nss1)

    nss2 = module.GetAllNs(node2)
    tester.compare(2, len(nss2))
    tester.compare(True, 'xml' in nss2)
    tester.compare('http://www.w3.org/XML/1998/namespace', nss2['xml'])
    tester.compare(True, None in nss2)
    tester.compare('http://default.com', nss2[None])
    tester.testDone()

    doc = module.implementation.createDocument(None,None,None)
    elem = doc.createElementNS("http://element.com","foo:root")
    elem.setAttributeNS("http://www.w3.org/2000/xmlns/","xmlns:foo","http://attrDecl")

    tester.startTest("Different element and namespace decl")
    res = module.GetAllNs(elem)
    tester.compare(2,len(res.keys()))
    tester.compare(1,res.has_key('xml'))
    tester.compare(1,res.has_key('foo'))
    tester.compare('http://element.com',res['foo'])
    tester.compare('http://www.w3.org/XML/1998/namespace',res['xml'])
    tester.testDone()

    tester.groupDone()
    return

def test_seek_nss(tester, module):
    tester.startGroup("SeekNss")

    src_1 = """
<foo:bar xmlns:foo='http://foo.com'>
  <baz:bar xmlns:baz='http://baz.com'/>
</foo:bar>
"""
    isrc = InputSource.DefaultFactory.fromString(src_1, "dummy")
    doc = module.NonvalParse(isrc)

    tester.startTest("Simple")
    node = doc.documentElement
    res = module.SeekNss(node)
    tester.compare(2,len(res.keys()))
    tester.compare(1,res.has_key('foo'))
    tester.compare('http://foo.com',res['foo'])
    tester.compare(1,res.has_key('baz'))
    tester.compare('http://baz.com',res['baz'])
    tester.testDone()

    src_1a = """
<foo:bar xmlns:foo='http://foo.com'>
  <foo:bar xmlns:foo='http://other-foo.com'/>
</foo:bar>
"""
    isrc = InputSource.DefaultFactory.fromString(src_1a, "dummy")
    doc = module.NonvalParse(isrc)

    tester.startTest("Redefined prefix")
    node = doc.documentElement
    res = module.SeekNss(node)
    tester.compare(1,len(res.keys()))
    tester.compare(1,res.has_key('foo'))
    tester.compare('http://foo.com',res['foo'])
    tester.testDone()

    src_2 = """
<foo:bar xmlns='http://default.com'
         xmlns:foo='http://foo.com'
         xmlns:baz='http://baz.com'
/>"""
    isrc = InputSource.DefaultFactory.fromString(src_2, "dummy")
    doc = module.NonvalParse(isrc)

    tester.startTest("Unused xmlns declaration")
    node = doc.documentElement
    res = module.SeekNss(node)
    tester.compare(3,len(res.keys()))
    tester.compare(1,res.has_key('foo'))
    tester.compare(1,res.has_key('baz'))
    tester.compare(1,res.has_key(None))
    tester.compare('http://foo.com',res['foo'])
    tester.compare('http://baz.com',res['baz'])
    tester.compare('http://default.com',res[None])
    tester.testDone()

    src_3 = """
<foo:bar xmlns:foo='http://foo.com'
         xmlns:baz='http://baz.com'>
  <bar xmlns='http://default.com'/>
  <bar xmlns='http://other-default.com'/>
</foo:bar>"""
    isrc = InputSource.DefaultFactory.fromString(src_3, "dummy")
    doc = module.NonvalParse(isrc)

    tester.startTest("Default xmlns declaration")
    node = doc.documentElement
    res = module.SeekNss(node)
    tester.compare(3,len(res.keys()))
    tester.compare(1,res.has_key('foo'))
    tester.compare(1,res.has_key('baz'))
    tester.compare(1,res.has_key(None))
    tester.compare('http://foo.com',res['foo'])
    tester.compare('http://baz.com',res['baz'])
    tester.compare('http://default.com',res[None])
    tester.testDone()

    src_4 = """
<foo:bar xmlns:foo='http://foo.com'
         xmlns:baz='http://baz.com'>
  <bar xmlns='http://default.com'/>
  <bar xmlns='http://other-default.com'/>
</foo:bar>"""
    isrc = InputSource.DefaultFactory.fromString(src_4, "dummy")
    doc = module.NonvalParse(isrc)

    tester.startTest("Multiple default xmlns declarations")
    node = doc.documentElement
    res = module.SeekNss(node)
    tester.compare(3,len(res.keys()))
    tester.compare(1,res.has_key('foo'))
    tester.compare(1,res.has_key('baz'))
    tester.compare(1,res.has_key(None))
    tester.compare('http://foo.com',res['foo'])
    tester.compare('http://baz.com',res['baz'])
    tester.compare('http://default.com',res[None])
    tester.testDone()

    tester.startTest("Multiple redefined xmlns declarations")
    src_5 = """
<S:foo xmlns:S="http://example.com/1">
  <bar>test</bar>
  <bar xmlns='http://example.com/2'>test2</bar>
  <S:bar xmlns:S='http://example.com/2'>test2</S:bar>
</S:foo>"""
    isrc = InputSource.DefaultFactory.fromString(src_5, "dummy")
    doc = module.NonvalParse(isrc)
    res = module.SeekNss(doc)
    tester.compare(1,len(res.keys()))
    tester.compare(1,res.has_key('S'))
    tester.compare('http://example.com/1', res['S'])
    tester.testDone()

    doc = module.implementation.createDocument(None,None,None)
    elem = doc.createElementNS("http://element.com","foo:root")
    elem.setAttributeNS("http://www.w3.org/2000/xmlns/","xmlns:foo","http://attrDecl")

    tester.startTest("Different element and namespace decl")
    res = module.SeekNss(elem)
    tester.compare(1,len(res.keys()))
    tester.compare(1,res.has_key('foo'))
    tester.compare('http://element.com',res['foo'])
    tester.testDone()

    tester.groupDone()
    return

def Test(tester):
    # -- GetAllNs ------------------------------------------------------
    test_get_all_ns(tester, Domlette)

    # -- SeekNss -------------------------------------------------------
    test_seek_nss(tester, Domlette)
    return
