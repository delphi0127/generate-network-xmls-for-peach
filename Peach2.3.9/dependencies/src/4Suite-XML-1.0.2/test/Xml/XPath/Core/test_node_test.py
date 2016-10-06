def Test(tester):

    tester.startGroup('Node Tests')
    
    tester.startTest('Creating test environment')
    from Ft.Xml.XPath.ParsedNodeTest import ParsedNodeTest, ParsedNameTest
    from Ft.Xml.XPath import Context, Conversions
    from Ft.Lib.boolean import true, false

    DomTree = tester.test_data['tree']

    context = Context.Context(DomTree.ROOT,1,1,{},{'bar':'http://foo.com'})
    tests = [(ParsedNameTest('*'), [(DomTree.ROOT, true)]),
             (ParsedNameTest('bar:CHILD3'), [(DomTree.ROOT, false),
                                             (DomTree.CHILD1, false),
                                             (DomTree.CHILD3, true),
                                             ]),
             (ParsedNameTest('bar:*'), [(DomTree.ROOT, false),
                                        (DomTree.CHILD1, false),
                                        (DomTree.CHILD3, true),
                                        ]),
             (ParsedNodeTest('node'), [(DomTree.ROOT, true),
                                       (DomTree.TEXT1, true),
                                       ]),
             (ParsedNodeTest('text'), [(DomTree.ROOT, false),
                                       (DomTree.TEXT1, true),
                                       ]),
             (ParsedNodeTest('comment'), [(DomTree.ROOT, false),
                                          (DomTree.COMMENT, true),
                                          ]),
             (ParsedNodeTest('processing-instruction'), [(DomTree.ROOT, false),
                                                         (DomTree.PI, true),
                                                         ]),
             (ParsedNodeTest('processing-instruction', "'xml-stylesheet'"), [(DomTree.PI, true),
                                                                           (DomTree.PI2, false),
                                                                           ]),
             ]
                                                  
    tester.testDone()
    
    for nt, nodeTests in tests:
        tester.startTest('Running %s' % repr(nt))
        for node,expected in nodeTests:
            # Use Booleans for display only
            result = Conversions.BooleanValue(nt.match(context, node))
            tester.compare(expected, result, 'Filter of "%s" against %s' % (
                repr(nt),
                node.nodeName,
                ))
        tester.testDone()

    return tester.groupDone()
