from Ft.Xml.Xslt import Processor
from Ft.Xml import Domlette, InputSource


expected = """<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <title>Address Book</title>
  </head>
  <body>
    <h1>Tabulate Just Names and Phone Numbers</h1>
    <table>
      <tr>
        <td align='center'><b>Pieter Aaron</b></td>
        <td>(Work) 404-555-1234<br>(Fax) 404-555-4321<br>(Pager) 404-555-5555</td>
      </tr>
      <tr>
        <td align='center'><b>Emeka Ndubuisi</b></td>
        <td>(Work) 767-555-7676<br>(Fax) 767-555-7642<br>(Pager) 800-SKY-PAGEx767676</td>
      </tr>
      <tr>
        <td align='center'><b>Vasia Zhugenev</b></td>
        <td>(Work) 000-987-6543<br>(Cell) 000-000-0000</td>
      </tr>
    </table>
  </body>
</html>
"""

from Ft.Lib import Uri
from Ft.Xml.Lib import TreeCompare

def Test(tester):
    tester.startGroup("instantiation of runNode")

    base = Uri.OsPathToUri(__file__, attemptAbsolute=True)
    src_uri = Uri.Absolutize('addr_book1.xml', base)
    sty_uri = Uri.Absolutize('addr_book1.xsl', base)

    tester.startTest("without whitespace preservation")
    p = Processor.Processor()
    node = Domlette.NonvalidatingReader.parseUri(src_uri)
    isrc = InputSource.DefaultFactory.fromUri(sty_uri)
    p.appendStylesheet(isrc)
    res = p.runNode(node, src_uri, ignorePis=True, preserveSrc=False)
    tester.compare(expected, res, func=TreeCompare.TreeCompare)
    tester.testDone()

    tester.startTest("with whitespace preservation")
    p = Processor.Processor()
    node = Domlette.NonvalidatingReader.parseUri(src_uri)
    isrc = InputSource.DefaultFactory.fromUri(sty_uri)
    p.appendStylesheet(isrc)
    res = p.runNode(node, src_uri, ignorePis=True, preserveSrc=True)
    tester.compare(expected, res, func=TreeCompare.TreeCompare)
    tester.testDone()

    tester.groupDone()
    return
