#Jeni Tennison <jeni.tennison@epistemics.co.uk>'s implementation of Oliver Becker's arbitrary sort/XPath conditionals trick.  Aug 8 2000.

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet
xmlns:xsl='http://www.w3.org/1999/XSL/Transform' version="1.0">

<xsl:output method="text"/>

<xsl:template match="items">
  <xsl:for-each select="item">
    <xsl:sort
      select="concat(
              substring(concat('Mac', substring-after(., 'Re Mc'), ', Re'),
                        1 div starts-with(., 'Re Mc')),
              substring(concat(substring-after(., 'Re '), ', Re'),
                        1 div (starts-with(., 'Re ') and
                        not(starts-with(., 'Re Mc')))),
              substring(concat('Mac', substring-after(., 'Mc')),
                        1 div (not(starts-with(., 'Re ')) and
                        starts-with(., 'Mc'))),
              substring(.,
                        1 div not(starts-with(.,'Mc') or
                        starts-with(., 'Re '))))" />
    <xsl:copy-of select="." />
  </xsl:for-each>
</xsl:template>

</xsl:stylesheet>"""

source_1 = """<items>
<item>MacBean</item>
<item>McBarlow</item>
<item>Re MacBart</item>
<item>Re McBeanie</item>
</items>"""

expected_1 = """McBarlowRe MacBartMacBeanRe McBeanie"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
    
