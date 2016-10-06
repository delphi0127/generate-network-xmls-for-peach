#andreg@attglobal.net thought he had a problem with position() on Xalan
from Xml.Xslt import test_harness

stylesheet = """<?xml version='1.0'?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
  <xsl:output method="html" indent="yes"/>

<xsl:strip-space elements="*"/>

<xsl:template match="* | @*">
<xsl:copy><xsl:copy-of select="@*"/><xsl:apply-templates/></xsl:copy>
</xsl:template>

<!-- process table -->

<!-- handle the rows -->
<xsl:template match="row">
  <xsl:call-template name="processRow">
         <xsl:with-param name="numItems"><xsl:value-of
select="count(//item)"/></xsl:with-param>
         <xsl:with-param name="n">1</xsl:with-param>
  </xsl:call-template>
</xsl:template>

<!-- handle all rows recursively for as many times as we have items -->
<xsl:template name="processRow">
  <xsl:param name="numItems"/>
  <xsl:param name="n"/>

  <!-- first check if the loop ended -->
  <xsl:if test="$numItems >= $n">
       <xsl:copy>

       <!-- handle all cells -->
       <xsl:for-each select="cell">
          <!-- copy the content of the cell, including attributes -->
          <xsl:copy><xsl:copy-of select="@*"/>
            <!-- find the elements that have an id attribute -->
            <xsl:for-each select="./*[@id]">
              <!-- need to assign a variable to the attribute value,
otherwise it will not work at all -->
              <xsl:variable name="elname"><xsl:value-of
select="./@id"/></xsl:variable>
              <xsl:copy><xsl:copy-of select="@*"/>
                 <!-- insert the value of the cell -->
                 <!-- this is the statement that causes trouble!! -->
                 <xsl:value-of select="//*[(name() = $elname) and
(parent::node()[position() = $n])]"/>
              </xsl:copy>
            </xsl:for-each>
          </xsl:copy>
       </xsl:for-each>
       </xsl:copy>

       <!-- now make the recursive call, increase n by 1 -->
       <xsl:call-template name="processRow">
         <xsl:with-param name="n">
            <xsl:value-of select="$n + 1"/>
         </xsl:with-param>
         <xsl:with-param name="numItems">
            <xsl:value-of select="$numItems"/>
         </xsl:with-param>
       </xsl:call-template>

  </xsl:if>
</xsl:template>

<xsl:template match="doc">
<xsl:apply-templates/>
</xsl:template>

<xsl:template match="items"/>

</xsl:stylesheet>
"""

xml_source = """<?xml version="1.0"?>
<doc>
<table>
        <row>
                <cell><input id="entry1"/></cell>
                <cell><input id="entry2"/></cell>
                <cell><input id="entry3"/></cell>
        </row>
</table>

<items>
        <item>
                <entry1>Entry 1 Value 1</entry1>
                <entry2>Entry 2 Value 1</entry2>
                <entry3>Entry 3 Value 1</entry3>
        </item>
        <item>
                <entry1>Entry 1 Value 2</entry1>
                <entry2>Entry 2 Value 2</entry2>
                <entry3>Entry 3 Value 2</entry3>
        </item>
</items>
</doc>"""


expected = """<table>
  <row>
    <cell><input id="entry1">Entry 1 Value 1</cell>
    <cell><input id="entry2">Entry 2 Value 1</cell>
    <cell><input id="entry3">Entry 3 Value 1</cell>
  </row>
  <row>
    <cell><input id="entry1"></cell>
    <cell><input id="entry2"></cell>
    <cell><input id="entry3"></cell>
  </row>
</table>"""


def Test(tester):
    source = test_harness.FileInfo(string=xml_source)
    sheet = test_harness.FileInfo(string=stylesheet)
    test_harness.XsltTest(tester, source, [sheet], expected,
                          title='position() bug')
    return
