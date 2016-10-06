#See https://sourceforge.net/tracker/?func=detail&atid=106473&aid=418317&group_id=6473
import os
from Ft.Xml import Domlette
from Ft.Lib import Uri
from xml.dom import Node
from Ft.Xml import InputSource
from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Xml.XPath import Evaluate, Compile, Context


SRC_1 = """<?xml version="1.0" encoding="utf-8"?>
<doc>
<elem>abc</elem>
<elem><![CDATA[abc]]></elem>
<elem>a<![CDATA[b]]>c</elem>
</doc>"""


def Test(tester):
    tester.startGroup('CDATA sections in doc')
    
    isrc = InputSource.DefaultFactory.fromString(SRC_1,
                                                 Uri.OsPathToUri(os.getcwd()))
    doc = NonvalidatingReader.parse(isrc)
    con = Context.Context(doc, 1, 1)

    EXPR = '/doc/elem/text()'
    expr = Compile(EXPR)
    tester.startTest(EXPR)
    actual = [ node.data for node in expr.evaluate(con) ]
    tester.compare(actual, ["abc"]*3)
    tester.testDone()

    return tester.groupDone()

