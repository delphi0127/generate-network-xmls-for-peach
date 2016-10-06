#Example from Pawson, David <DPawson@rnib.org.uk> to Leigh Dodds on 6 March 2000

from Xml.Xslt import test_harness

sheet_1 = """<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:output method="html" indent="yes"/>

  <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="TASKS/TASK/COMPONENTS">
    <xsl:variable name="t-size" select="count(COMPONENT)"/>
    <xsl:variable name="half" select="ceiling($t-size div 2)"/>
   
    <TABLE>
      <xsl:for-each select="COMPONENT[position() &lt;= $half]">
      <xsl:variable name="here" select="position()"/>
      <TR>
        <TD><xsl:value-of select="."/></TD>
        <TD>
          <xsl:choose>
            <xsl:when test="../COMPONENT[$here+$half]">
              <xsl:value-of select="../COMPONENT[$here+$half]"/>
            </xsl:when>
            <xsl:otherwise></xsl:otherwise>
          </xsl:choose>
        </TD>
      </TR>
      </xsl:for-each>
    </TABLE>

  </xsl:template>

</xsl:stylesheet>"""


source_1="""<?xml version='1.0'?>
<TASKS>
  <TASK>
    <COMPONENTS>
      <COMPONENT>A</COMPONENT>
      <COMPONENT>B</COMPONENT>
      <COMPONENT>C</COMPONENT>
      <COMPONENT>D</COMPONENT>
      <COMPONENT>E</COMPONENT>
      <COMPONENT>F</COMPONENT>
      <COMPONENT>G</COMPONENT>
      <COMPONENT>H</COMPONENT>
      <COMPONENT>I</COMPONENT>
      <COMPONENT>J</COMPONENT>
      <COMPONENT>K</COMPONENT>
    </COMPONENTS>
  </TASK>
</TASKS>
"""


expected_1 = """
  
    <TABLE>
  <TR>
    <TD>A</TD>
    <TD>G</TD>
  </TR>
  <TR>
    <TD>B</TD>
    <TD>H</TD>
  </TR>
  <TR>
    <TD>C</TD>
    <TD>I</TD>
  </TR>
  <TR>
    <TD>D</TD>
    <TD>J</TD>
  </TR>
  <TR>
    <TD>E</TD>
    <TD>K</TD>
  </TR>
  <TR>
    <TD>F</TD>
    <TD></TD>
  </TR>
</TABLE>"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1)
    return
    
