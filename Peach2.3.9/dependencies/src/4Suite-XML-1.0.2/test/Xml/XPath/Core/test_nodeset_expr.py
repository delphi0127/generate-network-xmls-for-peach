#!/usr/bin/env python
#
# File Name:        File Name
#
# Documentation:    http://docs.fourthought.com/file/name.html
#


def Test(tester):

    tester.startGroup('Node-set Expressions')

    tester.startTest('Creating test environment')

    from Ft.Xml.XPath import ParsedExpr
    from Ft.Xml.XPath import ParsedPredicateList

    DomTree = tester.test_data['tree']

    import DummyExpr
    from DummyExpr import boolT, boolF
    from DummyExpr import num3, numN4, num4p5
    from DummyExpr import strPi, strText
    
    nodeset0 = DummyExpr.DummyNodeSetExpr([])
    nodeset1 = DummyExpr.DummyNodeSetExpr([DomTree.ROOT])
    nodeset2 = DummyExpr.DummyNodeSetExpr([DomTree.ROOT, DomTree.CHILD1])
    nodeset3 = DummyExpr.DummyNodeSetExpr([DomTree.CHILD1])
    nodeset4 = DummyExpr.DummyNodeSetExpr([DomTree.CHILD3])

    from Ft.Xml.XPath import Context
    context1 = Context.Context(DomTree.CHILD1,1,2)
    context2 = Context.Context(DomTree.CHILD2,2,2)
    plT = ParsedPredicateList.ParsedPredicateList([boolT])
    plF = ParsedPredicateList.ParsedPredicateList([boolF])

    tests = {ParsedExpr.ParsedFilterExpr : [((nodeset2, plT), context1, list(nodeset2.val)),
                                            ((nodeset2, plF), context1, []),
                                            ],
             ParsedExpr.ParsedPathExpr : [((0, nodeset2, nodeset1), context1, list(nodeset1.val)),
                                          ],
             ParsedExpr.ParsedUnionExpr : [((nodeset2, nodeset1), context1, list(nodeset2.val)),
                                           ],

             }

    tester.testDone()

    for (expr, boolTests) in tests.items():
        for (args, context, expected) in boolTests:
            p = apply(expr, args)
            tester.startTest('Comparing %s' % repr(p))
            result = p.evaluate(context)
            tester.compare(result, expected)
            tester.testDone()

    tester.groupDone()

if __name__ == '__main__':
    from Ft.Lib.TestSuite import Tester
    tester = Tester.Tester()
    Test(tester)
