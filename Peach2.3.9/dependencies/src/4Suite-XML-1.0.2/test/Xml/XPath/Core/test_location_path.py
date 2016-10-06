def Test(tester):

    tester.startGroup('Location path expressions')

    tester.startTest('Creating test environment')
    from Ft.Xml.XPath.ParsedAbbreviatedAbsoluteLocationPath import ParsedAbbreviatedAbsoluteLocationPath
    from Ft.Xml.XPath.ParsedAbbreviatedRelativeLocationPath import ParsedAbbreviatedRelativeLocationPath
    from Ft.Xml.XPath.ParsedAbsoluteLocationPath import ParsedAbsoluteLocationPath
    from Ft.Xml.XPath.ParsedRelativeLocationPath import ParsedRelativeLocationPath
    from Ft.Xml.XPath import ParsedStep
    from Ft.Xml.XPath import ParsedNodeTest
    from Ft.Xml.XPath import ParsedAxisSpecifier
    from Ft.Xml.XPath import Context

    DomTree = tester.test_data['tree']

    nt = ParsedNodeTest.ParsedNameTest('*')
    as = ParsedAxisSpecifier.ParsedAxisSpecifier('child')
    step = ParsedStep.ParsedStep(as,nt,None)
    # [(expression, context, expected)...]
    tests = [(ParsedAbbreviatedAbsoluteLocationPath(step),
              Context.Context(DomTree.CHILD2, 1, 1),
              # all element children
              [DomTree.ROOT, DomTree.CHILD1] + DomTree.GCHILDREN1 +
              [DomTree.CHILD2] + DomTree.GCHILDREN2 + [DomTree.CHILD3] +
              [DomTree.LANG] + DomTree.LCHILDREN),
             (ParsedAbbreviatedRelativeLocationPath(step, step),
              Context.Context(DomTree.ROOT, 1, 1),
              # all element grand children
              DomTree.GCHILDREN1 + DomTree.GCHILDREN2 + DomTree.LCHILDREN),
             (ParsedAbsoluteLocationPath(None),
              Context.Context(DomTree.CHILD1, 1, 1),
              [DomTree.DOM]),
             (ParsedAbsoluteLocationPath(step),
              Context.Context(DomTree.CHILD1, 1, 1),
              [DomTree.ROOT]),
             (ParsedRelativeLocationPath(step, step),
              Context.Context(DomTree.ROOT, 1, 1),
              DomTree.GCHILDREN1 + DomTree.GCHILDREN2 + DomTree.LCHILDREN),
             ]
    tester.testDone()

    for (location, context, expected) in tests:
        tester.startTest(repr(location))
        actual = location.select(context)
        tester.compare(expected, actual)
        tester.testDone()

    return tester.groupDone()
