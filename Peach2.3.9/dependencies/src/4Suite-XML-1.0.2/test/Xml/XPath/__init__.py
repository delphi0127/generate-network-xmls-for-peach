__revision__ = '$Id: __init__.py,v 1.19 2005/10/09 01:04:46 mbrown Exp $'

def PreprocessFiles(dirs, files):
    """
    PreprocessFiles(dirs, files) -> (dirs, files)

    This function is responsible for sorting and trimming the
    file and directory lists as needed for proper testing.
    """
    from Ft.Lib.TestSuite import RemoveTests, SortTests

    ignored_files = []
    RemoveTests(files, ignored_files)

    ordered_files = []
    SortTests(files, ordered_files)

    ignored_dirs = []
    RemoveTests(dirs, ignored_dirs)

    ordered_dirs = ['Core', 'Borrowed']
    SortTests(dirs, ordered_dirs)

    return (dirs, files)

# -- run modes -------------------------------------------------------

class _DomTree:
    def __init__(self, dom):
        from xml.dom import Node
        self.DOM = dom
        self.PI = dom.firstChild
        self.ROOT = dom.documentElement
        comment = self.ROOT.firstChild
        while comment and comment.nodeType != Node.COMMENT_NODE:
            comment = comment.nextSibling
        self.COMMENT = comment
        self.CHILDREN = filter(lambda node, type=Node.ELEMENT_NODE:
                               node.nodeType == type,
                               self.ROOT.childNodes)

        self.CHILD1 = self.CHILDREN[0]
        self.ATTR1 = self.CHILD1.getAttributeNodeNS(None, 'attr1')
        self.ATTR31 = self.CHILD1.getAttributeNodeNS(None, 'attr31')
        self.GCHILDREN1 = filter(lambda node, type=Node.ELEMENT_NODE:
                                 node.nodeType == type,
                                 self.CHILD1.childNodes)
        self.GCHILD11 = self.GCHILDREN1[0]
        self.GCHILD12 = self.GCHILDREN1[1]
        self.TEXT1 = self.CHILD1.lastChild

        self.CHILD2 = self.CHILDREN[1]
        self.ATTR2 = self.CHILD2.getAttributeNodeNS(None, 'attr1')
        self.IDATTR2 = self.CHILD2.getAttributeNodeNS(None, 'CODE')
        self.GCHILDREN2 = filter(lambda node, type=Node.ELEMENT_NODE:
                                 node.nodeType == type,
                                 self.CHILD2.childNodes)
        self.GCHILD21 = self.GCHILDREN2[0]
        self.GCHILD22 = self.GCHILDREN2[1]

        self.CHILD3 = self.CHILDREN[2]
        self.ATTR3 = self.CHILD3.getAttributeNodeNS('http://foo.com', 'name')

        self.PI2 = dom.lastChild

        self.LANG = self.CHILDREN[3]
        self.NONASCIIQNAME = filter(lambda node, type=Node.ELEMENT_NODE:
                                    node.nodeType == type,
                                    self.LANG.childNodes)[-1]
        self.LCHILDREN = filter(lambda node, type=Node.ELEMENT_NODE:
                                node.nodeType == type,
                                self.LANG.childNodes)
        self.LCHILD1 = self.LCHILDREN[0]
        self.LCHILD2 = self.LCHILDREN[1]

from Ft.Xml import cDomlette, InputSource

xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE ROOT [
  <!ELEMENT CHILD2 (#PCDATA|GCHILD)*>
  <!ATTLIST CHILD2 attr1 CDATA #IMPLIED
                   CODE ID #REQUIRED>
]>
<?xml-stylesheet "Data" ?>
<ROOT>
  <!-- Test Comment -->
  <CHILD1 attr1="val1" attr31="31">
    <GCHILD name="GCHILD11"/>
    <GCHILD name="GCHILD12"/>
    Text1
  </CHILD1>
  <CHILD2 attr1="val2" CODE="1">
    <GCHILD name="GCHILD21"/>
    <GCHILD name="GCHILD22"/>
  </CHILD2>
  <foo:CHILD3 xmlns:foo="http://foo.com" foo:name="mike"/>
  <lang xml:lang="en">
    <foo xml:lang=""/>
    <foo/>
    <f\xf6\xf8/>
  </lang>
</ROOT>
<?no-data ?>
"""

from Ft.Lib.TestSuite import TestMode

class _XPathMode(TestMode.TestMode):

    def _init(self, tester):
        return 1

    def _pre(self,tester):
        tester.test_data['tree'] = _DomMapping[self.name][0]
        tester.test_data['parse'] = _DomMapping[self.name][1]

_DomMapping = {}
isrc = InputSource.DefaultFactory.fromString(xml, 'urn:cDomlette-test-tree')
_DomMapping['cDomlette'] = (_DomTree(cDomlette.NonvalParse(isrc)),
                            cDomlette.NonvalParse)

MODES = [_XPathMode('cDomlette', default=1)]
