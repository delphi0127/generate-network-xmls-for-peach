def Test(tester):

    tester.startGroup('Core Function Library')

    tester.startTest('Creating test environment')

    from Ft.Lib import boolean, number
    from Ft.Xml import XPath
    from Ft.Xml.XPath import ParsedExpr, Context
    from Ft.Xml.XPath import XPathTypes as Types

    DomTree = tester.test_data['tree']
    context1 = Context.Context(DomTree.CHILD1,1,3)
    context2 = Context.Context(DomTree.CHILD2,2,3)
    contextLang1 = Context.Context(DomTree.LCHILD1, 1, 1)
    contextLang2 = Context.Context(DomTree.LCHILD2, 1, 1)

    import DummyExpr
    from DummyExpr import boolT, boolF
    from DummyExpr import num0, num0p5, numN0p5, num1, num1p5, num2, num2p6, num3, numN4, num4p5
    from DummyExpr import numN4p5, numN42, numInf, numNInf, numNan
    from DummyExpr import str12345, strPi, strText, strPiText, strSpace, strHelloWorld, strEmpty
    from DummyExpr import ONE_NODE_SET_DOC2, TWO_NODE_SET_DOC2, THREE_NODE_SET_DOC2, FOUR_NODE_SET_DOC2

    nodeset0 = DummyExpr.DummyNodeSetExpr([])
    nodeset1 = DummyExpr.DummyNodeSetExpr([DomTree.ROOT])
    nodeset2 = DummyExpr.DummyNodeSetExpr([DomTree.ROOT, DomTree.CHILD1])
    nodeset3 = DummyExpr.DummyNodeSetExpr([DomTree.CHILD1])
    nodeset4 = DummyExpr.DummyNodeSetExpr([DomTree.CHILD3])

    strNodeset3 = '\n    \n    \n    Text1\n  '

    # a,b,c,d,e,f,g become A,B,C,D,E,F,G
    translateFrom1 = DummyExpr.DummyStringExpr('abcdefg')
    translateTo1 = DummyExpr.DummyStringExpr('ABCDEFG')
    # e becomes a
    translateFrom2 = DummyExpr.DummyStringExpr('e')
    translateTo2 = DummyExpr.DummyStringExpr('a')
    # e becomes a; extra chars in To string are ignored
    translateFrom3 = DummyExpr.DummyStringExpr('e')
    translateTo3 = DummyExpr.DummyStringExpr('abc')
    # e becomes a; l is deleted
    translateFrom4 = DummyExpr.DummyStringExpr('el')
    translateTo4 = DummyExpr.DummyStringExpr('a')
    # a,b,c,d,e,f,g become A,B,C,D,E,F,G;
    # repeated chars in From string are ignored
    translateFrom5 = DummyExpr.DummyStringExpr('abcdefgabc')
    translateTo5 = DummyExpr.DummyStringExpr('ABCDEFG123')
    translateFrom6 = DummyExpr.DummyStringExpr('abcdefghhe')
    translateTo6 = DummyExpr.DummyStringExpr('ABCDEFGH')
    translateFrom7 = DummyExpr.DummyStringExpr('abcdefgh')
    translateTo7 = DummyExpr.DummyStringExpr('')

    tests = [('last', [], context1, 3),
             ('last', [], context2, 3),
             ('position', [], context1, 1),
             ('position', [], context2, 2),
             ('count', [nodeset2], context1, 2),
             ('id', [num1], context1, [DomTree.CHILD2]),
             ('id', [DummyExpr.DummyStringExpr('1 1')], context1, [DomTree.CHILD2]),
             ('id', [DummyExpr.DummyStringExpr('0')], context1, []),
             ('id', [DummyExpr.DummyStringExpr('0 1')], context1, [DomTree.CHILD2]),
             ('id', [DummyExpr.DummyStringExpr('0 1 1')], context1, [DomTree.CHILD2]),
             ('id', [DummyExpr.DummyStringExpr('0 0 1 1')], context1, [DomTree.CHILD2]),
             ('id', [ONE_NODE_SET_DOC2], context1, []),
             ('id', [TWO_NODE_SET_DOC2], context1, [DomTree.CHILD2]),
             ('id', [THREE_NODE_SET_DOC2], context1, [DomTree.CHILD2]),
             ('id', [FOUR_NODE_SET_DOC2], context1, [DomTree.CHILD2]),
             ('local-name', [nodeset0], context1, ''),
             ('local-name', [nodeset4], context1, 'CHILD3'),
             ('namespace-uri', [nodeset0], context1, ''),
             ('namespace-uri', [nodeset4], context1, u'http://foo.com'),
             ('name', [nodeset4], context1, 'foo:CHILD3'),
             ('string', [nodeset3], context1, strNodeset3),
             ('concat', [nodeset3, strPi, strText], context1, strNodeset3 + u'3.14Hi'),
             ('starts-with', [nodeset3, strPi], context1, boolean.false),
             ('starts-with', [nodeset3, nodeset3], context1, boolean.true),
             ('starts-with', [nodeset3, strEmpty], context1, boolean.true),
             ('contains', [nodeset3, strPi], context1, boolean.false),
             ('contains', [nodeset3, nodeset3], context1, boolean.true),
             ('contains', [nodeset3, strEmpty], context1, boolean.true),
             ('substring-before', [strPiText, strText], context1, u'3.14'),
             ('substring-before', [strPiText, strEmpty], context1, u''),
             ('substring-after', [strPiText, strPi], context1, u'Hi'),
             ('substring-after', [strPiText, strEmpty], context1, u''),
             ('substring', [strPiText, strPi], context1, u'14Hi'),
             ('substring', [strPiText, strPi, num1], context1, u'1'),
             ('substring', [str12345, num2, num3], context1, u'234'),
             ('substring', [str12345, num2], context1, u'2345'),
             ('substring', [str12345, num1p5, num2p6], context1, u'234'),
             ('substring', [str12345, num0, num3], context1, u'12'),
             ('substring', [str12345, numNan, num3], context1, u''),
             ('substring', [str12345, num1, numNan], context1, u''),
             ('substring', [str12345, numN42, numInf], context1, u'12345'),
             ('substring', [str12345, numNInf, numInf], context1, u''),
             ('string-length', [strPiText], context1, 6),
             ('normalize-space', [strSpace], context1, u'Ht There Mike'),
             ('translate', [strSpace, translateFrom1, translateTo1], context1, u'Ht    \t ThErE\t   MikE'),
             ('translate', [strHelloWorld, translateFrom2, translateTo2], context1, u'hallo world'),
             ('translate', [strHelloWorld, translateFrom3, translateTo3], context1, u'hallo world'),
             ('translate', [strHelloWorld, translateFrom4, translateTo4], context1, u'hao word'),
             ('translate', [strHelloWorld, translateFrom5, translateTo5], context1, u'hEllo worlD'),
             ('translate', [strHelloWorld, translateFrom6, translateTo6], context1, u'HEllo worlD'),
             ('translate', [strHelloWorld, translateFrom7, translateTo7], context1, u'llo worl'),
             ('boolean', [strPiText], context1, boolean.true),
             ('not', [strPiText], context1, boolean.false),
             ('true', [], context1, boolean.true),
             ('false', [], context1, boolean.false),
             ('number', [], context1, number.nan),
             ('floor', [strPi], context1, 3),
             ('floor', [numNan], context1, number.nan),
             ('floor', [numInf], context1, number.inf),
             ('floor', [numNInf], context1, -number.inf),
             ('floor', [num0p5], context1, 0),
             ('floor', [numN0p5], context1, -1),
             ('ceiling', [strPi], context1, 4),
             ('ceiling', [numNan], context1, number.nan),
             ('ceiling', [numInf], context1, number.inf),
             ('ceiling', [num0p5], context1, 1),
             ('ceiling', [numN0p5], context1, 0), # actually should be negative zero
             ('round', [strPi], context1, 3),
             ('round', [numN4p5], context1, -4),
             ('round', [numNan], context1, number.nan),
             ('round', [numInf], context1, number.inf),
             ('round', [numNInf], context1, -number.inf),
             ('round', [str12345], context1, 12345),
             ('lang', [DummyExpr.DummyStringExpr('en')], contextLang1, boolean.false),
             ('lang', [DummyExpr.DummyStringExpr('en')], contextLang2, boolean.true),
             ('lang', [DummyExpr.DummyStringExpr('')], contextLang1, boolean.true),
             ('lang', [DummyExpr.DummyStringExpr('')], contextLang2, boolean.false),
             ('lang', [DummyExpr.DummyStringExpr('foo')], contextLang1, boolean.false),
             ('lang', [DummyExpr.DummyStringExpr('foo')], contextLang2, boolean.false),
             ]

    typetests = [('last', [], Types.NumberType),
                 ('position', [], Types.NumberType),
                 ('count', [nodeset0], Types.NumberType),
                 ('id', [DummyExpr.DummyStringExpr('id1')], Types.NodesetType),
                 ('local-name', [nodeset3], Types.StringType),
                 ('namespace-uri', [nodeset3], Types.StringType),
                 ('name', [nodeset3], Types.StringType),
                 ('string', [nodeset3], Types.StringType),
                 ('concat', [nodeset3, DummyExpr.DummyStringExpr('foo')], Types.StringType),
                 ('starts-with', [nodeset3, DummyExpr.DummyStringExpr('foo')], Types.BooleanType),
                 ('contains', [nodeset3, DummyExpr.DummyStringExpr('foo')], Types.BooleanType),
                 ('substring-before', [nodeset3, DummyExpr.DummyStringExpr('foo')], Types.StringType),
                 ('substring-after', [nodeset3, DummyExpr.DummyStringExpr('foo')], Types.StringType),
                 ('substring', [nodeset3, DummyExpr.DummyStringExpr('foo')], Types.StringType),
                 ('string-length', [DummyExpr.DummyStringExpr('foo')], Types.NumberType),
                 ('normalize-space', [DummyExpr.DummyStringExpr('foo')], Types.StringType),
                 ('translate', [DummyExpr.DummyStringExpr('foo'),
                                DummyExpr.DummyStringExpr('f'),
                                DummyExpr.DummyStringExpr('b')], Types.StringType),
                 ('boolean', [nodeset0], Types.BooleanType),
                 ('not', [nodeset0], Types.BooleanType),
                 ('true', [], Types.BooleanType),
                 ('false', [], Types.BooleanType),
                 ('lang', [DummyExpr.DummyStringExpr('en')], Types.BooleanType),
                 ('number', [DummyExpr.DummyStringExpr('foo')], Types.NumberType),
                 ('sum', [nodeset3], Types.NumberType),
                 ('floor', [num4p5], Types.NumberType),
                 ('ceiling', [num4p5], Types.NumberType),
                 ('round', [num4p5], Types.NumberType),
                ]

    tester.testDone()

    tester.startGroup('Function evaluation')

    for (funcname, args, context, expected) in tests:
        p = ParsedExpr.ParsedFunctionCallExpr(funcname, args)
        tester.startTest('Evaluation of %s' % repr(p))
        result = p.evaluate(context)
        tester.compare(expected, result)
        tester.testDone()

    tester.groupDone()

    tester.startGroup('Evaluated function type')

    for (funcname, args, expected) in typetests:
        p = ParsedExpr.ParsedFunctionCallExpr(funcname, args)
        tester.startTest('%s()' % funcname)
        result = p.evaluate(context1)
        tester.compare(expected, type(result))
        tester.testDone()

    tester.groupDone()

    tester.groupDone()

    return
