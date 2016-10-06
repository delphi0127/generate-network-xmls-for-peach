#Jeni Tennison <Jeni.Tennison@epistemics.co.uk> taunts her cross-pond mates about politics and the self axis

from Xml.Xslt import test_harness

sheet_1 = """\
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dem="http://www.democrat.org/"
  xmlns:rep="http://www.republican.org/">

<xsl:template match="vote">
   <xsl:copy>
      <dem:count><xsl:value-of select="rep:count - 432" /></dem:count>
      <xsl:copy-of select="*[not(self::dem:count)]" />
   </xsl:copy>
</xsl:template>

</xsl:stylesheet>"""

source_1 = """<vote xmlns:d="http://www.democrat.org/"
      xmlns:r="http://www.republican.org/">
   <county>Palm Beach</county>
   <d:count>31563</d:count>
   <r:count>23725</r:count>
</vote>"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>\n<vote xmlns:d='http://www.democrat.org/' xmlns:r='http://www.republican.org/'><dem:count xmlns:dem='http://www.democrat.org/' xmlns:rep='http://www.republican.org/'>23293</dem:count><county>Palm Beach</county><r:count>23725</r:count></vote>"""

#This version forgets that the principal node type of the self axis is element
sheet_2 = """<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dem="http://www.democrat.org/"
                xmlns:rep="http://www.republican.org/">

<xsl:template match="vote">
   <xsl:copy>
      <xsl:attribute name="dem:count" namespace="http://www.democrat.org/">
        <xsl:value-of select="@rep:count - 432" />
      </xsl:attribute>
      <xsl:copy-of select="@*[not(self::dem:count)]" />
   </xsl:copy>
</xsl:template>

</xsl:stylesheet>"""

source_2 = """<vote xmlns:d="http://www.democrat.org/"
      xmlns:r="http://www.republican.org/"
      county="Palm Beach"
      d:count="31563"
      r:count="23725"/>"""

expected_2 = """<?xml version='1.0' encoding='UTF-8'?>
<vote r:count='23725' county='Palm Beach' d:count='23293' xmlns:d='http://www.democrat.org/' xmlns:r='http://www.republican.org/'/>"""

# The nastiness Jeni resorts to as a general solution to this
sheet_3 = """<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:dem="http://www.democrat.org/"
                xmlns:rep="http://www.republican.org/">

<xsl:template match="vote">
   <xsl:copy>
      <xsl:attribute name="dem:count" namespace="http://www.democrat.org/">
        <xsl:value-of select="@rep:count - 432" />
      </xsl:attribute>
      <xsl:copy-of select="@*[not(local-name() = 'count' and namespace-uri() = document('')/*/namespace::dem)]" />
   </xsl:copy>
</xsl:template>

</xsl:stylesheet>"""

expected_3 = """<?xml version='1.0' encoding='UTF-8'?>
<vote r:count='23725' county='Palm Beach' d:count='23293' xmlns:d='http://www.democrat.org/' xmlns:r='http://www.republican.org/'/>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')

    source = test_harness.FileInfo(string=source_2)
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 3')
    return
    
