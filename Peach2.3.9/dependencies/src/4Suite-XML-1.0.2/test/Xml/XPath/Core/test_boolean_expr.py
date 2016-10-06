def Test(tester):

    tester.startGroup('Boolean Expressions')

    tester.startTest('Creating test environment')
    from Ft.Xml.XPath import ParsedExpr
    from Ft.Lib import boolean

    from DummyExpr import boolT, boolF
    from DummyExpr import num3, numN4, num4p5, numNan, numInf
    from DummyExpr import strPi, strText, STR_EGG1, STR_EGG2
    from DummyExpr import EMPTY_NODE_SET, ONE_NODE_SET, TWO_NODE_SET
    from DummyExpr import nodesetNum0, nodesetNum2, nodesetNum4

    tests = {
        ParsedExpr.ParsedRelationalExpr : [
            # (opcode, left, right), where opcode is
            #  0: <, 1: <=, 2: >, 3: >=
            ((0, strPi, numN4), boolean.false),
            ((1, strPi, numN4), boolean.false),
            ((2, strPi, numN4), boolean.true),
            ((3, strPi, strPi), boolean.true),
            ((0, numNan, numN4), boolean.false),
            ((1, numNan, numN4), boolean.false),
            ((2, numNan, numN4), boolean.false),
            ((3, numNan, strPi), boolean.false),
            ((1, nodesetNum2, nodesetNum2), boolean.true),
            ((3, nodesetNum2, nodesetNum2), boolean.true),
            ((1, nodesetNum0, nodesetNum2), boolean.true),
            ((3, nodesetNum0, nodesetNum2), boolean.false),
            ((1, nodesetNum4, nodesetNum2), boolean.false),
            ((3, nodesetNum4, nodesetNum2), boolean.true),
            ],
        ParsedExpr.ParsedEqualityExpr : [
            (('=', strPi, strPi), boolean.true),
            (('=', strPi, strText), boolean.false),
            (('!=', strPi, numN4), boolean.true),
            (('=', numNan, strText), boolean.false),
            (('!=', numNan, numN4), boolean.true),
            (('=', numNan, numNan), boolean.false),
            (('!=', numNan, numNan), boolean.true),
            (('=', EMPTY_NODE_SET, boolT), boolean.false),
            (('!=', EMPTY_NODE_SET, boolT), boolean.true),
            (('=', EMPTY_NODE_SET, boolF), boolean.true),
            (('!=', EMPTY_NODE_SET, boolF), boolean.false),
            (('=', EMPTY_NODE_SET, ONE_NODE_SET), boolean.false),
            (('!=', EMPTY_NODE_SET, ONE_NODE_SET), boolean.false),
            (('=', ONE_NODE_SET, EMPTY_NODE_SET), boolean.false),
            (('!=', ONE_NODE_SET, EMPTY_NODE_SET), boolean.false),
            (('=', ONE_NODE_SET, ONE_NODE_SET), boolean.true),
            (('!=', ONE_NODE_SET, ONE_NODE_SET), boolean.false),
            (('=', STR_EGG1, ONE_NODE_SET), boolean.true),
            (('!=', STR_EGG1, ONE_NODE_SET), boolean.false),
            (('=', STR_EGG2, ONE_NODE_SET), boolean.false),
            (('!=', STR_EGG2, ONE_NODE_SET), boolean.true),
            (('=', STR_EGG1, TWO_NODE_SET), boolean.true),
            # Yeah, non-intuitive, but boolean.true acc to XPath spec 3.4
            (('!=', STR_EGG1, TWO_NODE_SET), boolean.true),
            ],
        ParsedExpr.ParsedAndExpr : [
            ((boolT, boolT), boolean.true),
            ((boolT, boolF), boolean.false),
            ((boolF, boolF), boolean.false),
            ],
        ParsedExpr.ParsedOrExpr : [
            ((boolT, boolF), boolean.true),
            ((boolT, boolT), boolean.true),
            ((boolF, boolF), boolean.false),
            ],
        }

    tester.testDone()

    for exprClass, tests in tests.iteritems():
        tester.startTest(exprClass.__name__)
        for args, expected in tests:
            expr = exprClass(*args)
            result = expr.evaluate(None)
            tester.compare(expected, result, repr(expr))
        tester.testDone()

    tester.groupDone()
