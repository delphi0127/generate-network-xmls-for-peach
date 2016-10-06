#edmund mitchell <edmund_mitchell@hotmail.com> having trouble with call-template

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
version='1.0'>

<xsl:template name="pad">
    <xsl:param name="String"/>
    <xsl:param name="length"/>
    <xsl:variable name="spaces"
                  select="'                                      '"/>
    <xsl:value-of select="substring(concat($String,$spaces),1,$length)"/>
</xsl:template>

<xsl:variable name="stuff">
  <xsl:call-template name="pad">
    <xsl:with-param name="String" select="/outer/inner/deep/@att2"/>
    <xsl:with-param name="length" select="15"/>
  </xsl:call-template>
</xsl:variable>

<xsl:template match='/'>
        <xsl:value-of select="$stuff"/>
</xsl:template>

</xsl:stylesheet>
"""

source_1 = """<?xml version="1.0"?>
<outer>
        <inner>
                <deep att='value' att2='val2'>
                my goodness
                </deep>
        </inner>
</outer>"""

expected_1 = """<?xml version="1.0" encoding="UTF-8"?>\012val2           """


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
    
