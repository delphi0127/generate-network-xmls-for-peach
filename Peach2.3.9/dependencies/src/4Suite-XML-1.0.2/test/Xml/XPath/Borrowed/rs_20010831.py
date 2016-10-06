#! /usr/bin/env python

from Ft.Xml.XPath import Evaluate, NormalizeNode
from Ft.Xml.XPath.Conversions import StringValue
from Ft.Xml import InputSource

test = '''<foo>
    <bar>normal text</bar>
    <f>f1</f>
    Free range chickens
    <bar><![CDATA[<cdatatext>]]></bar>
    <f>f2</f>
</foo>
'''


def Test(tester):
    
    tester.startTest("CDATA Conversions")
    isrc = InputSource.DefaultFactory.fromString(test,'rs')
    dom = tester.test_data['parse'](isrc)
    NormalizeNode(dom)
    nodes = Evaluate('//bar/text()', contextNode = dom)
    tester.compare(2,len(nodes))
    tester.compare('normal text',StringValue(nodes[0]))
    tester.compare('<cdatatext>',StringValue(nodes[1]))
    tester.compare('<cdatatext>',Evaluate('string(//bar[2]/text())', contextNode = dom))
    tester.testDone()
