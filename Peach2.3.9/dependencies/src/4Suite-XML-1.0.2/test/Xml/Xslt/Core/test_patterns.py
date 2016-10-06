# XPatternParser Test patterns
import sys, cStringIO

class TestCase:
    def __init__(self, pattern, expected=None):
        self.pattern = pattern
        self.expected = expected or pattern


patterns = [TestCase('para'),
            TestCase('*'),
            TestCase('chapter | appendix'),
            TestCase('olist/item'),
            TestCase('appendix//para'),
            TestCase('/'),
            TestCase('text()'),
            TestCase('processing-instruction()'),
            TestCase('node()'),
            TestCase('id("W11")'),
            TestCase('para[1]'),
            TestCase('*[position()=1 and self::para]',
                     '*[position() = 1 and self::para]'),
            TestCase('para[last()=1]', 'para[last() = 1]'),
            TestCase('items/item[position()>1]',
                     'items/item[position() > 1]'),
            TestCase('item[(position() mod 2) = 1]',
                     'item[position() mod 2 = 1]'),
            TestCase('div[@class="appendix"]//p',
                     'div[attribute::class = "appendix"]//p'),
            TestCase('@class'),
            TestCase('@*'),
            TestCase('@class[.="appendix"]',
                     '@class[. = "appendix"]'),
            TestCase('appendix//ulist/item[position()=1]',
                     'appendix//ulist/item[position() = 1]'),
            TestCase('* | /'),
            TestCase('text() | @*'),
            ]

from Ft.Xml.Xslt import parser
parsers = [('Default', parser)]
try:
    from Ft.Xml.Xslt import XPatternParser
    parsers.append(('BisonGen Python Parser', XPatternParser))
except:
    pass
try:
    from Ft.Xml.Xslt import XPatternParserc
    parsers.append(('BisonGen C Parser', XPatternParserc))
except:
    pass

def Test(tester):
    for (name, factory) in parsers:
        parser = factory.new()
        tester.startGroup('%s (%s)' % (name, factory.__name__))
        for case in patterns:
            tester.startTest(case.pattern)
            result = parser.parse(case.pattern)
            sys.stdout = cStringIO.StringIO()
            result.pprint()
            msg = sys.stdout.getvalue()
            sys.stdout = sys.__stdout__
            tester.compare(case.expected, repr(result), msg)
            tester.testDone()
        tester.groupDone()

    return
