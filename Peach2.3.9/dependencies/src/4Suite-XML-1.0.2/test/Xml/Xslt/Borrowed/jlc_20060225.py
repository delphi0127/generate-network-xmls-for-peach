# This is in response to bug 1438337
# (<https://sourceforge.net/tracker/index.php?func=detail&aid=1438337&group_id=39954&atid=428292>).
# We have some XPath test cases that provide coverage for the bug, but it's
# good to have an XSLT test case or two to deal with it as well.

from Xml.Xslt import test_harness

SRC_1 = """\
<doc><a b='1'/></doc>"""

SHEET_1 = """\
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="/doc">
    <output>
      <xsl:apply-templates
        select="a[@b = '1' and @b!=preceding-sibling::a/@b]"/>
    </output>
  </xsl:template>
  <xsl:template match="a">
    <got-one>!</got-one>
  </xsl:template>
</xsl:stylesheet>"""

EXPECTED_1 = """<?xml version="1.0" encoding="UTF-8"?>
<output/>"""

def Test(tester):
    source = test_harness.FileInfo(string=SRC_1)
    sheet = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sheet], EXPECTED_1,
        title='XPath comparison against empty node-set in an XSLT context')

    return
