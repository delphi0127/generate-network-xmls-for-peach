#http://sourceforge.net/tracker/index.php?func=detail&aid=679374&group_id=39954&atid=428292
from Xml.Xslt import test_harness

SHEET_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="foo">
    <res>
      <xsl:apply-templates select="@*"/>
    </res>
  </xsl:template>

  <xsl:template match="@bar[. = 'xxx']">
    <ok>
      <xsl:copy-of select="."/>
    </ok>
  </xsl:template>

</xsl:stylesheet>
"""


SOURCE_1 = """\
<?xml version="1.0" encoding="UTF-8"?>
<foo bar="xxx"/>
"""


EXPECTED = """<?xml version="1.0" encoding="UTF-8"?>
<res><ok bar="xxx"/></res>"""


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED,
                          title="""matches of the form <xsl:template match="@a[.='b']">""")
    return

