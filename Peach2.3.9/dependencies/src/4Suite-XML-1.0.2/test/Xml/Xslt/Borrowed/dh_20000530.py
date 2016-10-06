#XT Bug Report from David Hunter <david.hunter@mobileQ.COM> on 30 May 2000, with additional checks

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text"/>

<xsl:template match="/nodes/node[last()]">
  <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="text()"/>
</xsl:stylesheet>"""


sheet_2 = """<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text"/>

<xsl:template match="/nodes/node[1]">
  <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="/nodes/node[2]">
  <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="/nodes/node[3]">
  <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="text()"/>
</xsl:stylesheet>"""


sheet_3 = """<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text"/>

<xsl:template match="/nodes/node[last()]">
  <xsl:value-of select="."/>
</xsl:template>

<xsl:template match="text()"/>

<xsl:template match="/nodes/*" priority="-10">
<xsl:text>Hello</xsl:text>
</xsl:template>

</xsl:stylesheet>"""


source_1="""<nodes>
  <node>a</node>
  <node>b</node>
  <node>c</node>
</nodes>"""


expected_1="""c"""


expected_2="""abc"""


expected_3="""HelloHelloc"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
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
    
