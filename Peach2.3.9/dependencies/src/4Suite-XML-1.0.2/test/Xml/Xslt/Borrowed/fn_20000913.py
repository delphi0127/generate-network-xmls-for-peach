#Francis Norton's <francis@redrice.com> saxon vs msxml bug query

from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="xml" indent="yes"/>

  <!-- take a wrapper with a header and an appStatus -->
  <xsl:template match="/">
    <header>
      <status><xsl:value-of select="//status"/></status>
      <!-- now the rest of the simple itemStatus elements -->
      <xsl:apply-templates select="*"/>
    </header>
  </xsl:template>

  <!-- kill the itemStatus/status since we've already output it -->
  <xsl:template match="status" />
  <xsl:template match="itemStatus/status" priority="1.0"/>

  <!-- and generate "attribute" elements with the rest... -->
  <xsl:template match="itemStatus/*">
    <attribute name="{name(.)}"><xsl:value-of
select="text()"/></attribute>
  </xsl:template>

</xsl:stylesheet>"""


source_1 = """<xw:wrapper
xmlns:xw='http://www.workspot.net/~roundand/xml/xwrapper.xsd'>
  <itemStatus>
    <status>REFER</status>
    <applicationId>CCUK000000000604</applicationId>
  </itemStatus>
</xw:wrapper>"""


expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<header>
  <status>REFER</status>
  
    
    <attribute name='applicationId'>CCUK000000000604</attribute>
  
</header>"""



def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
    
