def Test(tester):

    tester.startGroup('Steps')
    
    tester.startTest('Checking syntax')
    DomTree = tester.test_data['tree']
    from Ft.Xml.XPath import ParsedStep
    from Ft.Xml.XPath import ParsedNodeTest
    from Ft.Xml.XPath import ParsedExpr
    from Ft.Xml.XPath import ParsedPredicateList
    from Ft.Xml.XPath import ParsedAxisSpecifier
    from Ft.Xml.XPath import Context
    tester.testDone()
    
    tester.startTest('Creating test environment')
    rootContext = Context.Context(DomTree.ROOT,1,1)
    context = child1Context = Context.Context(DomTree.CHILD1,1,3)
    child2Context = Context.Context(DomTree.CHILD2,2,3)
    textContext = Context.Context(DomTree.TEXT1,3,3)
    
    tests = []

    # Test 1
    as = ParsedAxisSpecifier.ParsedAxisSpecifier('ancestor')
    nt = ParsedNodeTest.ParsedNameTest('*')
    s = ParsedStep.ParsedStep(as, nt)
    tests.append((s, [DomTree.ROOT]))
    
    # Test 2
    as = ParsedAxisSpecifier.ParsedAxisSpecifier('ancestor-or-self')
    s = ParsedStep.ParsedStep(as, nt, None)
    tests.append((s, [DomTree.ROOT, DomTree.CHILD1]))

    # Test 3
    as = ParsedAxisSpecifier.ParsedAxisSpecifier('descendant-or-self')
    nt = ParsedNodeTest.ParsedNameTest('GCHILD')
    s = ParsedStep.ParsedStep(as, nt)
    tests.append((s, DomTree.GCHILDREN1))
    
    # Test 4
    as = ParsedAxisSpecifier.ParsedAxisSpecifier('child')
    nt = ParsedNodeTest.ParsedNameTest('GCHILD')
    left = ParsedExpr.ParsedFunctionCallExpr('position', [])
    right = ParsedExpr.ParsedNLiteralExpr('1')
    exp = ParsedExpr.ParsedEqualityExpr('=', left, right)
    pl = ParsedPredicateList.ParsedPredicateList([exp])
    s = ParsedStep.ParsedStep(as, nt, pl)
    tests.append((s, [DomTree.GCHILD11]))

    # Test 5
    right = ParsedExpr.ParsedNLiteralExpr('1')
    pl = ParsedPredicateList.ParsedPredicateList([right])
    as = ParsedAxisSpecifier.ParsedAxisSpecifier('child')
    nt = ParsedNodeTest.ParsedNameTest('GCHILD')
    s = ParsedStep.ParsedStep(as,nt,pl)
    tests.append((s, [DomTree.GCHILD11]))
    
    tester.testDone()

    for step,expected in tests:
        tester.startTest('Select "%s"' % repr(step))
        node_set = step.select(context)
        if len(node_set) != len(expected):
            tester.error('Wrong size of node set. Expected %d, got %d' % (
                len(expected),
                len(node_set)
                ))
        results = map(lambda a,b: a == b, node_set, expected)
        if not reduce(lambda a,b: a and b, results, 1):
            tester.error('Invalid node in node set. Expected\n%s\ngot\n%s' % (
                str(expected),
                str(node_set),
                ))
        tester.testDone()
   

    return tester.groupDone()
