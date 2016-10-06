# http://mail.python.org/pipermail/xml-sig/2003-February/009070.html
# SF#695819

def Test(tester):

    from Ft.Xml import InputSource
    from Ft.Xml import XPath
    
    SRC = """<?xml version='1.0'?>
<alpha>
  <beta no="a">
    <gamma>
      <delta>1</delta>
    </gamma>
    <delta mark="foo">2</delta>
    <gamma mark="bar">
      <delta>3</delta>
    </gamma>
  </beta>
  <beta no="b">
    <delta>4</delta>
    <gamma>
      <delta>5</delta>
    </gamma>
  </beta>
</alpha>"""

    isrc = InputSource.DefaultFactory.fromString(SRC, __file__)
    doc = tester.test_data['parse'](isrc)

    expr = '/alpha/beta[attribute::no = "a"]'
    tester.startTest(expr)
    nodeset = XPath.Evaluate(expr, contextNode=doc)
    tester.compare(1, len(nodeset))
    tester.testDone()

    expr = '/alpha/beta[attribute::no = 1]'
    tester.startTest(expr)
    nodeset = XPath.Evaluate(expr, contextNode=doc)
    tester.compare(0, len(nodeset))
    tester.testDone()

    expr = '/alpha/beta[@no = "a"]'
    tester.startTest(expr)
    nodeset = XPath.Evaluate(expr, contextNode=doc)
    tester.compare(1, len(nodeset))
    tester.testDone()

    expr = '/alpha/beta[@no = 1]'
    tester.startTest(expr)
    nodeset = XPath.Evaluate(expr, contextNode=doc)
    tester.compare(0, len(nodeset))
    tester.testDone()

    return
