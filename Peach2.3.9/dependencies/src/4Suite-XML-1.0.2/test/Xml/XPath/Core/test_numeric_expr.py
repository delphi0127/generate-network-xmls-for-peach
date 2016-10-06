import test_literal_expr
from Ft.Xml.XPath import ParsedExpr
from Ft.Lib.boolean import true, false
from Ft.Lib.number import nan, inf

test_literal_expr.setupStringLiterals()
StringLiterals = test_literal_expr.StringLiterals
test_literal_expr.setupNumberLiterals()
NumberLiterals = test_literal_expr.NumberLiterals


def RunTests(tester, tests):
    for klass, cases in tests:
        tester.startGroup(klass.__name__)
        for args, expected in cases:
            expr = klass(*args)
            # of course the test started already,
            # but we like the nice string repr
            tester.startTest(repr(expr))
            result = expr.evaluate(None)
            tester.compare(expected, result, 'Wrong result evaluating "%s".' % repr(expr))
            tester.testDone()
        tester.groupDone()


def Test(tester):

    tester.startGroup('Numeric Expressions with Number Literals')

    tester.startTest('Creating test environment')

    from DummyExpr import DummyNodeSetExpr
    DomTree = tester.test_data['tree']
    attr31 = DomTree.ATTR31
    nodeset31 = DummyNodeSetExpr([attr31])

    # IEEE 754 says:
    #
    #   +-Infinity * +-Infinity = +-Infinity
    #   +-Infinity * 0 = NaN
    #
    #   n div +-Infinity = 0
    #   +-nonzero div 0 = +-Infinity
    #   +-Infinity div +-Infinity = NaN
    #   +-0 div +-0 = NaN
    #
    #   Infinity + Infinity = Infinity
    #   Infinity - Infinity = NaN

    # operators:
    #    *  -> 0
    #   div -> 1
    #   mod -> 2
    multiply_tests = [#(operator, left expression, right expression), expected result)
                      ((0, NumberLiterals['N5'][0], NumberLiterals['2'][0]), -10.0),
                      ((0, NumberLiterals['N4'][0], NumberLiterals['N2'][0]), 8.0),
                      ((0, NumberLiterals['0'][0], NumberLiterals['2'][0]), 0.0),
                      ((0, NumberLiterals['Inf'][0], NumberLiterals['Inf'][0]), inf),
                      ((0, NumberLiterals['NInf'][0], NumberLiterals['NInf'][0]), inf),
                      ((0, NumberLiterals['Inf'][0], NumberLiterals['NInf'][0]), -inf),
                      ((1, NumberLiterals['0'][0], NumberLiterals['2'][0]), 0.0),
                      ((1, NumberLiterals['N5'][0], NumberLiterals['2'][0]), -2.5),
                      ((1, NumberLiterals['N4'][0], NumberLiterals['N2'][0]), 2.0),
                      ((1, NumberLiterals['0'][0], NumberLiterals['0'][0]), nan),
                      ((1, NumberLiterals['1'][0], NumberLiterals['0'][0]), inf),
                      ((1, NumberLiterals['N1'][0], NumberLiterals['0'][0]), -inf),
                      ((1, NumberLiterals['0'][0], NumberLiterals['Inf'][0]), 0),
                      ((1, NumberLiterals['1'][0], NumberLiterals['Inf'][0]), 0),
                      ((1, NumberLiterals['N1'][0], NumberLiterals['Inf'][0]), 0),
                      ((1, NumberLiterals['0'][0], NumberLiterals['NInf'][0]), 0),
                      ((1, NumberLiterals['1'][0], NumberLiterals['NInf'][0]), 0),
                      ((1, NumberLiterals['N1'][0], NumberLiterals['NInf'][0]), 0),
                      ((1, NumberLiterals['Inf'][0], NumberLiterals['Inf'][0]), nan),
                      ((1, NumberLiterals['Inf'][0], NumberLiterals['NInf'][0]), nan),
                      ((1, NumberLiterals['NInf'][0], NumberLiterals['NInf'][0]), nan),
                      ((1, NumberLiterals['NInf'][0], NumberLiterals['Inf'][0]), nan),
                      ((2, NumberLiterals['0'][0], NumberLiterals['2'][0]), 0.0),
                      ((2, NumberLiterals['5'][0], NumberLiterals['2'][0]), 1.0),
                      ((2, NumberLiterals['5'][0], NumberLiterals['N2'][0]), -1.0),
                      ((2, NumberLiterals['N5'][0], NumberLiterals['2'][0]), 1.0),
                      ((2, NumberLiterals['N5'][0], NumberLiterals['N2'][0]), -1.0),
                      ]

    # operators:
    #   + -> 1
    #   - -> -1
    addition_tests = [((1, NumberLiterals['5'][0], NumberLiterals['2'][0]), 7.0),
                      ((1, NumberLiterals['3'][0], NumberLiterals['N2'][0]), 1.0),
                      ((1, NumberLiterals['Inf'][0], NumberLiterals['Inf'][0]), inf),
                      ((-1, NumberLiterals['5'][0], NumberLiterals['2'][0]), 3.0),
                      ((-1, NumberLiterals['3'][0], NumberLiterals['N2'][0]), 5.0),
                      ((-1, NumberLiterals['Inf'][0], NumberLiterals['Inf'][0]), nan),
                      ]

    unary_tests = [((NumberLiterals['5'][0],), -5.0),
                   ((NumberLiterals['N2'][0],), 2.0),
                   ]

    # operators:
    #  '=' -> =
    #  (anything else) -> '!='
    equality_tests = [(('=', NumberLiterals['5'][0], NumberLiterals['5'][0]), true),
                      (('=', NumberLiterals['5'][0], NumberLiterals['N5'][0]), false),
                      (('=', NumberLiterals['N5'][0], NumberLiterals['N5'][0]), true),
                      (('=', NumberLiterals['0'][0], NumberLiterals['0'][0]), true),
                      (('=', NumberLiterals['Inf'][0], NumberLiterals['Inf'][0]), true),
                      (('=', NumberLiterals['NInf'][0], NumberLiterals['NInf'][0]), true),
                      (('=', NumberLiterals['5'][0], NumberLiterals['Inf'][0]), false),
                      (('=', NumberLiterals['5'][0], NumberLiterals['NaN'][0]), false),
                      (('=', NumberLiterals['NaN'][0], NumberLiterals['NaN'][0]), false),
                      (('=', NumberLiterals['5'][0], nodeset31), false),
                      (('!=', NumberLiterals['5'][0], NumberLiterals['5'][0]), false),
                      (('!=', NumberLiterals['5'][0], NumberLiterals['N5'][0]), true),
                      (('!=', NumberLiterals['N5'][0], NumberLiterals['N5'][0]), false),
                      (('!=', NumberLiterals['0'][0], NumberLiterals['0'][0]), false),
                      (('!=', NumberLiterals['Inf'][0], NumberLiterals['Inf'][0]), false),
                      (('!=', NumberLiterals['NInf'][0], NumberLiterals['NInf'][0]), false),
                      (('!=', NumberLiterals['5'][0], NumberLiterals['Inf'][0]), true),
                      (('!=', NumberLiterals['5'][0], NumberLiterals['NaN'][0]), true),
                      (('!=', NumberLiterals['NaN'][0], NumberLiterals['NaN'][0]), true),
                      (('!=', NumberLiterals['5'][0], nodeset31), true),
                      ]

    # operators:
    #  0 -> <
    #  1 -> <=
    #  2 -> >
    #  3 -> >=
    relational_tests = [((0, NumberLiterals['5'][0], NumberLiterals['5'][0]), false),
                        ((1, NumberLiterals['5'][0], NumberLiterals['5'][0]), true),
                        ((2, NumberLiterals['5'][0], NumberLiterals['5'][0]), false),
                        ((3, NumberLiterals['5'][0], NumberLiterals['5'][0]), true),
                        ((0, NumberLiterals['5'][0], NumberLiterals['N5'][0]), false),
                        ((1, NumberLiterals['5'][0], NumberLiterals['N5'][0]), false),
                        ((2, NumberLiterals['5'][0], NumberLiterals['N5'][0]), true),
                        ((3, NumberLiterals['5'][0], NumberLiterals['N5'][0]), true),
                        ((0, NumberLiterals['5'][0], NumberLiterals['0'][0]), false),
                        ((1, NumberLiterals['5'][0], NumberLiterals['0'][0]), false),
                        ((2, NumberLiterals['5'][0], NumberLiterals['0'][0]), true),
                        ((3, NumberLiterals['5'][0], NumberLiterals['0'][0]), true),
                        ((0, NumberLiterals['5'][0], NumberLiterals['Inf'][0]), true),
                        ((1, NumberLiterals['5'][0], NumberLiterals['Inf'][0]), true),
                        ((2, NumberLiterals['5'][0], NumberLiterals['Inf'][0]), false),
                        ((3, NumberLiterals['5'][0], NumberLiterals['Inf'][0]), false),
                        ((0, NumberLiterals['5'][0], NumberLiterals['NInf'][0]), false),
                        ((1, NumberLiterals['5'][0], NumberLiterals['NInf'][0]), false),
                        ((2, NumberLiterals['5'][0], NumberLiterals['NInf'][0]), true),
                        ((3, NumberLiterals['5'][0], NumberLiterals['NInf'][0]), true),
                        ((0, NumberLiterals['5'][0], NumberLiterals['NaN'][0]), false),
                        ((1, NumberLiterals['5'][0], NumberLiterals['NaN'][0]), false),
                        ((2, NumberLiterals['5'][0], NumberLiterals['NaN'][0]), false),
                        ((3, NumberLiterals['5'][0], NumberLiterals['NaN'][0]), false),
                        ((0, NumberLiterals['5'][0], nodeset31), true),
                        ((1, NumberLiterals['5'][0], nodeset31), true),
                        ((2, NumberLiterals['5'][0], nodeset31), false),
                        ((3, NumberLiterals['5'][0], nodeset31), false),
                        ]

    tests = [(ParsedExpr.ParsedMultiplicativeExpr, multiply_tests),
             (ParsedExpr.ParsedAdditiveExpr, addition_tests),
             (ParsedExpr.ParsedUnaryExpr, unary_tests),
             (ParsedExpr.ParsedEqualityExpr, equality_tests),
             (ParsedExpr.ParsedRelationalExpr, relational_tests),
             ]
    tester.testDone()

    RunTests(tester, tests)

    tester.groupDone()

    # basically tests automatic coercion of strings to numbers
    tester.startGroup('Numeric Expressions with String Literals')

    tester.startTest('Creating test environment')

    multiply_tests = [#(operator, left expression, right expression), expected result)
                      ((0, StringLiterals['N5'][0], StringLiterals['2'][0]), -10.0),
                      ((0, StringLiterals['N4'][0], StringLiterals['N2'][0]), 8.0),
                      ((0, StringLiterals['0'][0], StringLiterals['2'][0]), 0.0),
                      ((0, StringLiterals['1'][0], StringLiterals['1'][0]), 1.0),
                      ((0, StringLiterals['Pi'][0], StringLiterals['1'][0]), 3.1415926535),
                      ((0, StringLiterals['Empty'][0], StringLiterals['1'][0]), nan),
                      ((0, StringLiterals['Hi'][0], StringLiterals['1'][0]), nan),
                      ((0, StringLiterals['NaN'][0], StringLiterals['1'][0]), nan),
                      ((0, StringLiterals['Unicode'][0], StringLiterals['1'][0]), nan),
                      ((1, StringLiterals['0'][0], StringLiterals['2'][0]), 0.0),
                      ((1, StringLiterals['1'][0], StringLiterals['1'][0]), 1.0),
                      ((1, StringLiterals['N5'][0], StringLiterals['2'][0]), -2.5),
                      ((1, StringLiterals['N4'][0], StringLiterals['N2'][0]), 2.0),
                      ((1, StringLiterals['0'][0], StringLiterals['0'][0]), nan),
                      ((1, StringLiterals['1'][0], StringLiterals['0'][0]), inf),
                      ((1, StringLiterals['N1'][0], StringLiterals['0'][0]), -inf),
                      ((2, StringLiterals['0'][0], StringLiterals['2'][0]), 0.0),
                      ((2, StringLiterals['5'][0], StringLiterals['2'][0]), 1.0),
                      ((2, StringLiterals['5'][0], StringLiterals['N2'][0]), -1.0),
                      ((2, StringLiterals['N5'][0], StringLiterals['2'][0]), 1.0),
                      ((2, StringLiterals['N5'][0], StringLiterals['N2'][0]), -1.0),
                      ]

    addition_tests = [((1, StringLiterals['5'][0], StringLiterals['2'][0]), 7.0),
                      ((1, StringLiterals['3'][0], StringLiterals['N2'][0]), 1.0),
                      ((-1, StringLiterals['5'][0], StringLiterals['2'][0]), 3.0),
                      ((-1, StringLiterals['3'][0], StringLiterals['N2'][0]), 5.0),
                      ]

    unary_tests = [((StringLiterals['5'][0],), -5.0),
                   ((StringLiterals['N2'][0],), 2.0),
                   ]

    equality_tests = [(('=', StringLiterals['5'][0], StringLiterals['5'][0]), true),
                      (('=', StringLiterals['5'][0], StringLiterals['N5'][0]), false),
                      (('=', StringLiterals['N5'][0], StringLiterals['N5'][0]), true),
                      (('=', StringLiterals['0'][0], StringLiterals['0'][0]), true),
                      (('=', StringLiterals['Hi'][0], StringLiterals['Hi'][0]), true),
                      (('=', StringLiterals['5'][0], StringLiterals['Hi'][0]), false),
                      (('=', StringLiterals['5'][0], StringLiterals['NaN'][0]), false),
                      (('=', StringLiterals['NaN'][0], StringLiterals['NaN'][0]), true),
                      (('=', StringLiterals['5'][0], nodeset31), false),
                      (('!=', StringLiterals['5'][0], StringLiterals['5'][0]), false),
                      (('!=', StringLiterals['5'][0], StringLiterals['N5'][0]), true),
                      (('!=', StringLiterals['N5'][0], StringLiterals['N5'][0]), false),
                      (('!=', StringLiterals['0'][0], StringLiterals['0'][0]), false),
                      (('!=', StringLiterals['5'][0], StringLiterals['Hi'][0]), true),
                      (('!=', StringLiterals['5'][0], StringLiterals['NaN'][0]), true),
                      (('!=', StringLiterals['NaN'][0], StringLiterals['NaN'][0]), false),
                      (('!=', StringLiterals['5'][0], nodeset31), true),
                      ]

    relational_tests = [((0, NumberLiterals['5'][0], StringLiterals['5'][0]), false),   # 5 < '5'
                        ((0, NumberLiterals['31'][0], StringLiterals['5'][0]), false),  # 31 < '5'
                        ((0, StringLiterals['5'][0], StringLiterals['5'][0]), false),   # '5' < '5'
                        ((0, StringLiterals['31'][0], StringLiterals['5'][0]), false),  # '31' < '5'
                        ((1, NumberLiterals['5'][0], StringLiterals['5'][0]), true),    # 5 <= '5'
                        ((1, NumberLiterals['31'][0], StringLiterals['5'][0]), false),  # 31 <= '5'
                        ((1, StringLiterals['5'][0], StringLiterals['5'][0]), true),    # '5' <= '5'
                        ((1, StringLiterals['31'][0], StringLiterals['5'][0]), false),  # '31' <= '5'
                        ((2, NumberLiterals['5'][0], StringLiterals['5'][0]), false),   # 5 > '5'
                        ((2, NumberLiterals['31'][0], StringLiterals['5'][0]), true),   # 31 > '5'
                        ((2, StringLiterals['5'][0], StringLiterals['5'][0]), false),   # '5' > '5'
                        ((2, StringLiterals['31'][0], StringLiterals['5'][0]), true),   # '31' > '5'
                        ((0, NumberLiterals['5'][0], StringLiterals['N5'][0]), false),  # 5 < '-5'
                        ((0, NumberLiterals['31'][0], StringLiterals['N5'][0]), false), # 31 < '-5'
                        ((0, StringLiterals['5'][0], StringLiterals['N5'][0]), false),  # '5' < '-5'
                        ((0, StringLiterals['31'][0], StringLiterals['N5'][0]), false), # '31' < '-5'
                        ((1, NumberLiterals['5'][0], StringLiterals['N5'][0]), false),  # 5 <= '-5'
                        ((1, NumberLiterals['31'][0], StringLiterals['N5'][0]), false), # 31 <= '-5'
                        ((1, StringLiterals['5'][0], StringLiterals['N5'][0]), false),  # '5' <= '-5'
                        ((1, StringLiterals['31'][0], StringLiterals['N5'][0]), false), # '31' <= '-5'
                        ((2, NumberLiterals['5'][0], StringLiterals['N5'][0]), true),   # 5 > '-5'
                        ((2, NumberLiterals['31'][0], StringLiterals['N5'][0]), true),  # 31 > '-5'
                        ((2, StringLiterals['5'][0], StringLiterals['N5'][0]), true),   # '5' > '-5'
                        ((2, StringLiterals['31'][0], StringLiterals['N5'][0]), true),  # '31' > '-5'
                        ((0, StringLiterals['5'][0], StringLiterals['Hi'][0]), false),  # '5' < 'Hi'
                        ((1, StringLiterals['5'][0], StringLiterals['Hi'][0]), false),  # '5' <= 'Hi'
                        ((2, StringLiterals['5'][0], StringLiterals['Hi'][0]), false),  # '5' > 'Hi'
                        ((3, StringLiterals['5'][0], StringLiterals['Hi'][0]), false),  # '5' >= 'Hi'
                        ((0, StringLiterals['5'][0], nodeset31), true),                 # '5' < (node '31')
                        ((1, StringLiterals['5'][0], nodeset31), true),                 # '5' <= (node '31')
                        ((2, StringLiterals['5'][0], nodeset31), false),                # '5' > (node '31')
                        ((3, StringLiterals['5'][0], nodeset31), false),                # '5' >= (node '31')
                        ]

    tests = [(ParsedExpr.ParsedMultiplicativeExpr, multiply_tests),
             (ParsedExpr.ParsedAdditiveExpr, addition_tests),
             (ParsedExpr.ParsedUnaryExpr, unary_tests),
             (ParsedExpr.ParsedEqualityExpr, equality_tests),
             (ParsedExpr.ParsedRelationalExpr, relational_tests),
             ]
    tester.testDone()

    RunTests(tester, tests)

    tester.groupDone()

    return
