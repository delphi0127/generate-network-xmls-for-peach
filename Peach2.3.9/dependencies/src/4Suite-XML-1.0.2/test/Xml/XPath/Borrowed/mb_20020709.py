import os
from Ft.Xml import Domlette
from Ft.Lib import Uri
from xml.dom import Node
from Ft.Xml import InputSource
from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Xml.XPath import Evaluate, Compile, Context


SRC_1 = """<?xml version="1.0" encoding="utf-8"?>
<docu>
<elem xmlns:unused="urn:uuu000"/>
<elem xmlns="urn:sss111"/>
<y:elem xmlns:y="urn:yyyy222"/>
</docu>"""


def Test(tester):
    tester.startGroup('Exercise namespace nodes')
    
    isrc = InputSource.DefaultFactory.fromString(SRC_1, Uri.OsPathToUri(os.getcwd()))
    doc = NonvalidatingReader.parse(isrc)
    con = Context.Context(doc, 1, 1)

    EXPR = '//namespace::node()'
    expr = Compile(EXPR)
    #expr is <AbbreviatedAbsoluteLocationPath: /descendant-or-self::node()/namespace::node()>
    #expr._rel is <Step: namespace::node()>
    #expr._step is <Step: descendant-or-self::node()>
    tester.startTest(EXPR)
    actual = expr.evaluate(con)
    tester.compare(7, len(actual))
    tester.testDone()

    EXPR = '//node()/namespace::node()'
    expr = Compile(EXPR)
    tester.startTest(EXPR)
    EXPECTED = []
    actual = expr.evaluate(con)
    tester.compare(7, len(actual))
    tester.testDone()

    EXPR = '//*/namespace::node()'
    expr = Compile(EXPR)
    tester.startTest(EXPR)
    EXPECTED = []
    actual = expr.evaluate(con)
    tester.compare(7, len(actual))
    tester.testDone()

    EXPR = '/*/*/namespace::node()'
    expr = Compile(EXPR)
    tester.startTest(EXPR)
    EXPECTED = []
    actual = expr.evaluate(con)
    tester.compare(6, len(actual))
    tester.testDone()

    EXPR = '/*/namespace::node()|/*/*/namespace::node()'
    expr = Compile(EXPR)
    tester.startTest(EXPR)
    EXPECTED = []
    actual = expr.evaluate(con)
    tester.compare(7, len(actual))
    tester.testDone()

    EXPR = '//*'
    expr = Compile(EXPR)
    #expr is <AbbreviatedAbsoluteLocationPath: /descendant-or-self::node()/child::*>
    tester.startTest(EXPR)
    EXPECTED = []
    actual = expr.evaluate(con)
    tester.compare(4, len(actual))
    tester.testDone()

    return tester.groupDone()

