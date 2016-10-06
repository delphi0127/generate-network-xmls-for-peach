#http://sourceforge.net/tracker/index.php?func=detail&aid=679360&group_id=39954&atid=428292
from Xml.Xslt import test_harness

SHEET_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="xpath">
    <xpath>
      <xsl:copy-of select="namespace::* "/>
      <xsl:value-of select="@expr"/>
    </xpath>
  </xsl:template>

</xsl:stylesheet>
"""


SOURCE_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<xpath
xmlns:foo="http://examplotron.com/namespaces/example"
expr="/foo:bar"/>
"""


EXPECTED = """<?xml version="1.0" encoding="UTF-8"?>
<xpath xmlns:foo="http://examplotron.com/namespaces/example">/foo:bar</xpath>"""


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED,
                          title='<xsl:copy-of select="namespace::*"/> should copy the namespace')
    return

