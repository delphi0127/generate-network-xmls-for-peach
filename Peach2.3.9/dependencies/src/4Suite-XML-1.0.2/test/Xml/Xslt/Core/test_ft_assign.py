from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="text"/>
  
  <xsl:output method="text"/>
  <xsl:variable name="counter" select="1"/>
  <xsl:variable name="train" select="'a'"/>
  
  <xsl:template match="/">
    <xsl:value-of select="'before'"/>
    <xsl:value-of select="$counter"/>
    <xsl:value-of select="$train"/>
    <ft:assign name='counter' select="$counter+1"/>
    <ft:assign name='train'>
      <xsl:value-of select="$train"/>a<xsl:text/>
    </ft:assign>
    <xsl:value-of select="'after'"/>
    <xsl:value-of select="$counter"/>
    <xsl:value-of select="$train"/>
  </xsl:template>
  
</xsl:stylesheet>
"""

source_1 = "<dummy/>"


expected_1 = "before1aafter2aa"


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          title='basic ft:assign')
    return
