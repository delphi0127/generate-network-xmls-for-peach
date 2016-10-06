#Jeremy J. Sydik <Jeremy.Sydik@iuniverse.com> found a bug in the preceding-sibling axis

from Xml.Xslt import test_harness

source_1="""
<top>
    <prev val='1'/>
    <prev val='2'/>
    <prev val='3'/>
    <target/>
</top>
"""

sheet_1="""
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:template match='top'>
        <top><xsl:apply-templates/></top>
    </xsl:template>
    <xsl:template match='prev'>
        <prev val='{@val}'/>
    </xsl:template>
    <xsl:template match='target'>
        <output>
            <xsl:copy-of select='preceding-sibling::*[1]'/>
        </output>
    </xsl:template>
</xsl:stylesheet>
"""
    
expected_1="""<?xml version='1.0' encoding='UTF-8'?>
<top>
    <prev val='1'/>
    <prev val='2'/>
    <prev val='3'/>
    <output><prev val='3'/></output>
</top>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
    
