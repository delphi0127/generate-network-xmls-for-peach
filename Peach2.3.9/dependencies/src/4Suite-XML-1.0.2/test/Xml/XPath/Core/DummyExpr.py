from Ft.Lib import boolean, number
from Ft.Xml.Domlette import NonvalidatingReader, Document, Element
from Ft.Xml.XPath import ParsedExpr

class DummyBooleanExpr:
    def __init__(self,val):
        self.val = val and boolean.true or boolean.false

    def evaluate(self,context):
        return self.val

    def __repr__(self):
        return str(self.val)

class DummyNumberExpr:
    def __init__(self,val):
        self.val = val

    def evaluate(self,context):
        return self.val

    def __repr__(self):
        return str(self.val)

class DummyNodeSetExpr:
    def __init__(self, val=None):
        self.val = val

    def evaluate(self,context):
        return self.val

    def select(self,context):
        return self.val

    def __repr__(self):
        return '<%d-item nodeset>' % len(self.val)

class DummyStringExpr:
    def __init__(self, val=None):
        self.val = (val is None) and u'DummyString' or val

    def evaluate(self,context):
        return self.val

    def __repr__(self):
        return repr(self.val)


boolT = DummyBooleanExpr(1)
boolF = DummyBooleanExpr(0)

num0 = DummyNumberExpr(0)
num0p5 = DummyNumberExpr(0.5)
numN0p5 = DummyNumberExpr(-0.5)
num1 = DummyNumberExpr(1)
num1p5 = DummyNumberExpr(1.5)
num2 = DummyNumberExpr(2)
num2p6 = DummyNumberExpr(2.6)
num3 = DummyNumberExpr(3)
numN4 = DummyNumberExpr(-4)
num4p5 = DummyNumberExpr(4.5)
numN4p5 = DummyNumberExpr(-4.5)
numN42 = DummyNumberExpr(-42)
numNan = DummyNumberExpr(number.nan)
numInf = DummyNumberExpr(number.inf)
numNInf = DummyNumberExpr(-number.inf)

strEmpty = DummyStringExpr(u'')
str12345 = DummyStringExpr(u'12345')
strPi = DummyStringExpr(u'3.14')
strText = DummyStringExpr(u'Hi')
strPiText = DummyStringExpr(u'3.14Hi')
strSpace = DummyStringExpr(u'Ht    \t There\t   Mike')
strHelloWorld = DummyStringExpr(u'hello world')
STR_EGG1 = DummyStringExpr(u'egg1')
STR_EGG2 = DummyStringExpr(u'egg2')

DOC = "<spam><egg1>egg1</egg1><egg2>egg2</egg2></spam>"
doc = NonvalidatingReader.parseString(DOC, 'http://foo/test/spam.xml')
node1 = doc.documentElement.firstChild
node2 = node1.nextSibling

EMPTY_NODE_SET = DummyNodeSetExpr([])
ONE_NODE_SET = DummyNodeSetExpr([node1])
TWO_NODE_SET = DummyNodeSetExpr([node1, node2])

DOC2 = "<spam><egg0>0</egg0><egg1>1</egg1><egg0>0</egg0><egg1>1</egg1><egg0>0</egg0></spam>"
doc = NonvalidatingReader.parseString(DOC2, 'http://foo/test/spam.xml')
node1 = doc.documentElement.firstChild
node2 = node1.nextSibling
node3 = node2.nextSibling
node4 = node3.nextSibling
node5 = node4.nextSibling

ONE_NODE_SET_DOC2 = DummyNodeSetExpr([node1])
TWO_NODE_SET_DOC2 = DummyNodeSetExpr([node1, node2])
THREE_NODE_SET_DOC2 = DummyNodeSetExpr([node1, node2, node3])
FOUR_NODE_SET_DOC2 = DummyNodeSetExpr([node1, node2, node3, node4])
FIVE_NODE_SET_DOC2 = DummyNodeSetExpr([node1, node2, node3, node4, node5])


root = Element(Document(), None, 'root')
root.setAttributeNS(None, 'num0', '0')
root.setAttributeNS(None, 'num2', '2')
root.setAttributeNS(None, 'num4', '4')
nodesetNum0 = DummyNodeSetExpr([root.getAttributeNodeNS(None, 'num0')])
nodesetNum2 = DummyNodeSetExpr([root.getAttributeNodeNS(None, 'num2')])
nodesetNum4 = DummyNodeSetExpr([root.getAttributeNodeNS(None, 'num4')])
