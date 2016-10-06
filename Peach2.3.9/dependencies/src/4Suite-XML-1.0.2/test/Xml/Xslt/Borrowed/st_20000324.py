#Steve Tinney's conformance test, 24 Mar 2000

import os
from Ft.Lib import Uri
from Xml.Xslt import test_harness

sheet_1 = """<?xml version='1.0'?>
<xsl:stylesheet version="1.0" 
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="text"/>

<xsl:variable name="textnode">Text node</xsl:variable>

<xsl:template match="/">
  <xsl:for-each select="document('')/*/xsl:variable">
    <xsl:text>child::text() = </xsl:text>
      <xsl:choose><xsl:when test="child::text()">true</xsl:when>
                  <xsl:otherwise>false</xsl:otherwise></xsl:choose>
    <xsl:text>&#xa;</xsl:text>
  </xsl:for-each>
  <xsl:for-each select="document('')/*/xsl:variable/text()">
    <xsl:text>self::text() = </xsl:text>
      <xsl:choose><xsl:when test="self::text()">true</xsl:when>
                  <xsl:otherwise>false</xsl:otherwise></xsl:choose>
    <xsl:text>&#xa;</xsl:text>
  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>"""


source_1="""<dummy/>"""


expected_1="""child::text() = true
self::text() = true
"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)

    #Test again with a specfied baseUri
    uri = Uri.OsPathToUri(os.path.abspath(__file__))
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1, baseUri=uri)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
