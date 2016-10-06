#Example for Jon Smirl on 28 Dec 1999, originally by Steve Muench, with improvements by Mike Brown and Jeremy Richman

from Xml.Xslt import test_harness

sheet_1 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

<xsl:template match="/">
<html>
  <head/>
  <body>
  <xsl:apply-templates/>
  </body>
</html>
</xsl:template>

<xsl:template match="p">
<p><xsl:apply-templates/></p>
</xsl:template>

<xsl:template match="programlisting">
  <span style="font-family:monospace">
  <xsl:call-template name="br-replace">
    <xsl:with-param name="word" select="."/>
  </xsl:call-template>
  </span>
</xsl:template>

<xsl:template name="br-replace">
  <xsl:param name="word"/>
   <!-- </xsl:text> on next line on purpose to get newline -->
  <xsl:variable name="cr"><xsl:text>
</xsl:text></xsl:variable>
  <xsl:choose>
  <xsl:when test="contains($word,$cr)">
      <xsl:value-of select="substring-before($word,$cr)"/>
      <br/>
      <xsl:call-template name="br-replace">
        <xsl:with-param name="word" select="substring-after($word,$cr)"/>
      </xsl:call-template>
  </xsl:when>
  <xsl:otherwise>
    <xsl:value-of select="$word"/>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

</xsl:stylesheet>"""


sheet_2 = """<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">

<xsl:template match="/">
<html>
  <head/>
  <body>
  <xsl:apply-templates/>
  </body>
</html>
</xsl:template>

<xsl:template match="p">
<p><xsl:apply-templates/></p>
</xsl:template>

<xsl:template match="programlisting">
  <span style="font-family:monospace">
  <xsl:apply-templates/>
  </span>
</xsl:template>

<xsl:template match="programlisting/text()[contains(.,'&#xA;')]">
  <xsl:call-template name="br-replace">
    <xsl:with-param name="text" select="."/>
  </xsl:call-template>
</xsl:template>

<xsl:template name="br-replace">
  <xsl:param name="text"/>
  <!-- </xsl:text> on next line on purpose to get newline -->
  <xsl:choose>
  <xsl:when test="contains($text, '&#xA;')">
    <xsl:value-of select="substring-before($text, '&#xA;')"/>
    <br/>
    <xsl:call-template name="br-replace">
      <xsl:with-param name="text" select="substring-after($text, '&#xA;')"/>
    </xsl:call-template>
  </xsl:when>
  <xsl:otherwise>
    <xsl:value-of select="$text"/>
  </xsl:otherwise>
 </xsl:choose>
</xsl:template>

</xsl:stylesheet>"""


source_1="""<doc>
  <p>This is some text.</p>
  <programlisting><![CDATA[This is a paragraph
  with some newlines
  does it work?]]></programlisting>
</doc>"""


expected_1 = """<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
  </head>
  <body>
    <p>This is some text.</p>
    <span style='font-family:monospace'>This is a paragraph<br>  with some newlines<br>  does it work?</span>
  </body>
</html>"""

def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')

    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 2')
    return
