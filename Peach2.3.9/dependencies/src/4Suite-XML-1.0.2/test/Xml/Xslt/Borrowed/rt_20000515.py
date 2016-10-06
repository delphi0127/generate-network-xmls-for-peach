#"Ron Ten-Hove" <rtenhove@forte.com>, by wondering why he doesn't get the expected result from passing params to unnamed templates, exposes a subtle gotcha.  15 May 2000

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">
    <xsl:output indent="yes"/>

    <xsl:template match="/">
        <root>
            <xsl:apply-templates>
                <xsl:with-param name="param">List</xsl:with-param>
            </xsl:apply-templates>
        </root>
    </xsl:template>

    <xsl:template match="chapter">
      <xsl:param name="param">Unset</xsl:param>
      <chap>
        <xsl:attribute name="title"><xsl:value-of
select="@name"/></xsl:attribute>
        <xsl:attribute name="cat"><xsl:value-of
select="$param"/></xsl:attribute>
      </chap>
    </xsl:template>

    <xsl:template match="text()" />
</xsl:stylesheet>"""


source_1 = """<?xml version="1.0"?>
<doc>
  <chapter name="The beginning">
    Alpha.
  </chapter>
</doc>
"""


expected_1="""<?xml version='1.0' encoding='UTF-8'?>
<root>
  <chap title='The beginning' cat='Unset'/>
</root>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
