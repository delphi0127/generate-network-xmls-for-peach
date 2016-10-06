#Mike Brown on 4Suite ML
from Xml.Xslt import test_harness

sheet_1 = """<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/">
    <result>
      <xsl:apply-templates/>
      <xsl:apply-templates mode="m"/>
    </result>
  </xsl:template>

  <xsl:template match="foo[@bar]" mode="m">
    <bar>matched foo[@bar] (mode m)</bar>
  </xsl:template>

  <xsl:template match="foo[@baz]" mode="m">
    <baz>matched foo[@baz] (mode m)</baz>
  </xsl:template>    

  <xsl:template match="foo[@bar]">
    <bar>matched foo[@bar]</bar>
  </xsl:template>

  <xsl:template match="foo[@baz]">
    <baz>matched foo[@baz]</baz>
  </xsl:template>    

</xsl:stylesheet>
"""
        
source_1 = """<?xml version="1.0" encoding="utf-8"?>
<stuff><foo bar="1"/><foo baz="1"/><foo bar="2"/><foo bar="3"/><foo baz="2"/></stuff>
"""

expected_1 = """<?xml version='1.0' encoding='UTF-8'?>
<result>
  <bar>matched foo[@bar]</bar>
  <baz>matched foo[@baz]</baz>
  <bar>matched foo[@bar]</bar>
  <bar>matched foo[@bar]</bar>
  <baz>matched foo[@baz]</baz>
  <bar>matched foo[@bar] (mode m)</bar>
  <baz>matched foo[@baz] (mode m)</baz>
  <bar>matched foo[@bar] (mode m)</bar>
  <bar>matched foo[@bar] (mode m)</bar>
  <baz>matched foo[@baz] (mode m)</baz>
</result>
"""


def Test(tester):
    source = test_harness.FileInfo(string=source_1)
    sheet = test_harness.FileInfo(string=sheet_1)
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='Multiple templates with modes')
    return

