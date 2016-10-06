#Craeg K. Strong  cstrong@arielpartners.com's problem with exsl/func

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:arielpartners = "http://www.arielpartners.com/XSLT/Extensions"
  xmlns:func = "http://exslt.org/functions"
  extension-element-prefixes = "func"
  exclude-result-prefixes = "arielpartners"
  version="1.0"
>

  <xsl:output method="text"/>

  <func:function name="arielpartners:toUpperCase">
    <xsl:param name="stringToConvert"/>
    <func:result select="translate($stringToConvert,
                                   'abcdefghijklmnopqrstuvwxyz',
                                   'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
  </func:function>

  <xsl:template match="/">
    <xsl:value-of select="arielpartners:toUpperCase(.)"/>
  </xsl:template>

</xsl:stylesheet>
"""

source_1 = '<spam>eggs</spam>'

expected_1 = "EGGS"


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
