#CChad Pettit had probs with Xalan & exsl:func

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:func="http://exslt.org/functions"
  xmlns:my="http://www.xontech.com/functions"
  extension-element-prefixes ="func"
>

<xsl:output method="text"/>

<func:function name="my:check">
    <func:result select="3" />
</func:function>

<xsl:template match="/">
    <xsl:variable name="foo">
        <xsl:value-of select="my:check()"/>
    </xsl:variable>
   
    <xsl:value-of select="$foo"/>
</xsl:template>

</xsl:stylesheet>
"""

source_1 = '<dummy/>'

expected_1 = "3"


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='output func result')
    return
