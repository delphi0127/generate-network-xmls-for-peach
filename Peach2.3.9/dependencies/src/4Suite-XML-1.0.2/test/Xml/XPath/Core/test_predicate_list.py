from Ft.Xml import Domlette
from xml.dom import Node

source_1 = """<?xml version="1.0"?>
<elementList>
    <element>
        <x>
            <y>a</y>
        </x>
    </element>
    <element>
        <x>
            <y>z</y>
        </x>
    </element>
</elementList>"""

def Test(tester):

    tester.startGroup('Predicate List')
    
    tester.startTest('Checking syntax')
    from Ft.Xml.XPath import ParsedPredicateList
    from Ft.Xml.XPath import ParsedExpr
    from Ft.Xml.XPath import Context
    from Ft.Xml.XPath import Evaluate
    import DummyExpr
    DomTree = tester.test_data['tree']
    tester.testDone()

    tester.startTest('Creating test environment')
    t = DummyExpr.DummyBooleanExpr(1)
    f = DummyExpr.DummyBooleanExpr(0)
    a = ParsedExpr.ParsedAndExpr(t,f)
    o = ParsedExpr.ParsedOrExpr(t,f)
    context = Context.Context(DomTree.ROOT,1,1)
    tester.testDone()
    
    p = ParsedPredicateList.ParsedPredicateList([a,t])
    tester.startTest('Filter of "%s"' % repr(p))
    result = p.filter([context.node], context, 0)
    tester.compare(0, len(result))
    tester.testDone()
    
    p = ParsedPredicateList.ParsedPredicateList([o,t])
    tester.startTest('Filter of "%s"' % repr(p))
    result = p.filter([context.node], context, 0)
    tester.compare([DomTree.ROOT], result)
    tester.testDone()

    dom = Domlette.NonvalidatingReader.parseString(source_1,'.')

    expected = filter(lambda x: x.nodeType == Node.ELEMENT_NODE,
                      dom.documentElement.childNodes)[-1]

    tests = [("//element[descendant::y[.='z']]", [expected]),
             ("//element[descendant::y[.='z']][1]", [expected]),
             ("//element[descendant::y[.='z']][2]", []),
             ]

    for (expr, expected) in tests:
        tester.startTest(expr)
        actual = Evaluate(expr, contextNode=dom)
        tester.compare(expected, actual)
        tester.testDone()

    return tester.groupDone()
