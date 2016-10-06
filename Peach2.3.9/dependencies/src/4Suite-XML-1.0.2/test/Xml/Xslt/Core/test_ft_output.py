from Xml.Xslt import test_harness

sheet_1 = """\
<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ft="http://xmlns.4suite.org/ext"
  extension-element-prefixes="ft"
  version="1.0"
  >

  <xsl:output method="xml" omit-xml-declaration="yes"/>
  
  <xsl:template match="/">
    <xsl:text><![CDATA[<br/>]]></xsl:text>
    <ft:output method="text">
      <xsl:text><![CDATA[<br/>]]></xsl:text>
    </ft:output>
    <ft:output method="html">
      <xsl:text><![CDATA[<br/>]]></xsl:text>
    </ft:output>
  </xsl:template>
  
</xsl:stylesheet>
"""

source_1 = "<dummy/>"


expected_1 = "&lt;br/&gt;<br/>&lt;br/&gt;"


def Test(tester):

    source = test_harness.FileInfo(string=source_1)
    sty = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sty], expected_1,
                          title='ft:output')
    return
