#Olivier Cayrol reports output bug

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet version='1.0'
                xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>

  <xsl:template match='condition'>
    <xsl:element name='template'>
      <xsl:attribute name='match'>
        <xsl:value-of select='.'/>
      </xsl:attribute>
      <xsl:text>This is a good one</xsl:text>
    </xsl:element>
  </xsl:template>
</xsl:stylesheet>
"""

source_1 = "<condition>car[@price &lt; 1000]</condition>"

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<template match='car[@price &lt; 1000]'>This is a good one</template>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
