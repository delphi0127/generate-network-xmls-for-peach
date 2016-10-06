#http://lists.fourthought.com/pipermail/4suite/2002-December/004771.html
from Ft.Xml import InputSource
from Ft.Xml.XPath import Evaluate, NormalizeNode
from Ft.Xml.XPath.Conversions import StringValue

DOC1 = """
<a>
<b>
<c/>
<d/>
</b>
</a>
"""


def Test(tester):    
    tester.startTest("descendant-or-self document order")
    isrc = InputSource.DefaultFactory.fromString(DOC1, 'sr_20021217')
    dom = tester.test_data['parse'](isrc)
    #NormalizeNode(dom)

    node_list = Evaluate('.//*', dom.documentElement)
    node_names = [ str(node.nodeName) for node in node_list ]

    tester.compare(3, len(node_names))
    #Must contain all nodes, but not necessarily in any order
    node_name_set = {}
    for n in node_names: node_name_set[n] = None
    tester.compare({'b': None, 'c': None, 'd': None}, node_name_set)

    node_list = Evaluate('(.//*)[1]', dom.documentElement)
    node_names = [ str(node.nodeName) for node in node_list ]

    tester.compare(1, len(node_names))
    tester.compare(['b'], node_names)

    tester.testDone()

