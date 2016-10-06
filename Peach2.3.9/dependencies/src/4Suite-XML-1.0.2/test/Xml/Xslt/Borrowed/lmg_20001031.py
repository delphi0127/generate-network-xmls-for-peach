#Lars Marius Garshol <larsga@garshol.priv.no> reports bugs

from Ft.Xml.Xslt import XsltException, Error
from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:foo="http://foo.org/xslt/extensions"
                extension-element-prefixes="foo"
                version="1.0">

  <xsl:template match = "/">
    <foo:bar really-useful-attribute = "bing">
      [...proceed to use the foo:bar instruction for something
    useful...]

      <xsl:fallback>
        <xsl:message terminate="yes">
        Sorry, support for the foo:bar element required to run this
        stylesheet. Try using the XSLT processor from foo.org instead!
        </xsl:message>
      </xsl:fallback>
    </foo:bar>
  </xsl:template>

</xsl:stylesheet>"""


sheet_2 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:foo="http://foo.org/xslt/extensions"
                extension-element-prefixes="foo"
                version="1.0">

<xsl:output indent="yes"
    doctype-system="http://www.python.org/topics/xml/dtds/xbel-1.0.dtd"
    doctype-public="+//IDN python.org//DTD XML Bookmark Exchange
    Language 1.0//EN//XML" />

  <xsl:template match = "/">
    <spam/>
  </xsl:template>

</xsl:stylesheet>"""


sheet_3 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">

  <xsl:template match = "/">
    <spam>
    <xsl:processing-instruction name="xsl-stylesheet">
      bing.xslt
    </xsl:processing-instruction>
    </spam>
  </xsl:template>

</xsl:stylesheet>"""

source_1 = "<xbel/>"


expected_1 = """"""


expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE spam PUBLIC "+//IDN python.org//DTD XML Bookmark Exchange     Language 1.0//EN//XML" "http://www.python.org/topics/xml/dtds/xbel-1.0.dtd">
<spam/>"""


expected_3 = """<?xml version='1.0' encoding='UTF-8'?>\012<spam><?xsl-stylesheet bing.xslt?></spam>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          exceptionCode=Error.STYLESHEET_REQUESTED_TERMINATION,
                          title='test 1')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 3')
    return
