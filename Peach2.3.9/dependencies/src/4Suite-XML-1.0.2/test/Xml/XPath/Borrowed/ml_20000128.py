#Markus Lauer's message:
"""
does XPath work with html Documents? In the below code in the result of
 the XPath evaluation the <H1>...</H1> node is missing.

Do I use XPath in a wrong way? Is it a bug? Is XPath not supposed
to work with HTML files?

I tried this with 4Dom-0.9.2, XPath-0.8.2 and 4Suite-base-0.7.1
Python 1.5.2 under SuSE Linux 6.3

(by the way: the hole 4Suite compiled without any problems out of the box)
"""

from Ft.Xml.Domlette import Print
import Ft.Xml.XPath
from Ft.Xml.XPath import Evaluate, Context
import sys, cStringIO

html="""
<HTML>
<HEAD><TITLE>foo</TITLE>
<TITLE>foo</TITLE>
</HEAD>
<BODY>
<H1>foo</H1>
</BODY>
</HTML>
"""

expected_1 = """<HEAD><TITLE>foo</TITLE>
<TITLE>foo</TITLE>
</HEAD>"""

#"

try:
    from xml.dom.ext.reader import HtmlLib
except ImportError:
    HtmlLib = None

def Test(tester):

    tester.startTest("Evaluate on a HTML Document")

    if HtmlLib is None:
        tester.warning("Requires PyXML to be installed")
        tester.testDone()
        return

    xml_dom = HtmlLib.FromHtml(html)

    p = Ft.Xml.XPath.parser.new()
    exp = p.parse("/HTML/HEAD")

    c=Context.Context(xml_dom,0,0)
    result=exp.evaluate(c)

    
    st = cStringIO.StringIO()
    Print(result[0],st)
    tester.compare(expected_1,st.getvalue())

    tester.testDone()

if __name__ == '__main__':
    test()

