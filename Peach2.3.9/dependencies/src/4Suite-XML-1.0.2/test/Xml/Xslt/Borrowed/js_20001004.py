#Jeremy J. Sydik <Jeremy.Sydik@iuniverse.com> is having trouble with pattern matches

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
    <xsl:template match='p[@class="normal"]'>
       <p><xsl:apply-templates/></p>
    </xsl:template>
    <xsl:template match='p[@class="indent"]'>
       <blockquote><p><xsl:apply-templates/></p></blockquote>
    </xsl:template>
    <xsl:template match="*|@*" priority="-1">
        <xsl:copy>
            <xsl:apply-templates select="@*|*|text()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>"""


source_1 = """<?xml version="1.0" ?>
<top>
  <p class="normal">spam</p>
  <p class="indent">eggs</p>
  <p class="naught">lumberjack</p>
  <p>ok</p>
</top>"""


expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<top>
  <p>spam</p>
  <blockquote><p>eggs</p></blockquote>
  <p class='naught'>lumberjack</p>
  <p>ok</p>
</top>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
    
