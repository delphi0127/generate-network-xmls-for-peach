#Dan (hitt@charybdis.zembu.com) reports non-conformance with XSLT w.r.t. variable shadowing

from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0"?> 

<!-- 
     Thu Mar  8 03:17:39 PST 2001

     This attempts to count the children of the root by
     visiting each one and incrementing a counter.
-->

<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>
  <xsl:output omit-xml-declaration="yes"/>
  <xsl:strip-space elements="*"/>

  <xsl:variable name="node_count" select="0"/>

  <xsl:template match="/">
      <xsl:apply-templates/>
    node_count has value <xsl:copy-of select="$node_count"/>
  </xsl:template>

  <xsl:template match="*">
     <xsl:variable name="node_count" select="1+$node_count"/>
  </xsl:template>
  
</xsl:stylesheet>
"""

source_1 = "<a><b/><c/><d/></a>"

expected_1 = """
    node_count has value 0"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
