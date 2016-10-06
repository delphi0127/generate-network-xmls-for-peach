from Xml.Xslt import test_harness

SHEET_1 = """<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:f="http://xmlns.4suite.org/ext"
  extension-element-prefixes="f"
  version="1.0"
  >

  <xsl:output method="text"/>

  <xsl:template match="/">
    <xsl:variable name='bytes-fo' select="'abc&#xe9;fg'"/>
    <!--
    <xsl:variable name='orig' select="'abc&#xe9;fg'"/>
    <xsl:variable name='bytes-fo' select="f:encode($orig, 'utf-8')"/>
    <xsl:variable name='unicode-fo' select="f:decode($bytes-fo, 'utf-8')"/>
    -->
    <f:raw-text-output select='$bytes-fo'/>
  </xsl:template>
  
</xsl:stylesheet>
"""

SOURCE_1 = "<dummy/>"

EXPECTED_1 = "abc\xc3\xa9fg"


def Test(tester):
    source = test_harness.FileInfo(string=SOURCE_1)
    sty = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_1,
                          title="f:decode, f:encode and f:raw-text-output")

