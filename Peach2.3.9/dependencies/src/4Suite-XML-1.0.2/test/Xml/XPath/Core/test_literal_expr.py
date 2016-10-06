from Ft.Lib import number
from Ft.Xml import XPath
from Ft.Xml.XPath import Context
from Ft.Xml.XPath.ParsedExpr import ParsedLiteralExpr, ParsedNLiteralExpr

StringLiterals = {}
def setupStringLiterals():
    global StringLiterals
    for key, token, evaluated in [
        # lookup key, token, expected evaluated result
        ('Empty', u'""', u''),
        ('Hi', u'"Hi"', u'Hi'),
        ('NaN', u'"NaN"', u'NaN'),
        ('Unicode', u'"\u2022 = middle dot"', u'\u2022 = middle dot'),
        ('0', u'"0"', u'0'),
        ('1', u'"1"', u'1'),
        ('2', u'"2"', u'2'),
        ('3', u'"3"', u'3'),
        ('4', u'"4"', u'4'),
        ('5', u'"5"', u'5'),
        ('31', u'"31"', u'31'),
        ('N1', u'"-1"', u'-1'),
        ('N2', u'"-2"', u'-2'),
        ('N3', u'"-3"', u'-3'),
        ('N4', u'"-4"', u'-4'),
        ('N5', u'"-5"', u'-5'),
        ('Pi', u'"3.1415926535"', u'3.1415926535'),
        ]:
        StringLiterals[key] = (ParsedLiteralExpr(token), evaluated)
    return


NumberLiterals = {}
def setupNumberLiterals():
    global NumberLiterals
    for key, token, evaluated in [
        # lookup key, token, expected evaluated result
        ('0', 0, 0.0),
        ('0p5', 0.5, 0.5),
        ('N0p5', -0.5, -0.5),
        ('1', 1, 1.0),
        ('N1', -1, -1.0),
        ('1p5', 1.5, 1.5),
        ('N1p5', -1.5, -1.5),
        ('2', 2, 2.0),
        ('N2', -2, -2.0),
        ('2p6', 2.6, 2.6),
        ('N2p6', -2.6, -2.6),
        ('3', 3, 3.0),
        ('N3', -3.0, -3.0),
        ('31', 31, 31.0),
        ('4', 4, 4.0),
        ('N4', -4, -4.0),
        ('4p5', 4.5, 4.5),
        ('N4p5', -4.5, -4.5),
        ('5', 5, 5.0),
        ('N5', -5, -5.0),
        ('N42', -42, -42.0),
        ('NaN', number.nan, number.nan),
        ('Inf', number.inf, number.inf),
        ('NInf', -number.inf, -number.inf),
        ]:
        NumberLiterals[key] = (ParsedNLiteralExpr(token), evaluated)
    return


def Test(tester):

    context = Context.Context(tester.test_data['tree'].CHILD1,1,3)

    tester.startGroup('String Literals')

    tester.startTest('Parse string literal expression tokens')
    setupStringLiterals()
    tester.testDone()

    tester.startGroup('Evaluate parsed string literal expression tokens')
    global StringLiterals
    for parsedexpr, expected in StringLiterals.values():
        tester.startTest(repr(parsedexpr))
        tester.compare(expected, parsedexpr.evaluate(context))
        tester.testDone()
    tester.groupDone()

    tester.groupDone()

    tester.startGroup('Number Literals')

    tester.startTest('Parse numeric literal expression tokens')
    setupNumberLiterals()
    tester.testDone()

    tester.startGroup('Evaluate parsed numeric literal expression tokens')
    global NumberLiterals
    for parsedexpr, expected in NumberLiterals.values():
        tester.startTest(repr(parsedexpr))
        tester.compare(expected, parsedexpr.evaluate(context))
        tester.testDone()
    tester.groupDone()

    tester.groupDone()

