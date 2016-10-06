from Ft.Lib import boolean
from Ft.Lib.number import nan
from Ft.Xml.XPath import parser, CompiletimeException, Compile, RuntimeException, Evaluate


_parsers = [parser]
try:
    from Ft.Xml.XPath import XPathParser
    _parsers.append(XPathParser)
except:
    pass
try:
    from Ft.Xml.XPath import XPathParserc
    _parsers.append(XPathParserc)
except:
    pass

def equal(expected, actual):
    results = map(lambda a, b: a == b, node_set, expected)
    return reduce(lambda a, b: a and b, results, 1)

def Test(tester):

    tester.startGroup('Expression Parser')

    tester.startTest('Creating test environment')
    from Ft.Xml.XPath import Context
    DomTree = tester.test_data['tree']

    # not the root node, but the document element
    root = Context.Context(DomTree.ROOT, 1, 1, varBindings={(None, 'foo'): [DomTree.ROOT]})
    child1 = Context.Context(DomTree.CHILD1, 1, 2, processorNss={'x': 'http://spam.com'})
    child2 = Context.Context(DomTree.CHILD2, 2, 2)
    child3 = Context.Context(DomTree.CHILD3, 1, 1)
    text = Context.Context(DomTree.TEXT1, 3, 3)
    gchild11 = Context.Context(DomTree.GCHILD11, 1, 2)
    lang = Context.Context(DomTree.LANG, 1, 1)

    tests = [('child::*', root, DomTree.CHILDREN),
             ('/child::*', child1, [DomTree.ROOT]),
             ('/*/*', child1, DomTree.CHILDREN),
             ('/child::*/*/child::GCHILD', child1, DomTree.GCHILDREN1 + DomTree.GCHILDREN2),
             ('//*', child1, ([DomTree.ROOT, DomTree.CHILD1] + DomTree.GCHILDREN1 +
                              [DomTree.CHILD2] + DomTree.GCHILDREN2 +
                              [DomTree.CHILD3] + [DomTree.LANG] + DomTree.LCHILDREN)),
             ('//GCHILD', child1, DomTree.GCHILDREN1 + DomTree.GCHILDREN2),
             ('//@attr1', child1, [DomTree.ATTR1, DomTree.ATTR2]),
             ('x:GCHILD', child1, []),
             ('.//GCHILD', child2, DomTree.GCHILDREN2),
             ('.//GCHILD', root, DomTree.GCHILDREN1 + DomTree.GCHILDREN2),
             ('/', text, [DomTree.DOM]),
             ('//CHILD1/..', child1, [DomTree.ROOT]),
             ('.//foo:*', child3, []),
             ('CHILD1 | CHILD2', root, [DomTree.CHILD1, DomTree.CHILD2]),
             ('descendant::GCHILD[3]', root, [DomTree.GCHILD21]),
             ('descendant::GCHILD[parent::CHILD1]', root, DomTree.GCHILDREN1),
             ('descendant::GCHILD[position() > 1]', root, [DomTree.GCHILD12] + DomTree.GCHILDREN2),
             ('@attr1[.="val1"]', child1, [DomTree.ATTR1]),
             ('1', root, 1),
             ('00200', root, 200),
             ('3+4*7', root, 31),
             ('3-4*1', root, -1),
             ("string('1')", root, u"1"),
             ("concat('1', '2')", root, u"12"),
             ("true()", root, boolean.true),
             ("false()", root, boolean.false),
             ("1=3<4", root, boolean.true),
             ("1 or 2 and 3", root, boolean.true),
             ("1 and 2 = 3", root, boolean.false),
             ('-1 or 2', root, boolean.true),
             ('. or *', root, boolean.true),
             ("$foo[1]", root, [DomTree.ROOT]),
             ("text()", child3, []),
             ("processing-instruction('f')", root, []),
             ("$foo[1]/bar", root, []),
             ("$foo[1]//bar", root, []),
             ("$foo[1][3]", root, []),
             ('(child::*)', root, DomTree.CHILDREN),
             ('. * 0', root, nan),
             ('.. * 0', root, nan),
             ('/.. * 0', root, nan),
             ('CHILD2/@CODE', root, [DomTree.IDATTR2]),
             ('CHILD2/@CODE * 0', root, 0),
             (u'f\xf6\xf8', lang, [DomTree.NONASCIIQNAME]),
             ]
    tester.testDone()

    for (expr_str, context, expected) in tests:
        fromHere = context.node.nodeName
        tester.startTest('Evaluation of %r' % expr_str)
        message = 'Error while evaluating "%r" from <%r>' % (expr_str, fromHere)
        for factory in _parsers:
            parser = factory.new()
            try:
                parsed_expr = parser.parse(expr_str)
            except:
                tester.error('Error while parsing "%r"' % expr_str, traceLimit=None)
        node_set = parsed_expr.evaluate(context)
        tester.compare(expected, node_set, message)
        tester.testDone()


    tester.startTest("Syntax Exception")
    for factory in _parsers:
        parser = factory.new()
        tester.testException(parser.parse, ("\\", ), SyntaxError)
    tester.testDone()

    tester.startTest("Compiletime Exception")
    tester.testException(Compile, ("\\", ), CompiletimeException)
    tester.testDone()

    tester.startTest("Runtime Exception")
    tester.testException(Evaluate, ("$foo", DomTree.ROOT), RuntimeException)
    tester.testDone()


    return tester.groupDone()
