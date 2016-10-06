#Edmund Mitchell <> finds brokenness in format-number

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
version="1.0">
 <xsl:template match="/doc">
   <xsl:value-of select="format-number(number, '#,###;(#)' )"/>
 </xsl:template>
</xsl:stylesheet>"""

source_1 = """<doc>
   <number>-12345</number>
</doc>"""

expected_1 = """<?xml version="1.0" encoding="UTF-8"?>
(12,345)"""
#"

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
    
